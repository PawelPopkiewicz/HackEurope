"""Script to start the Cowrie honeypot and its session watcher."""

import subprocess as sp

cowrie_pr = sp.run(["cowrie", "start"], check=True)
streamer_pr = sp.run(["python3", "cowrie/session_watcher.py"], check=True)

if cowrie_pr.returncode != 0 or streamer_pr != 0:
    print("Scripts failed to run")
