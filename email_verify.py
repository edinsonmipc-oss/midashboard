#!/usr/bin/env python3
"""email_verify.py — Verifica emails vía DNS MX + SMTP handshake.
Se ejecuta desde leadgen.py y también se puede llamar standalone."""

import json, os, socket, smtplib, dns.resolver, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

# Dominios temporales/conocidos como malos
DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "10minutemail.com",
    "yopmail.com", "temp-mail.org", "throwaway.email",
    "trashmail.com", "sharklasers.com", "spam4.me",
}

def has_mx(domain):
    """Check if domain has MX records."""
    try:
        answers = dns.resolver.resolve(domain, 'MX', lifetime=5)
        return len(answers) > 0
    except:
        return False

def verify_email_smtp(email, from_addr="verify@toolshubpro.com.au", timeout=8):
    """Verify email via SMTP handshake (RCPT TO check).
    Returns: 'verified', 'risky', or 'invalid'"""
    try:
        domain = email.split('@')[1].lower()
        
        # Check disposable
        if domain in DISPOSABLE_DOMAINS:
            return 'invalid', "Disposable email domain"
        
        # Check MX
        if not has_mx(domain):
            return 'invalid', "No MX records"
        
        # SMTP check
        mx_records = dns.resolver.resolve(domain, 'MX', lifetime=5)
        mx_host = str(sorted(mx_records, key=lambda r: r.preference)[0].exchange)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((mx_host, 25))
            
            with smtplib.SMTP(timeout=timeout) as smtp:
                smtp.set_debuglevel(0)
                smtp.connect(mx_host, 25)
                smtp.ehlo_or_helo_if_needed()
                smtp.mail(from_addr)
                code, msg = smtp.rcpt(email)
                
                if code == 250:
                    return 'verified', "SMTP confirmed"
                elif code == 251:
                    return 'verified', "SMTP: will forward"
                elif code == 450:
                    return 'risky', "SMTP: mailbox busy"
                elif code == 550:
                    return 'invalid', f"SMTP: {msg}"
                else:
                    return 'risky', f"SMTP code {code}"
    except Exception as e:
        return 'risky', str(e)[:60]

def verify_batch(leads, max_workers=5):
    """Verify a batch of leads. Returns leads with verification status."""
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {}
        for lead in leads:
            email = lead.get("email", "")
            if email:
                future = pool.submit(verify_email_smtp, email)
                futures[future] = lead
        
        for future in as_completed(futures):
            lead = futures[future]
            try:
                status, reason = future.result()
                lead["verified"] = status
                lead["verified_reason"] = reason
            except:
                lead["verified"] = "risky"
                lead["verified_reason"] = "pool error"
    
    return leads

def verify_all_in_leads():
    """Verify all unverified leads in leads.json."""
    leads_path = os.path.join(DIR, "data", "leads.json")
    if not os.path.exists(leads_path):
        print("No leads.json found")
        return
    
    with open(leads_path) as f:
        data = json.load(f)
    
    all_leads = []
    for batch_key in data.get("leads_by_date", {}):
        for lead in data["leads_by_date"][batch_key]:
            if "verified" not in lead:
                all_leads.append(lead)
    
    if not all_leads:
        print("All leads already verified")
        return
    
    print(f"Verifying {len(all_leads)} unverified leads...")
    verified = verify_batch(all_leads)
    
    v = sum(1 for l in verified if l["verified"] == "verified")
    r = sum(1 for l in verified if l["verified"] == "risky")
    inv = sum(1 for l in verified if l["verified"] == "invalid")
    
    print(f"Results: {v} verified, {r} risky, {inv} invalid")
    
    # Save back
    with open(leads_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved to {leads_path}")

if __name__ == "__main__":
    verify_all_in_leads()
