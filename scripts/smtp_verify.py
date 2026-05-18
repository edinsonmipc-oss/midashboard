#!/usr/bin/env python3
"""SMTP email verification - checks if emails actually exist via SMTP handshake."""
import smtplib
import socket
import json
import sys
import time
import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.mime.text import MIMEText

# Gmail SMTP credentials
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = "antonioprimemaintenance@gmail.com"
FROM_PASSWORD = "pvir coud cwng udvs"

def verify_email_smtp(email, timeout=15):
    """Verify email via SMTP RCPT TO handshake.
    Returns: (status, detail) where status is 'valid', 'invalid', 'risky', or 'error'
    """
    try:
        domain = email.split('@')[1]
        
        # Step 1: Get MX records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_record = str(sorted(mx_records, key=lambda r: r.preference)[0].exchange)
        except:
            return 'invalid', f'No MX records for {domain}'
        
        # Step 2: SMTP handshake
        server = smtplib.SMTP(timeout=timeout)
        server.set_debuglevel(0)
        server.connect(mx_record, 25)
        server.ehlo_or_helo_if_needed()
        
        # Some servers require HELO before MAIL FROM
        server.mail(FROM_EMAIL)
        
        code, message = server.rcpt(email)
        server.quit()
        
        if code == 250:
            return 'valid', 'SMTP accepted'
        elif code == 550 or code == 551 or code == 552 or code == 553 or code == 450:
            return 'invalid', f'SMTP rejected ({code})'
        else:
            return 'risky', f'SMTP response ({code})'
            
    except smtplib.SMTPServerDisconnected:
        return 'risky', 'Server disconnected'
    except socket.timeout:
        return 'risky', 'SMTP timeout'
    except Exception as e:
        return 'error', str(e)[:100]

def verify_email_dns(email, timeout=10):
    """Fallback: DNS MX verification only."""
    try:
        domain = email.split('@')[1]
        mx_records = dns.resolver.resolve(domain, 'MX')
        return 'risky', f'Has MX records ({len(mx_records)} found)'
    except:
        return 'invalid', 'No MX records'

def verify_emails(emails, use_smtp=True):
    """Verify a list of emails in parallel."""
    results = []
    
    def verify_one(email_info):
        email = email_info['email']
        name = email_info.get('name', '')
        company = email_info.get('company', '')
        title = email_info.get('title', '')
        
        if use_smtp:
            status, detail = verify_email_smtp(email)
            time.sleep(1)  # Be polite to mail servers
        else:
            status, detail = verify_email_dns(email)
        
        return {
            'email': email,
            'name': name,
            'company': company,
            'title': title,
            'status': status,
            'detail': detail
        }
    
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(verify_one, e) for e in emails]
        for future in as_completed(futures):
            results.append(future.result())
    
    results.sort(key=lambda r: r['email'])
    return results

def main():
    # Generate emails for Henley Properties
    henley_contacts = [
        {'name': 'Ben Sayers', 'email': 'ben.sayers@henley.com.au', 'company': 'Henley Properties', 'title': 'Construction Manager'},
        {'name': 'George Agiazis', 'email': 'george.agiazis@henley.com.au', 'company': 'Henley Properties', 'title': 'Construction Supervisor'},
        {'name': 'Harmohan Singh', 'email': 'harmohan.singh@henley.com.au', 'company': 'Henley Properties', 'title': 'Construction Supervisor'},
        {'name': 'Darren Dean', 'email': 'darren.dean@henley.com.au', 'company': 'Henley Properties', 'title': 'General Manager'},
        {'name': 'Mark Glenn', 'email': 'mark.glenn@henley.com.au', 'company': 'Henley Properties', 'title': 'Construction'},
        {'name': 'Tim O\'Shea', 'email': 'tim.oshea@henley.com.au', 'company': 'Henley Properties', 'title': 'Construction'},
        # Also try with dot
        {'name': 'Tim O\'Shea', 'email': 'tim.o\'shea@henley.com.au', 'company': 'Henley Properties', 'title': 'Construction'},
        # Try variations
        {'name': 'Ben Sayers', 'email': 'ben.sayers@henley.com', 'company': 'Henley Properties', 'title': 'Construction Manager'},
    ]
    
    print("="*60)
    print("Verifying Henley Properties emails via SMTP...")
    print("="*60)
    
    results = verify_emails(henley_contacts, use_smtp=True)
    
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    
    valid = [r for r in results if r['status'] == 'valid']
    invalid = [r for r in results if r['status'] == 'invalid']
    risky = [r for r in results if r['status'] == 'risky']
    errors = [r for r in results if r['status'] == 'error']
    
    print(f"\n✅ VALID ({len(valid)}):")
    for r in valid:
        print(f"  {r['email']:40s} | {r['name']:20s} | {r['title']}")
    
    print(f"\n❌ INVALID ({len(invalid)}):")
    for r in invalid:
        print(f"  {r['email']:40s} | {r['name']:20s} | {r['detail']}")
    
    print(f"\n⚠️ RISKY ({len(risky)}):")
    for r in risky:
        print(f"  {r['email']:40s} | {r['name']:20s} | {r['detail']}")
    
    print(f"\n❗ ERRORS ({len(errors)}):")
    for r in errors:
        print(f"  {r['email']:40s} | {r['name']:20s} | {r['detail']}")
    
    # Save results
    output = {
        'company': 'Henley Properties',
        'domain': 'henley.com.au',
        'verified_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'results': results
    }
    
    with open('/home/edinsonmipc/midashboard/data/henley_verified.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to data/henley_verified.json")

if __name__ == '__main__':
    main()
