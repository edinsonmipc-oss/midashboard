#!/usr/bin/env python3
"""
auto_send.py — Envío automatizado de outreach emails vía SMTP.
Lee leads.json, aplica templates con reemplazo [COMPANY] y envía
con rate limiting para evitar spam flags.

Uso:
  python3 auto_send.py                          # Envía batch (5-10) automático
  python3 auto_send.py --dry-run                # Simula sin enviar
  python3 auto_send.py --force                  # Envía aunque ya se haya enviado hoy
  python3 auto_send.py --setup                  # Muestra instrucciones de configuración
  python3 auto_send.py --test-connection        # Prueba conexión SMTP
"""

import json, os, sys, time, random, re, smtplib, ssl
from datetime import datetime, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "email_config.json")
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")
TEMPLATES_FILE = os.path.join(DATA_DIR, "templates.json")
LOG_FILE = os.path.join(DIR, "..", "business", "automations", "logs", "email-send.log")

# ── Logging ──────────────────────────────────────────────────────
def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_json(path, default=None):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default or {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ── Template Engine ──────────────────────────────────────────────
def render_body(template_body, company, from_name, signature):
    """Reemplaza [COMPANY] y personaliza el body."""
    body = template_body.replace("[COMPANY]", company)
    # Templates are self-contained with full signature — no extra footer needed
    return body

def render_html_body(body):
    """Convierte texto plano a HTML simple."""
    paragraphs = body.strip().split("\n\n")
    html_parts = []
    for p in paragraphs:
        lines = p.strip().split("\n")
        if len(lines) > 1 and any(l.startswith("•") for l in lines):
            # Bullet list
            items = "\n".join(f"      <li>{l.lstrip('• ').strip()}</li>" for l in lines if l.strip())
            html_parts.append(f"    <ul>\n{items}\n    </ul>")
        else:
            html_parts.append(f"    <p>{p.strip().replace(chr(10), '<br>')}</p>")
    html_body = "\n".join(html_parts)
    return f"""<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
{html_body}
</body></html>"""

# ── SMTP Sender ──────────────────────────────────────────────────
def create_smtp_connection(config):
    """Create and return an SMTP connection."""
    ctx = ssl.create_default_context()
    server = smtplib.SMTP(config["smtp_server"], config["smtp_port"], timeout=30)
    server.ehlo()
    if config.get("use_tls", True):
        server.starttls(context=ctx)
        server.ehlo()
    password = config.get("gmail_app_password") or config.get("password", "")
    if password:
        server.login(config["sender_email"], password)
        log("SMTP login OK")
    else:
        log("No password set — SMTP not configured for sending", "WARN")
    return server

def send_email(server, config, to_email, subject, body_html, body_text, from_name, from_email):
    """Send a single email via the SMTP connection."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    server.sendmail(from_email, to_email, msg.as_string())
    return True

# ── Lead Selection ──────────────────────────────────────────────
def get_uncontacted_leads(leads_data, contacted_set, count=10):
    """Get leads that haven't been contacted yet."""
    candidates = []
    for batch_key in sorted(leads_data.get("leads_by_date", {}).keys()):
        for lead in leads_data["leads_by_date"][batch_key]:
            email = lead.get("email", "").strip()
            if not email:
                continue
            # Skip if already contacted
            if email in contacted_set:
                continue
            # Skip unverified or invalid
            if lead.get("verified") == "invalid":
                continue
            
            biz_target = lead.get("business_target", "")
            if not biz_target:
                # Infer from type
                biz_target = "antoniopaving" if lead.get("type") in ("builder", "constructora") else "primeproperty"
            
            candidates.append({
                "email": email,
                "company": lead.get("company", ""),
                "business_target": biz_target,
                "type": lead.get("type", ""),
                "batch_key": batch_key,
            })
    
    # Shuffle for randomization
    random.shuffle(candidates)
    return candidates[:count]

def get_template(templates_data, business_id):
    """Get template for a specific business."""
    for tmpl in templates_data.get("templates", []):
        if tmpl.get("business") == business_id or tmpl.get("id") == business_id:
            return tmpl
    return templates_data.get("templates", [{}])[0] if templates_data.get("templates") else None

def load_contacted():
    """Load the contacted set from leads.json (only truly sent leads)."""
    data = load_json(LEADS_FILE, {})
    contacted = {}
    for batch_key in sorted(data.get("leads_by_date", {}).keys()):
        for lead in data["leads_by_date"][batch_key]:
            if lead.get("sent") is True or lead.get("contact_status") == "sent":
                contacted[lead.get("email", "")] = lead.get("contacted", "")
    return contacted

def mark_contacted(email, status="sent"):
    """Mark a lead as contacted in leads.json."""
    data = load_json(LEADS_FILE, {})
    now = datetime.now().strftime("%Y-%m-%dT%H:%M")
    for batch_key in data.get("leads_by_date", {}):
        for lead in data["leads_by_date"][batch_key]:
            if lead.get("email") == email:
                lead["contacted"] = now
                lead["contact_status"] = status
                lead["sent"] = (status == "sent")
                save_json(LEADS_FILE, data)
                return True
    return False

def update_health_json(seo_data=None):
    """Update health.json with email stats."""
    health_path = os.path.join(DATA_DIR, "health.json")
    health = load_json(health_path, {"sites": []})
    health["email_stats"] = {
        "last_send": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "total_sent": len(load_contacted()),
    }
    if seo_data:
        health["seo_audit"] = seo_data
    save_json(health_path, health)

# ── Main Sender ──────────────────────────────────────────────────
def send_batch(config, count=8, dry_run=False):
    """Send a batch of outreach emails."""
    templates = load_json(TEMPLATES_FILE, {})
    leads_data = load_json(LEADS_FILE, {})
    contacted = load_contacted()
    
    if not templates.get("templates"):
        log("No templates found in templates.json", "ERROR")
        return 0
    
    candidates = get_uncontacted_leads(leads_data, contacted, count)
    
    if not candidates:
        log("No new leads to contact. Everyone has been reached!", "INFO")
        return 0
    
    server = None
    if not dry_run:
        server = create_smtp_connection(config)
    
    sent = 0
    errors = 0
    daily_stats = []
    
    for i, candidate in enumerate(candidates):
        biz_id = candidate["business_target"]
        tmpl = get_template(templates, biz_id)
        if not tmpl:
            log(f"No template for {biz_id} — skipping {candidate['company']}", "WARN")
            continue
        
        biz_addr = config.get("business_addresses", {}).get(biz_id, {})
        from_name = biz_addr.get("from_name", config["sender_name"])
        from_email = biz_addr.get("from_email", config["sender_email"])
        signature = biz_addr.get("signature", from_name)

        # ── Pre-send duplicate check: re-read leads.json to confirm not already sent ──
        leads_data_fresh = load_json(LEADS_FILE, {})
        already_sent = False
        for batch_key in sorted(leads_data_fresh.get("leads_by_date", {}).keys()):
            for lead in leads_data_fresh["leads_by_date"][batch_key]:
                if lead.get("email") == candidate["email"] and (lead.get("sent") is True or lead.get("contact_status") == "sent"):
                    already_sent = True
                    break
            if already_sent:
                break
        if already_sent:
            log(f"⏭️ SKIPPED (duplicate) → {candidate['email']:35s} ({candidate['company']})")
            continue
        
        body_text = render_body(tmpl["body"], candidate["company"], from_name, signature)
        body_html = render_html_body(body_text)
        subject = tmpl.get("subject", "Colaboración en servicios")
        
        if dry_run:
            log(f"[DRY-RUN] {biz_id.upper():15s} → {candidate['email']:35s} ({candidate['company']})")
            daily_stats.append({
                "email": candidate["email"],
                "company": candidate["company"],
                "business": biz_id,
                "subject": subject,
            })
            mark_contacted(candidate["email"], "dry-run")
            sent += 1
        else:
            try:
                send_email(server, config, candidate["email"], subject, body_html, body_text, from_name, from_email)
                mark_contacted(candidate["email"], "sent")
                log(f"✅ {biz_id.upper():15s} → {candidate['email']:35s} ({candidate['company']})")
                daily_stats.append({
                    "email": candidate["email"],
                    "company": candidate["company"],
                    "business": biz_id,
                    "status": "sent",
                    "time": datetime.now().strftime("%Y-%m-%dT%H:%M"),
                })
                sent += 1
            except Exception as e:
                log(f"❌ {candidate['email']:35s} → Error: {e}", "ERROR")
                mark_contacted(candidate["email"], f"error: {str(e)[:50]}")
                errors += 1
        
        # Delay between emails (3-7 min randomized)
        if i < len(candidates) - 1 and not dry_run:
            delay = random.randint(
                config.get("min_delay_seconds", 180),
                config.get("max_delay_seconds", 420)
            )
            log(f"⏳ Esperando {delay}s antes del próximo envío...")
            time.sleep(delay)
    
    if server and not dry_run:
        try:
            server.quit()
        except:
            pass
    
    # Update health.json
    update_health_json()
    
    # Log daily summary
    log(f"📊 RESUMEN: {sent} enviados, {errors} errores, {len(candidates)} intentos")
    
    # Save daily report
    report_path = os.path.join(DATA_DIR, "send_report.json")
    reports = load_json(report_path, {"reports": []})
    reports["reports"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "sent": sent,
        "errors": errors,
        "batch": daily_stats,
    })
    reports["reports"] = reports["reports"][-30:]  # Keep last 30
    save_json(report_path, reports)
    
    return sent

# ── CLI ──────────────────────────────────────────────────────────
def show_setup():
    """Show setup instructions."""
    config = load_json(CONFIG_FILE, {})
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       AUTO SEND — Configuración de Email                ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    print("📧 Sender email configurado:", config.get("sender_email", "No configurado"))
    print("📊 Límite diario:", config.get("daily_limit", 10))
    print()
    print("🔑 Para activar el envío automático necesitas un App Password de Gmail:")
    print()
    print("  1. Ve a https://myaccount.google.com/security")
    print("  2. Activa 'Verificación en dos pasos' (2FA)")
    print("  3. Ve a 'Contraseñas de aplicaciones'")
    print("     (https://myaccount.google.com/apppasswords)")
    print("  4. Selecciona 'Correo' y 'Windows' (o 'Otra')")
    print("  5. Copia la contraseña de 16 caracteres generada")
    print()
    print("  6. Edita el archivo: data/email_config.json")
    print("     Agrega el App Password en: \"gmail_app_password\": \"TU_CODIGO_AQUÍ\"")
    print()
    print("  NOTA: La contraseña normal de Gmail NO funciona como SMTP.")
    print("  Solo funcionan App Passwords con 2FA activado.")
    print()
    print("📧 CONSEJO: Usa toolshubproau@gmail.com o el email que prefieras")
    print("  como sender_email si quieres usar su App Password.")

def test_connection():
    """Test SMTP connection."""
    config = load_json(CONFIG_FILE, {})
    password = config.get("gmail_app_password") or config.get("password", "")
    
    if not password:
        log("❌ No hay contraseña configurada. Ejecuta --setup para instrucciones.", "ERROR")
        return False
    
    try:
        server = create_smtp_connection(config)
        server.quit()
        log(f"✅ Conexión SMTP exitosa a {config['smtp_server']}:{config['smtp_port']}")
        log(f"📧 Autenticado como: {config['sender_email']}")
        return True
    except Exception as e:
        log(f"❌ Error de conexión SMTP: {e}", "ERROR")
        return False

def main():
    config = load_json(CONFIG_FILE, {})
    
    if "--setup" in sys.argv:
        show_setup()
        return
    
    if "--test-connection" in sys.argv:
        test_connection()
        return
    
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    
    count = config.get("daily_limit", 10)
    
    if not dry_run and not force:
        # Check if we already sent today
        report_path = os.path.join(DATA_DIR, "send_report.json")
        reports = load_json(report_path, {"reports": []})
        today = date.today().isoformat()
        already_sent_today = sum(
            1 for r in reports.get("reports", [])
            if r.get("date") == today
        )
        if already_sent_today > 0:
            log(f"⚠️  Ya se enviaron {already_sent_today} batches hoy ({today}). Usa --force para re-enviar.")
            print(f"⚠️  Already sent {already_sent_today} batch(es) today. Use --force to override.")
            return
    
    if not dry_run:
        password = config.get("gmail_app_password") or config.get("password", "")
        if not password:
            log("❌ No hay App Password configurado. Ejecuta --setup para instrucciones.", "ERROR")
            print("❌ No App Password set. Run --setup for instructions.")
            return
    
    log(f"🚀 Iniciando envío batch de {count} emails (dry_run={dry_run})")
    sent = send_batch(config, count=count, dry_run=dry_run)
    log(f"✅ Batch completo: {sent} emails procesados")

if __name__ == "__main__":
    main()
