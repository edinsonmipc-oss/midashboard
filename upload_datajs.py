#!/usr/bin/env python3
"""Upload data.js to /dashboard/"""
import ftplib, os

HOST = "153.92.8.188"
USER = "u228844205.toolshubpro"
PASS = "K7!mQ2#vL9@pX4$z"
BASE_DIR = "/home/edinsonmipc/midashboard"

ftp = ftplib.FTP(HOST)
ftp.login(USER, PASS)
ftp.cwd("..")

data_js_path = BASE_DIR + "/data.js"
with open(data_js_path, "rb") as f:
    ftp.storbinary("STOR dashboard/data.js", f)
print("Uploaded data.js (" + str(os.path.getsize(data_js_path)) + " bytes)")
ftp.quit()
