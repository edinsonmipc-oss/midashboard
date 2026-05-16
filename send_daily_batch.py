#!/usr/bin/env python3
import json, os, sys, time, random, smtplib, ssl
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DIR = os.path.expanduser("~/midashboard")
DATA_DIR = os.path.join(DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "email_config.json")
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")
TEMPLATES_FILE = os.path.join(DATA_DIR, "templates.json")

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def render_html_body(body):
    paragraphs = body.strip().split("\n\n")
    html_parts = []
    for p in paragraphs:
        html_parts.append("    <p>" + p.strip().replace("\n", "<br>") + "</p>")
    html_body = "\n".join(html_parts)
    return "<html><body style=\"font-family: Arial, sans-serif; line-height: 1.6; color: #333;\">\n" + html_body + "\n</body></html>"

def get_template(templates_data, business_id):
    for tmpl in templates_data.get("templates", []):
        if tmpl.get("business") == business_id or tmpl.get("id") == business_id:
            return tmpl
    return (templates_data.get("templates") or [{}])[0]

config = load_json(CONFIG_FILE)
templates = load_json(TEMPLATES_FILE)
leads = load_json(LEADS_FILE)

pending = []
for batch_key in sorted(leads.get("leads_by_date", {}).keys()):
    for idx, lead in enumerate(leads["leads_by_date"][batch_key]):
        company = lead.get("company", "")
        email = lead.get("email", "").strip()
        verified = lead.get("verified", "")
        contacted = lead.get("contacted")
        if contacted is None and verified == "verified" and email and not company.startswith("Test"):
            biz_target = lead.get("business_target", "")
            if not biz_target:
                biz_target = "antoniopaving" if lead.get("type") in ("builder", "constructora") else "primeproperty"
            pending.append({"email": email, "company": company, "business_target": biz_target, "batch_key": batch_key, "lead_index": idx})

print("Pending leads:", len(pending), file=sys.stderr)

daily_limit = config.get("daily_limit", 8)
antipaving = [p for p in pending if p["business_target"] == "antoniopaving"]
primeproperty = [p for p in pending if p["business_target"] == "primeproperty"]
to_send = antipaving[:min(len(antipaving), daily_limit)]
remaining = daily_limit - len(to_send)
to_send.extend(primeproperty[:remaining])

if not to_send:
    print("No emails to send.")
    sys.exit(0)

password = config.get("gmail_app_password") or config.get("password", "")
ctx = ssl.create_default_context()
print("Connecting to SMTP...", file=sys.stderr)
server = smtplib.SMTP(config["smtp_server"], config["smtp_port"], timeout=30)
server.ehlo()
if config.get("use_tls", True):
    server.starttls(context=ctx)
    server.ehlo()
server.login(config["sender_email"], password)
print("SMTP login OK", file=sys.stderr)

now = datetime.now()
timestamp = now.strftime("%Y-%m-%dT%H:%M")
sent_count = 0
error_count = 0
results = []

for i, item in enumerate(to_send):
    biz_id = item["business_target"]
    tmpl = get_template(templates, biz_id)
    if not tmpl:
        print("No template for", biz_id, "- skipping", item["company"], file=sys.stderr)
        continue
    biz_addr = config.get("business_addresses", {}).get(biz_id, {})
    from_name = biz_addr.get("from_name", config["sender_name"])
    from_email = biz_addr.get("from_email", config["sender_email"])
    body_text = tmpl["body"].replace("[COMPANY]", item["company"])
    body_html = render_html_body(body_text)
    subject = tmpl.get("subject", "Colaboracion en servicios")
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = from_name + " <" + from_email + ">"
        msg["To"] = item["email"]
        msg["Subject"] = subject
        msg.attach(MIMEText(body_text, "plain", "utf-8"))
        msg.attach(MIMEText(body_html, "html", "utf-8"))
        server.sendmail(from_email, item["email"], msg.as_string())
        leads["leads_by_date"][item["batch_key"]][item["lead_index"]]["contacted"] = timestamp
        leads["leads_by_date"][item["batch_key"]][item["lead_index"]]["contact_status"] = "sent"
        leads["leads_by_date"][item["batch_key"]][item["lead_index"]]["sent"] = True
        save_json(LEADS_FILE, leads)
        print("SENT[" + str(i+1) + "/" + str(len(to_send)) + "] " + biz_id.upper() + " -> " + item["email"] + " (" + item["company"] + ")")
        sent_count += 1
        results.append({"email": item["email"], "company": item["company"], "business": biz_id, "status": "sent"})
    except Exception as e:
        print("ERROR[" + str(i+1) + "] " + item["email"] + " -> " + str(e))
        error_count += 1
        results.append({"email": item["email"], "company": item["company"], "business": biz_id, "status": "error: " + str(e)[:50]})
        try:
            leads["leads_by_date"][item["batch_key"]][item["lead_index"]]["contacted"] = timestamp
            leads["leads_by_date"][item["batch_key"]][item["lead_index"]]["contact_status"] = "error: " + str(e)[:50]
            save_json(LEADS_FILE, leads)
        except:
            pass
    if i < len(to_send) - 1:
        delay = random.randint(config.get("min_delay_seconds", 180), config.get("max_delay_seconds", 300))
        print("Waiting " + str(delay) + "s before next send...", file=sys.stderr)
        sys.stdout.flush()
        time.sleep(delay)

server.quit()
print("SUMMARY: " + str(sent_count) + " sent, " + str(error_count) + " errors / " + str(len(to_send)) + " attempts")

health_path = os.path.join(DATA_DIR, "health.json")
health = load_json(health_path)
health["email_stats"] = {"last_send": timestamp, "total_sent": sent_count}
save_json(health_path, health)

report_path = os.path.join(DATA_DIR, "send_report.json")
reports = load_json(report_path)
reports["reports"].append({"date": now.strftime("%Y-%m-%d"), "time": timestamp, "sent": sent_count, "errors": error_count, "batch": results})
reports["reports"] = reports["reports"][-30:]
save_json(report_path, reports)
