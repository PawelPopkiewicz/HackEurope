import json
import os
import time
import requests
from collections import defaultdict

LOG_FILE = os.getenv(
    "COWRIE_LOG_FILE",
    "/var/log/cowrie/cowrie.json",
)
API_URL = os.getenv(
    "DASHBOARD_API_URL",
    "http://localhost:8000/api/v1/dashboard/send_honeypot_json",
)
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")

# store logs grouped by session
sessions = defaultdict(list)


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

        # when session ends → send all logs for that session
        if event.get("eventid") == "cowrie.session.closed":
            print("Session closed:", session_id)

            payload = {
                "session": session_id,
                "logs": sessions[session_id]
            }

            try:
                headers = {}
                if INTERNAL_API_TOKEN:
                    headers["X-Internal-Token"] = INTERNAL_API_TOKEN
                requests.post(API_URL, json=payload, headers=headers, timeout=5)
                print(f"POST sent ({len(payload['logs'])} events)")
            except Exception as e:
                print("POST failed:", e)

            # remove from memory after sending
            del sessions[session_id]
