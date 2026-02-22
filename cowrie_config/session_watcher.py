import json
import time
import requests
from collections import defaultdict

LOG_FILE = "/home/cowrie/cowrie/var/log/cowrie/cowrie.json"
API_URL = "http://localhost:8000/api/v1/dashboard/send_honeypot_json"

# Thresholds for brute-force detection (M1027 - Technical Controls)
BRUTE_FORCE_THRESHOLD = 5  # failed attempts before alerting
BRUTE_FORCE_WINDOW = 60    # seconds

# Commands that warrant elevated alerting (T1046, T1095, T1083)
SUSPICIOUS_COMMANDS = {"netcat", "nc", "ncat", "wget", "curl", "chmod", "bash", "sh", "python", "perl"}

# store logs grouped by session
sessions = defaultdict(list)

# track failed login attempts per IP for brute-force detection (T1110)
failed_logins: dict[str, list] = defaultdict(list)
# track IPs that have already triggered a brute-force alert to suppress spam
alerted_ips: set = set()


def _check_brute_force(src_ip: str) -> bool:
    """Return True if the IP has exceeded the failed-login threshold within the window."""
    now = time.time()
    attempts = [t for t in failed_logins[src_ip] if now - t < BRUTE_FORCE_WINDOW]
    failed_logins[src_ip] = attempts
    return len(attempts) >= BRUTE_FORCE_THRESHOLD


def _is_suspicious_command(command: str) -> bool:
    """Return True if the command matches a known suspicious tool."""
    cmd_base = command.strip().split()[0] if command.strip() else ""
    return cmd_base.lower() in SUSPICIOUS_COMMANDS


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

        event_id = event.get("eventid", "")
        src_ip = event.get("src_ip", "")

        # --- Brute-force detection (T1110 / M1027) ---
        if event_id == "cowrie.login.failed":
            failed_logins[src_ip].append(time.time())
            if _check_brute_force(src_ip) and src_ip not in alerted_ips:
                alerted_ips.add(src_ip)
                print(f"[ALERT] Brute-force detected from {src_ip} "
                      f"({len(failed_logins[src_ip])} failed attempts in {BRUTE_FORCE_WINDOW}s)")

        # --- Root login with empty password alert (T1078 / M1047) ---
        elif event_id == "cowrie.login.success":
            username = event.get("username", "")
            password = event.get("password", "")
            if username == "root" and password == "":
                print(f"[ALERT] Root login with empty password from {src_ip} – "
                      "investigate immediately and disable PermitEmptyPasswords")

        # --- Suspicious command detection (T1046, T1095 / M1027) ---
        elif event_id == "cowrie.command.input":
            command = event.get("input", "")
            if _is_suspicious_command(command):
                print(f"[ALERT] Suspicious command '{command}' executed in session "
                      f"{session_id} from {src_ip}")

        # store every event for this session
        sessions[session_id].append(event)

        # when session ends → send all logs for that session
        if event_id == "cowrie.session.closed":
            print("Session closed:", session_id)

            payload = {
                "session": session_id,
                "logs": sessions[session_id]
            }

            try:
                requests.post(API_URL, json=payload, timeout=5)
                print(f"POST sent ({len(payload['logs'])} events)")
            except Exception as e:
                print("POST failed:", e)

            # remove from memory after sending
            del sessions[session_id]
