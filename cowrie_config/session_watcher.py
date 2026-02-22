import json
import time
import subprocess
import requests
from collections import defaultdict

LOG_FILE = "/home/letv1n/comsci/Projects/HackEurope/cowrie_config/cowrie/var/log/cowrie/cowrie.json"
API_URL = "http://localhost:8000/api/v1/dashboard/send_honeypot_json"

# --- M1030 / M1034: Automated IP Blocking configuration ---
BRUTE_FORCE_THRESHOLD = 5   # block after this many failed logins from one IP
IP_WHITELIST = {"127.0.0.1", "::1"}   # never block these IPs

# --- M1041: Suspicious command patterns (Application Control) ---
MALICIOUS_PATTERNS = [
    "wget ", "curl ", "chmod +x", "/bin/sh", "/bin/bash",
    "base64 ", "python -c", "perl -e", "nc ", "ncat ",
    "rm -rf", "/etc/passwd", "/etc/shadow",
]
_MALICIOUS_PATTERNS_LOWER = [p.lower() for p in MALICIOUS_PATTERNS]

# track per-IP failed login count across sessions (M1034)
failed_attempts = defaultdict(int)
# track already-blocked IPs to avoid duplicate iptables calls
blocked_ips: set[str] = set()

# store logs grouped by session
sessions = defaultdict(list)


def block_ip(ip: str) -> None:
    """Add an iptables DROP rule for the given IP (M1034 - Automated Blocking)."""
    if ip in blocked_ips or ip in IP_WHITELIST:
        return
    blocked_ips.add(ip)
    try:
        subprocess.run(
            ["iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"],
            check=True,
            capture_output=True,
        )
        print(f"[BLOCK] Blocked IP {ip} via iptables (M1034)")
    except FileNotFoundError:
        print(f"[BLOCK] iptables not available; would have blocked {ip}")
    except subprocess.CalledProcessError as exc:
        print(f"[BLOCK] Failed to block {ip}: {exc.stderr.decode().strip()}")


def contains_malicious_command(command: str) -> bool:
    """Return True if the command matches a known malicious pattern (M1041)."""
    lower = command.lower()
    return any(pat in lower for pat in _MALICIOUS_PATTERNS_LOWER)


def follow(file):
    file.seek(0, 2)  # go to end of file
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.2)
            continue
        yield line


with open(LOG_FILE, "r") as f:
    print("Session watcher is up and running")

    for line in follow(f):
        try:
            event = json.loads(line)
        except Exception:
            continue

        session_id = event.get("session")
        if not session_id:
            continue

        # store every event for this session
        sessions[session_id].append(event)

        event_id = event.get("eventid", "")
        src_ip = event.get("src_ip", "")

        # --- M1034: track failed logins and auto-block brute-forcers ---
        if event_id == "cowrie.login.failed" and src_ip:
            failed_attempts[src_ip] += 1
            if failed_attempts[src_ip] >= BRUTE_FORCE_THRESHOLD:
                block_ip(src_ip)

        # --- M1041: alert on suspicious / malicious commands ---
        if event_id in ("cowrie.command.input", "cowrie.command.success"):
            command = event.get("input", event.get("message", ""))
            if contains_malicious_command(command):
                print(f"[ALERT] Malicious command detected from {src_ip}: {command!r}")

        # when session ends → send all logs for that session
        if event_id == "cowrie.session.closed":
            print("Session closed:", session_id)

            payload = sessions[session_id]

            try:
                requests.post(API_URL, json=payload, timeout=5)
                print(f"POST sent ({len(payload)} events)")
            except Exception as e:
                print("POST failed:", e)

            # remove from memory after sending
            del sessions[session_id]
