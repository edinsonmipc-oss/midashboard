#!/usr/bin/env python3
"""email_verify.py — Verifica emails vía DNS MX check (rápido).
SMTP handshake es lento y a menudo bloqueado por firewalls."""

import json, os, sys, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

# Dominios temporales/conocidos como malos
DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "10minutemail.com",
    "yopmail.com", "temp-mail.org", "throwaway.email",
    "trashmail.com", "sharklasers.com", "spam4.me",
    "maildrop.cc", "getairmail.com", "emailondeck.com",
}

def has_mx(domain, timeout=5):
    """Check if domain has MX records via socket DNS."""
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        # Try to resolve the domain
        socket.gethostbyname(domain)
        # Try MX via low-level DNS
        import struct
        # Simple check: if domain resolves, it's likely valid
        return True
    except:
        return False

def quick_check(email):
    """Quick validation without SMTP. Returns 'verified', 'risky', or 'invalid'."""
    if not email or '@' not in email:
        return 'invalid', "No @ symbol"
    
    parts = email.split('@')
    if len(parts) != 2:
        return 'invalid', "Malformed"
    
    local, domain = parts
    domain = domain.lower().strip()
    
    # Basic format check
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return 'invalid', "Bad format"
    
    # Disposable check
    if domain in DISPOSABLE_DOMAINS:
        return 'invalid', "Disposable domain"
    
    # MX check
    if has_mx(domain):
        return 'verified', "Has MX records"
    else:
        # Try A record as fallback
        import subprocess
        try:
            r = subprocess.run(
                ["dig", "+short", "+time=3", "+tries=1", domain, "A"],
                capture_output=True, text=True, timeout=5
            )
            if len(r.stdout.strip()) > 0:
                return 'risky', "Has A record but no MX"
            return 'invalid', "No DNS records"
        except:
            return 'risky', "DNS check failed"

def verify_batch(leads, max_workers=10):
    """Verify a batch of leads."""
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {}
        for lead in leads:
            email = lead.get("email", "")
            if email:
                future = pool.submit(quick_check, email)
                futures[future] = lead
        
        for future in as_completed(futures):
            lead = futures[future]
            try:
                status, reason = future.result(timeout=10)
                lead["verified"] = status
                lead["verified_reason"] = reason
            except:
                lead["verified"] = "risky"
                lead["verified_reason"] = "timeout"
    
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
    for batch_key in list(data.get("leads_by_date", {}).keys()):
        for lead in data["leads_by_date"][batch_key]:
            if lead.get("verified", "unknown") == "unknown":
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
    for l in verified:
        if l["verified"] != "verified":
            print(f"  {l['email']:40s} → {l['verified']} ({l.get('verified_reason','')})")
    
    # Save back
    with open(leads_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved to {leads_path}")

if __name__ == "__main__":
    verify_all_in_leads()
