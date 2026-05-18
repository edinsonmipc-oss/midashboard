#!/usr/bin/env python3
"""Upload Hermes Dashboard to toolshubpro.com.au/dashboard/ via FTP."""
import ftplib, os, sys

DIR = "/home/edinsonmipc/midashboard"
HOST = "153.92.8.188"
USER = "u228844205.toolshubpro"
PASS = "K7!mQ2#vL9@pX4$z"

ftp = ftplib.FTP(HOST)
ftp.login(USER, PASS)
print(f"✅ FTP logged in. PWD: {ftp.pwd()}")

# Upload index.html → /dashboard/index.html
index_path = os.path.join(DIR, "index.html")
with open(index_path, "rb") as f:
    ftp.storbinary("STOR dashboard/index.html", f)
print(f"✅ index.html ({os.path.getsize(index_path)} bytes) → /dashboard/index.html")

# Upload data.js → /dashboard/data.js (CRITICAL: at root of dashboard/, NOT in data/ subdir)
datajs_path = os.path.join(DIR, "data.js")
with open(datajs_path, "rb") as f:
    ftp.storbinary("STOR dashboard/data.js", f)
print(f"✅ data.js ({os.path.getsize(datajs_path)} bytes) → /dashboard/data.js")

# Ensure data dir exists
try:
    ftp.mkd("dashboard/data")
except:
    pass

# Upload data/*.json → /dashboard/data/*.json
data_dir = os.path.join(DIR, "data")
count = 0
for fname in sorted(os.listdir(data_dir)):
    if fname.endswith(".json"):
        local_path = os.path.join(data_dir, fname)
        with open(local_path, "rb") as f:
            ftp.storbinary(f"STOR dashboard/data/{fname}", f)
        count += 1
        print(f"  → dashboard/data/{fname} ({os.path.getsize(local_path)} bytes)")

print(f"✅ {count} data JSON files uploaded to /dashboard/data/")
ftp.quit()
print("✅ FTP upload complete")
