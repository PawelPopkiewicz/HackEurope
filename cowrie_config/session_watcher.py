import json
import time
import requests
from collections import defaultdict

LOG_FILE = "/home/letv1n/comsci/Projects/HackEurope/cowrie_config/cowrie/var/log/cowrie/cowrie.json"
API_URL = "http://localhost:8000/api/v1/dashboard/send_honeypot_json"
BLOCK_IP_URL = "http://localhost:8000/api/v1/dashboard/block_ip"

# store logs grouped by session
sessions = defaultdict(list)

# M1040 - Behavioral Analysis: Track failed login attempts per IP
failed_login_attempts: dict[str, int] = defaultdict(int)
BRUTE_FORCE_THRESHOLD = 5  # Alert after this many failed logins from the same IP


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
        except:
            continue

        session_id = event.get("session")
        if not session_id:
            continue

        # store every event for this session
        sessions[session_id].append(event)

        # M1040 - Behavioral Analysis: detect brute-force login attempts
        if event.get("eventid") == "cowrie.login.failed":
            src_ip = event.get("src_ip")
            if src_ip:
                failed_login_attempts[src_ip] += 1
                count = failed_login_attempts[src_ip]
                if count >= BRUTE_FORCE_THRESHOLD:
                    print(f"[ALERT] Brute-force detected from {src_ip} ({count} failed logins)")
                    alert_payload = {
                        "type": "brute_force_detected",
                        "src_ip": src_ip,
                        "failed_attempts": count,
                        "session": session_id,
                        "eventid": "cowrie.login.failed",
                    }
                    try:
                        requests.post(API_URL, json=alert_payload, timeout=5)
                    except Exception as e:
                        print("Alert POST failed:", e)
                    # M1003 - Firewall: request IP block on threshold breach
                    try:
                        requests.post(
                            BLOCK_IP_URL,
                            json={"ip": src_ip, "reason": f"Brute-force: {count} failed logins"},
                            timeout=5,
                        )
                        print(f"[BLOCK] Requested block for {src_ip}")
                    except Exception as e:
                        print("Block IP POST failed:", e)

        # when session ends → send all logs for that session
        if event.get("eventid") == "cowrie.session.closed":
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
