import asyncio
import html
import json
import os
import re
import logging
import httpx
from typing import Optional, Any, List

from google import genai

# Relative imports for the new structure
try:
    from env_setup import GEMINI_API_KEY, logger
    from prompts import SYSTEM_PROMPT, OUTPUT_SCHEMA, CORRELATION_PROMPT, CORRELATION_SCHEMA, TICKET_GENERATION_PROMPT, TICKET_GENERATION_SCHEMA
except ImportError:
    # Fallback for different execution contexts
    from .env_setup import GEMINI_API_KEY, logger
    from .prompts import SYSTEM_PROMPT, OUTPUT_SCHEMA, CORRELATION_PROMPT, CORRELATION_SCHEMA, TICKET_GENERATION_PROMPT, TICKET_GENERATION_SCHEMA

# -------------------------
# Gemini client setup
# -------------------------
if not GEMINI_API_KEY:
    logger.error("Metra Classifier: MISSING API KEY. Gemini will NOT work.")
    client = None
else:
    logger.info(f"Metra Classifier: Configuring Gemini with key starting with {GEMINI_API_KEY[:8]}")
    client = genai.Client(api_key=GEMINI_API_KEY)

# Global cache for MITRE data
_cached_mitre_data = None

# -------------------------
# Utilities
# -------------------------
def get_mitre_data(path: str = "data/mitre_attack.json") -> Optional[Any]:
    global _cached_mitre_data
    if _cached_mitre_data is not None:
        return _cached_mitre_data
    
    # Try multiple possible locations for the MITRE data file
    # Prefer the root data directory
    possible_paths = [
        os.path.join(os.getcwd(), "data", "mitre_attack.json"),  # From project root
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "mitre_attack.json"),  # From mitre_classifier
        os.path.join(os.path.dirname(__file__), "..", "data", "mitre_attack.json"),  # Local to agents
        path,  # Original path parameter
    ]
    
    for p in possible_paths:
        if os.path.exists(p):
            try:
                with open(p, "r") as f:
                    _cached_mitre_data = json.load(f)
                    logger.info(f"Loaded MITRE data from {p}")
                    return _cached_mitre_data
            except Exception as e:
                logger.error(f"Failed loading MITRE data from {p}: {e}")
    
    logger.error(f"MITRE data not found. Tried paths: {possible_paths}")
    return None

async def read_from_json(path: str) -> Optional[Any]:
    """Read JSON data from a file."""
    logger.info(f"Reading {path}")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed reading {path}: {e}")
        return None

async def logs_normalization(logs: Any) -> Any:
    """
    Standardize log format for the LLM.
    """
    if isinstance(logs, list):
        for event in logs:
            if isinstance(event, dict) and "timestamp" in event:
                event["timestamp"] = str(event["timestamp"])
    return logs

def clean_llm_json(text: str) -> str:
    """Extract valid JSON from LLM output, handling code blocks and extra text."""
    text = text.strip()
    
    # Remove code block wrappers
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    
    # Extract JSON object/array - find the first { or [ and match the closing bracket
    json_start = -1
    json_char = None
    for i, char in enumerate(text):
        if char in ('{', '['):
            json_start = i
            json_char = char
            break
    
    if json_start == -1:
        return text  # No JSON found, return as-is
    
    # Find matching closing bracket
    closing_char = '}' if json_char == '{' else ']'
    bracket_count = 0
    json_end = -1
    
    for i in range(json_start, len(text)):
        if text[i] == json_char:
            bracket_count += 1
        elif text[i] == closing_char:
            bracket_count -= 1
            if bracket_count == 0:
                json_end = i + 1
                break
    
    if json_end == -1:
        return text  # Couldn't find matching bracket, return as-is
    
    return text[json_start:json_end]

# -------------------------
# LLM Classification
# -------------------------

def _unescape_html_in_obj(obj: Any) -> None:
    """Recursively unescape HTML entities in all string values of a dict or list."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                obj[key] = html.unescape(value)
            else:
                _unescape_html_in_obj(value)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str):
                obj[i] = html.unescape(item)
            else:
                _unescape_html_in_obj(item)


async def classify_with_gemini(logs: List[dict], mitre_data: Any) -> Optional[List[dict]]:
    """Send logs to Gemini for individual MITRE classification."""
    if not client:
        logger.error("Metra Classifier: Gemini client not initialized.")
        return None

    logger.info(f"Metra Classifier: Sending {len(logs)} logs to Gemini for classification")
    logs_str = json.dumps(logs)
    mitre_str = json.dumps(mitre_data)

    try:
        prompt = (
            SYSTEM_PROMPT +
            "\n" + OUTPUT_SCHEMA +
            f"\nLOGS:\n{logs_str}\n\n"
            f"MITRE ATT&CK DATA:\n{mitre_str}"
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        if not response or not response.text:
            logger.error("Metra Classifier: Received empty response from Gemini.")
            return None

        raw_output = response.text
        cleaned_output = clean_llm_json(raw_output)
        
        try:
            parsed_json = json.loads(cleaned_output)
        except json.JSONDecodeError as e:
            logger.error(f"Metra Classifier: Failed to parse JSON from LLM output: {e}")
            logger.debug(f"Metra Classifier: Raw output: {raw_output[:500]}...")
            logger.debug(f"Metra Classifier: Cleaned output: {cleaned_output[:500]}...")
            return None

        # Handle batch results or single result
        results = []
        if isinstance(parsed_json, dict) and "items" in parsed_json:
            results = parsed_json["items"]
        else:
            results = [parsed_json]

        # Post-process each item for dashboard compatibility
        attacker_ip = None
        if logs and isinstance(logs, list) and len(logs) > 0:
            attacker_ip = logs[0].get("src_ip")

        for item in results:
            if not isinstance(item, dict): continue

            # Unescape HTML entities from LLM output (e.g., &amp;&amp; -> &&)
            _unescape_html_in_obj(item)

            # Inject attacker IP
            if attacker_ip:
                item["attacker_ip"] = attacker_ip
            
            # Flatten summary for dashboard
            if "analysis" in item and "summary" in item["analysis"]:
                item["summary"] = item["analysis"]["summary"]
            
            # Ensure type is set
            if "type" not in item:
                item["type"] = "risk_score"

        return results

    except Exception as e:
        logger.error(f"Metra Classifier: Exception during LLM call/parse: {e}", exc_info=True)
        return None

async def correlate_with_gemini(logs: List[dict]) -> Optional[dict]:
    """Analyze the sequence of logs to correlate them into an attack chain."""
    if not client:
        return None

    logger.info(f"Metra Classifier: Correlating {len(logs)} logs")
    logs_str = json.dumps(logs)

    try:
        prompt = (
            CORRELATION_PROMPT +
            "\n" + CORRELATION_SCHEMA +
            f"\nLOGS:\n{logs_str}"
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        if not response or not response.text:
            return None

        raw_output = response.text
        cleaned_output = clean_llm_json(raw_output)
        parsed_json = json.loads(cleaned_output)

        if logs and isinstance(logs, list) and len(logs) > 0:
            first_log = logs[0]
            if isinstance(first_log, dict) and "src_ip" in first_log:
                parsed_json["attacker_ip"] = first_log["src_ip"]

        return parsed_json

    except Exception as e:
        logger.error(f"Metra Classifier: Exception during correlation: {e}")
        return None

async def classify_logs(logs: List[dict]) -> Optional[List[dict]]:
    """High-level entry point for batch classification."""
    logger.info("Metra Classifier: classify_logs called")
    mitre_data = get_mitre_data()
    if not mitre_data:
        return None
    
    normalized = await logs_normalization(logs)
    return await classify_with_gemini(normalized, mitre_data)

async def correlate_logs(logs: List[dict]) -> Optional[dict]:
    """High-level entry point for multi-stage attack correlation."""
    logger.info("Metra Classifier: correlate_logs called")
    normalized = await logs_normalization(logs)
    return await correlate_with_gemini(normalized)

async def generate_agent_ticket(risk_result: dict) -> Optional[dict]:
    """
    Generate an agent ticket (code/config fix) based on a classification result.
    """
    if not client:
        return None

    logger.info("Metra Classifier: Generating Agent Ticket")
    try:
        context = {
            "severity": risk_result.get("severity"),
            "summary": risk_result.get("summary"),
            "mitigations": risk_result.get("mitigations", []),
            "mitre": risk_result.get("mitre_attack", [])
        }

        prompt = (
            TICKET_GENERATION_PROMPT +
            "\n" + TICKET_GENERATION_SCHEMA +
            f"\nCONTEXT:\n{json.dumps(context)}"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        if not response or not response.text:
            return None

        raw_output = response.text
        cleaned_output = clean_llm_json(raw_output)
        parsed_json = json.loads(cleaned_output)

        # Ensure type is set
        parsed_json["type"] = "agent_ticket"

        return parsed_json

    except Exception as e:
        logger.error(f"Metra Classifier: Exception during ticket generation: {e}")
        return None


async def submit_agent_ticket(ticket: dict, endpoint: str = "http://localhost:8000/api/v1/dashboard/tickets") -> bool:
    """Submit an agent ticket to the dashboard API endpoint. Returns True on success."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client_http:
            resp = await client_http.post(endpoint, json=ticket)
            if resp.status_code >= 200 and resp.status_code < 300:
                return True
            logger.warning(f"submit_agent_ticket failed: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logger.error(f"submit_agent_ticket exception: {e}")
        return False

# -------------------------
# Workflow / CLI Runner
# -------------------------

async def run_classification_workflow(
    honeypot_logs_path: str,
    mitre_attack_path: str
):
    """CLI workflow for testing."""
    logger.info("Starting classification workflow")

    honeypot_logs = await read_from_json(honeypot_logs_path)
    if not honeypot_logs:
        return

    result = await classify_logs(honeypot_logs)
    if result:
        print(json.dumps(result, indent=4))
    
    corr = await correlate_logs(honeypot_logs)
    if corr:
        print(json.dumps(corr, indent=4))

async def runner():
    logger.info("Metra Classifier: Runner started")
    # Example paths based on the new structure
    await run_classification_workflow(
        "backend/agents/data/honeypot_logs.json",
        "backend/agents/data/mitre_attack.json"
    )

if __name__ == "__main__":
    asyncio.run(runner())