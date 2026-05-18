#!/usr/bin/env python3
"""healthcheck.py — Verifica disponibilidad de sitios y actualiza data/health.json"""

import json, os, urllib.request, urllib.error
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

def check_site(url):
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "HermesHealthCheck/1.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        return "online", resp.status
    except Exception as e:
        return "offline", str(e)

def main():
    health_path = os.path.join(DIR, "data", "health.json")
    with open(health_path) as f:
        data = json.load(f)
    
    now = datetime.now().strftime("%Y-%m-%dT%H:%M")
    
    for site in data.get("sites", []):
        status, info = check_site(site["url"])
        site["status"] = status
        site["last_checked"] = now
        if status == "offline":
            if "issues" not in site or not any("offline" in i for i in site["issues"]):
                site.setdefault("issues", []).append(f"⚠️ Sitio offline: {info}")
    
    data["updated"] = now
    
    with open(health_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    online = sum(1 for s in data["sites"] if s["status"] == "online")
    print(f"✅ HealthCheck: {online}/{len(data['sites'])} sitios online")
    return True

if __name__ == "__main__":
    main()
