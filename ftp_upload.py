#!/usr/bin/env python3
"""FTP upload for Hermes Dashboard"""
import ftplib, os, sys

HOST = "toolshubpro.com.au"
USER = "u228844205.toolshubpro"
PASS = "K7!mQ2#vL9@pX4$z"
BASE_DIR = "/home/edinsonmipc/midashboard"

try:
    ftp = ftplib.FTP(HOST)
    ftp.login(USER, PASS)
    print("FTP connected")

    # cd /dashboard
    try:
        ftp.cwd("/dashboard")
    except:
        ftp.mkd("/dashboard")
        ftp.cwd("/dashboard")

    # Upload index.html
    with open(BASE_DIR + "/index.html", "rb") as f:
        ftp.storbinary("STOR index.html", f)
    print("Uploaded: index.html")

    # Upload data.js
    with open(BASE_DIR + "/data.js", "rb") as f:
        ftp.storbinary("STOR data.js", f)
    print("Uploaded: data.js")

    # Upload data/*.json
    try:
        ftp.cwd("data")
    except:
        ftp.mkd("data")
        ftp.cwd("data")

    data_dir = BASE_DIR + "/data"
    json_files = sorted(f for f in os.listdir(data_dir) if f.endswith(".json"))
    for fname in json_files:
        with open(data_dir + "/" + fname, "rb") as f:
            ftp.storbinary("STOR " + fname, f)
        print("Uploaded: data/" + fname)

    ftp.quit()
    print()
    print("Summary: 1 HTML + 1 JS + " + str(len(json_files)) + " JSON files uploaded")
    print("URL: http://toolshubpro.com.au/dashboard/")
    sys.exit(0)

except Exception as e:
    print("FTP Error: " + str(e), file=sys.stderr)
    sys.exit(1)
