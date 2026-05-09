#!/usr/bin/env python3
"""Send daily email outreach batch."""
import json, os, time, random, smtplib, ssl, sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DIR = os.path.dirname(os.path.abspath(__file__))
DD = os.path.join(DIR, "data")
CONFIG = json.load(open(os.path.join(DD, "email_config.json")))
LEADS = os.path.join(DD, "leads.json")
TEMPLATES = os.path.join(DD, "templates.json")

with open(TEMPLATES) as f:
    TM = {t["id"]: t for t in json.load(f)["templates"]}

MIN_D = CONFIG.get("min_delay_seconds", 180)
MAX_D = CONFIG.get("max_delay_seconds", 300)
print(f"Delay range: {MIN_D}-{MAX_D}s")

with open(LEADS) as f:
    LD = json.load(f)

PB = {"constructora": [], "builder": [], "real_estate": [], "property_mgmt": [], "strata": []}
OT = []
for db, leads in LD.get("leads_by_date", {}).items():
    for idx, lead in enumerate(leads):
        c = lead.get("company", "")
        e = lead.get("email", "")
        if c.startswith("Test") or not e: continue
        if "contacted" in lead: continue
        if lead.get("verified") != "verified": continue
        t = lead.get("type", "")
        entry = (db, idx, lead)
        if t in PB: PB[t].append(entry)
        else: OT.append(entry)

print(f"Pending: const={len(PB['constructora'])} bld={len(PB['builder'])} re={len(PB['real_estate'])} pm={len(PB['property_mgmt'])} strata={len(PB['strata'])}")

ap = PB["constructora"][:3] + PB["builder"][:3]
pp = PB["real_estate"][:3] + PB["property_mgmt"][:3] + PB["strata"][:3]
if len(ap) < 4:
    ap.extend([e for e in OT if e[2].get("type") in ("constructora","builder")][:4-len(ap)])
    if len(ap) < 4:
        ap.extend([e for e in OT][:4-len(ap)])
if len(pp) < 4:
    pp.extend([e for e in OT if e[2].get("type") not in ("constructora","builder")][:4-len(pp)])

ap_b = ap[:4]
pp_b = pp[:4]
total = len(ap_b) + len(pp_b)
print(f"Batch: {len(ap_b)} antoniopaving + {len(pp_b)} primeproperty = {total}")

if total == 0:
    print("No pending leads. Exiting.")
    sys.exit(0)

print("Connecting to SMTP...")
ctx = ssl.create_default_context()
server = smtplib.SMTP(CONFIG["smtp_server"], CONFIG["smtp_port"], timeout=30)
server.ehlo()
if CONFIG.get("use_tls", True):
    server.starttls(context=ctx)
    server.ehlo()
pw = CONFIG.get("gmail_app_password") or CONFIG.get("password", "")
server.login(CONFIG["sender_email"], pw)
print("SMTP login OK")

ap_tpl = TM["antoniopaving"]
pp_tpl = TM["primeproperty"]

sent = 0
failed = 0
updated = []

def send_one(entry, tpl, biz_key):
    global sent, failed
    db, idx, lead = entry
    co = lead["company"]
    to_e = lead["email"]
    biz = CONFIG["business_addresses"][biz_key]
    fn = biz["from_name"]
    fe = biz["from_email"]
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{fn} <{fe}>"
    msg["To"] = to_e
    msg["Subject"] = tpl["subject"]
    msg.attach(MIMEText(tpl["body"], "plain", "utf-8"))
    pars = tpl["body"].strip().split("\n\n")
    hp = []
    for p in pars:
        ls = p.strip().split("\n")
        if len(ls) > 1 and any(l.startswith("\u2022") for l in ls):
            items = "\n".join(f"<li>{l.lstrip(chr(0x2022)+' ').strip()}</li>" for l in ls if l.strip())
            hp.append("<ul>\n" + items + "\n</ul>")
        else:
            hp.append("<p>" + p.strip().replace(chr(10),"<br>") + "</p>")
    html = "<html><body style=\"font-family:Arial,sans-serif;line-height:1.6;color:#333;\">\n" + "\n".join(hp) + "\n</body></html>"
    msg.attach(MIMEText(html, "html", "utf-8"))
    try:
        server.sendmail(fe, to_e, msg.as_string())
        print(f"  SENT: {co} <{to_e}> via {biz_key}")
        lead["contacted"] = datetime.now().strftime("%Y-%m-%dT%H:%M")
        lead["contact_status"] = "sent"
        updated.append((db, idx, lead))
        sent += 1
    except Exception as e:
        print(f"  FAILED: {co} <{to_e}>: {e}")
        failed += 1

print("\n--- AntonioPrimeScape Construction ---")
for i, entry in enumerate(ap_b):
    print(f"\n[{i+1}/{len(ap_b)}] {entry[2]['company']} <{entry[2]['email']}>")
    send_one(entry, ap_tpl, "antoniopaving")
    if i < len(ap_b) - 1:
        d = random.randint(MIN_D, MAX_D)
        print(f"  Delay {d}s...")
        time.sleep(d)

print("\n--- Prime Property Maintenance ---")
for i, entry in enumerate(pp_b):
    print(f"\n[{i+1}/{len(pp_b)}] {entry[2]['company']} <{entry[2]['email']}>")
    send_one(entry, pp_tpl, "primeproperty")
    if i < len(pp_b) - 1:
        d = random.randint(MIN_D, MAX_D)
        print(f"  Delay {d}s...")
        time.sleep(d)

server.quit()
print(f"\n=== Sent: {sent}  Failed: {failed} ===")

for db, idx, lead in updated:
    LD["leads_by_date"][db][idx] = lead
with open(LEADS, "w") as f:
    json.dump(LD, f, indent=2, ensure_ascii=False)
print(f"Updated leads.json ({len(updated)} contacts).")

rp = os.path.join(DD, "send_report.json")
report = json.load(open(rp)) if os.path.exists(rp) else {}
today = datetime.now().strftime("%Y-%m-%d")
report[today] = {
    "sent": sent, "failed": failed, "total": sent+failed,
    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M"),
    "details": [{"company": e[2]["company"], "email": e[2]["email"], "type": e[2].get("type",""), "template": "antoniopaving" if e in ap_b else "primeproperty", "status": "sent"} for e in updated]
}
with open(rp, "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("Updated send_report.json.")
