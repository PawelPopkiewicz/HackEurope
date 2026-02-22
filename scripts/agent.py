import json
import subprocess
import os

def create_github_issue(
    title: str,
    body: str,
    assignees: list[str] | None = None,
    labels: list[str] | None = None,
    base_branch: str = "main",
    custom_instructions: str = "",
    custom_agent: str = "",
    model: str = "",
):
    owner = os.getenv("OWNER")
    repo = os.getenv("REPO")

    if not repo or not owner:
        raise ValueError("OWNER and REPO environment variables must be set")
    
    payload = {
        "title": title,
        "body": body,
        "assignees": assignees or ["copilot-swe-agent[bot]"],
        "labels": labels or [],
        "agent_assignment": {
            "target_repo": f"{owner}/{repo}",
            "base_branch": base_branch,
            "custom_instructions": custom_instructions,
            "custom_agent": custom_agent,
            "model": model,
        },
    }

    result = subprocess.run(
        [
            "gh", "api",
            "--method", "POST",
            "-H", "Accept: application/vnd.github+json",
            "-H", "X-GitHub-Api-Version: 2022-11-28",
            f"/repos/{owner}/{repo}/issues",
            "--input", "-",
        ],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh api failed: {result.stderr}")

    return json.loads(result.stdout)

