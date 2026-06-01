import json, os, sys, time, random, smtplib, ssl
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Unbuffered
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

DIR = os.path.abspath(".")
DATA_DIR = os.path.join(DIR, "data")

with open(os.path.join(DATA_DIR, "email_config.json")) as f:
    config = json.load(f)
with open(os.path.join(DATA_DIR, "templates.json")) as f:
    templates_data = json.load(f)
with open(os.path.join(DATA_DIR, "leads.json")) as f:
    leads_data = json.load(f)

daily_limit = config.get("daily_limit", 8)
min_delay = config.get("min_delay_seconds", 180)
max_delay = config.get("max_delay_seconds", 300)
sender = config["sender_email"]
password = config["gmail_app_password"]
smtp_server = config["smtp_server"]
smtp_port = config["smtp_port"]

sys.path.insert(0, DIR)
import brand_router
import email_validator  # MANDATORY pre-send validation gate

# Load bounced generic email domains into blacklist (in case not already loaded)
email_validator.load_bad_domains()

lbd = leads_data.get("leads_by_date", {})
pending = []
rejected_before_send = []  # Track emails rejected by validator
for date_key, leads_list in lbd.items():
    for idx, lead in enumerate(leads_list):
        has_contacted = "contacted" in lead and lead["contacted"]
        is_verified = lead.get("verified") == "verified"
        company = lead.get("company", "")
        email = lead.get("email", "")
        if not has_contacted and is_verified and email and not company.startswith("Test"):
            # PRE-SEND VALIDATION GATE: reject generic/blacklisted/disposable emails
            approved, result = email_validator.validate_before_send(email, max_age_hours=1)
            if not approved:
                reason = result.get("reason", "unknown")
                detail = result.get("detail", "")
                print(f"  REJECTED [{reason:20s}] {email:40s} ({company}) — {detail[:50]}")
                rejected_before_send.append({
                    "company": company,
                    "email": email,
                    "reason": reason,
                    "detail": detail
                })
                # Mark lead as invalid so it won't be picked up again
                lead["verified"] = "invalid"
                lead["verified_reason"] = f"REJECTED: {reason} — {detail}"
                lead["rejected_before_send"] = True
                continue
            pending.append((date_key, idx, lead))

print(f"Config: daily_limit={daily_limit}, delays={min_delay}-{max_delay}s")
print(f"Found {len(pending)} pending verified leads ({len(rejected_before_send)} rejected by validator)")

batch = pending[:daily_limit]
print(f"Sending {len(batch)} emails this batch")

if not batch:
    print("No emails to send. Exiting.")
    sys.exit(0)

routed = []
for date_key, idx, lead in batch:
    routing = brand_router.classify_lead(lead)
    brand = routing["brand"]
    template_info = routing["template"]
    brand_config = routing["brand_config"]
    company = lead.get("company", "")
    contact_name = lead.get("contact", "").split(" ")[0] if lead.get("contact") else ""
    body = template_info["body"].replace("{company}", company).replace("[COMPANY]", company).replace("{first_name}", contact_name if contact_name else company)
    subject = template_info["subject"].replace("{company}", company).replace("[COMPANY]", company)
    routed.append({"date_key": date_key, "idx": idx, "lead": lead, "company": company, "email": lead["email"], "brand": brand, "subject": subject, "body": body, "from_name": brand_config["name"]})
    print(f"  Routed {company:30s} -> {brand:15s} | {subject}")

print(f"\nConnecting to SMTP {smtp_server}:{smtp_port}...")
context = ssl.create_default_context()
server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls(context=context)
server.login(sender, password)
print("SMTP connected!")

sent_log, errors = [], []

for i, item in enumerate(routed):
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{item['from_name']} <{sender}>"
    msg["To"] = item["email"]
    msg["Subject"] = item["subject"]
    msg.attach(MIMEText(item["body"], "plain"))
    html_body = item["body"].replace("\n", "<br>\n")
    msg.attach(MIMEText(f'<html><body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;">\n{html_body}\n</body></html>', "html"))
    try:
        server.sendmail(sender, item["email"], msg.as_string())
        ts = datetime.now().strftime("%Y-%m-%dT%H:%M")
        print(f"  OK SENT [{item['brand']:15s}] -> {item['email']:35s} ({item['company']})")
        sent_log.append({"company": item["company"], "email": item["email"], "business": item["brand"], "status": "sent", "time": ts})
        item["lead"]["contacted"] = ts
        item["lead"]["contact_status"] = "sent"
        item["lead"]["sent"] = True
        if i < len(routed) - 1:
            delay = random.randint(min_delay, max_delay)
            print(f"     WAIT {delay}s before next...")
            time.sleep(delay)
    except Exception as e:
        print(f"  FAIL [{item['brand']:15s}] -> {item['email']:35s}: {e}")
        errors.append({"company": item["company"], "email": item["email"], "error": str(e)})

server.quit()
print(f"\nDONE: {len(sent_log)} sent, {len(errors)} errors, {len(rejected_before_send)} rejected (generic/bounced)")

with open(os.path.join(DATA_DIR, "leads.json"), "w") as f:
    json.dump(leads_data, f, indent=2, ensure_ascii=False)
print("leads.json updated")

report_path = os.path.join(DATA_DIR, "send_report.json")
if os.path.exists(report_path):
    with open(report_path) as f:
        report_data = json.load(f)
else:
    report_data = {"reports": []}
today_str = datetime.now().strftime("%Y-%m-%d")
report_data["reports"].append({"date": today_str, "time": datetime.now().strftime("%Y-%m-%dT%H:%M"), "sent": len(sent_log), "errors": len(errors), "batch": sent_log})
with open(report_path, "w") as f:
    json.dump(report_data, f, indent=2, ensure_ascii=False)
print("send_report.json updated")

with open(os.path.join(DIR, "email_batch.log"), "a") as f:
    f.write(f"\n--- Batch {today_str} ---\n")
    for s in sent_log:
        f.write(f"[{s['time']}] OK SENT [{s['business']}] -> {s['email']} ({s['company']})\n")
    for e in errors:
        f.write(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M')}] FAIL -> {e['email']} ({e['company']}): {e['error']}\n")
    for r in rejected_before_send:
        f.write(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M')}] REJECTED [{r['reason']}] -> {r['email']} ({r['company']}): {r['detail'][:60]}\n")
    f.write(f"DONE: {len(sent_log)} sent, {len(errors)} errors, {len(rejected_before_send)} rejected\n")
print("email_batch.log updated")

sys.exit(1 if errors else 0)
