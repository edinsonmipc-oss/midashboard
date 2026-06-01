#!/usr/bin/env python3
"""
deploy_dashboard.py — Genera y sube el Hermes Dashboard a toolshubpro.com.au/dashboard/
Se ejecuta vía cron cada 6 horas.
"""
import ftplib, os, sys

DIR = os.path.dirname(os.path.abspath(__file__))

def upload():
    # 1. Generate dashboard
    os.chdir(DIR)
    ret = os.system("python3 generate.py")
    if ret != 0:
        print("❌ generate.py failed")
        return False
    
    # 2. FTP upload
    ftp = ftplib.FTP("153.92.8.188")
    try:
        ftp.login("u228844205.toolshubpro", "K7!mQ2#vL9@pX4$z")
        ftp.cwd("..")  # web root
        
        # Upload index.html
        index_path = os.path.join(DIR, "index.html")
        with open(index_path, "rb") as f:
            ftp.storbinary("STOR dashboard/index.html", f)
        print(f"✅ index.html ({os.path.getsize(index_path)} bytes)")
        
        # Ensure data dir exists
        try:
            ftp.mkd("dashboard/data")
        except:
            pass
        
        # Upload data files
        data_dir = os.path.join(DIR, "data")
        count = 0
        for fname in os.listdir(data_dir):
            if fname.endswith(".json"):
                local_path = os.path.join(data_dir, fname)
                with open(local_path, "rb") as f:
                    ftp.storbinary(f"STOR dashboard/data/{fname}", f)
                count += 1
        print(f"✅ {count} data files uploaded")
        
        # 3. Verify
        ftp.quit()
        
        # Verify via HTTP
        import urllib.request
        req = urllib.request.urlopen("http://toolshubpro.com.au/dashboard/")
        html = req.read().decode()
        if "PrimeHermes Dashboard" in html:
            print("✅ Verification: Dashboard loads correctly")
            return True
        else:
            print("⚠️ Verification: Dashboard loaded but title missing")
            return False
            
    except Exception as e:
        print(f"❌ FTP Error: {e}")
        return False

if __name__ == "__main__":
    success = upload()
    sys.exit(0 if success else 1)
