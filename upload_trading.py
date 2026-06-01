"""Upload trading.json via FTP"""
import ftplib

HOST = "153.92.8.188"
USER = "u228844205.toolshubpro"
PASS = "P8c$J5v#M2uX7aQ4"

try:
    ftp = ftplib.FTP(HOST, USER, PASS, timeout=30)
    ftp.cwd("/")
    for d in ["dashboard", "data"]:
        try:
            ftp.cwd(d)
        except:
            ftp.cwd("/")
            ftp.mkd(d)
            ftp.cwd(d)
    ftp.cwd("/dashboard/data")
    with open("data/trading.json", "rb") as f:
        ftp.storbinary("STOR trading.json", f)
    ftp.quit()
    print("OK - trading.json uploaded successfully")
except Exception as e:
    print(f"FAILED: {e}")
