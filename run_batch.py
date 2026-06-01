#!/usr/bin/env python3
"""Wrapper that runs send_daily_batch.py and logs to a file."""
import sys, subprocess
with open('email_batch.log', 'a') as log:
    log.write(f"\n=== Batch started {__import__('datetime').datetime.now()} ===\n")
    p = subprocess.Popen(
        [sys.executable, '-u', 'send_daily_batch.py'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )
    for line in p.stdout:
        print(line, end='', flush=True)
        log.write(line)
        log.flush()
    p.wait()
    log.write(f"=== Exit code: {p.returncode} ===\n")
    sys.exit(p.returncode)
