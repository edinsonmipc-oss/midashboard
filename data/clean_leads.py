#!/usr/bin/env python3
"""
Clean and rebuild the leads database.
- Remove all generic role-based emails
- Deduplicate by email
- Keep only entries with contact names or clear personal emails
- Save backup, cleaned version, new pipeline file, and email patterns reference
"""

import json
import re
import shutil
import os
from collections import OrderedDict

LEADS_FILE = "/home/edinsonmipc/midashboard/data/leads.json"
BACKUP_FILE = "/home/edinsonmipc/midashboard/data/leads.json.backup"
NEW_PIPELINE_FILE = "/home/edinsonmipc/midashboard/data/leads_new_pipeline.json"
PATTERNS_FILE = "/home/edinsonmipc/midashboard/data/email_patterns.json"

# Generic role-based email prefixes to remove (lowercase)
GENERIC_PREFIXES = {
    "info", "admin", "contact", "sales", "support", "procurement",
    "suppliers", "supplier", "trades", "commercial", "property",
    "facilities", "leasing", "projects", "estimating", "community",
    "partnerships", "accounts", "bookings", "enquiries", "enquiry",
    "reception", "hello", "team", "office", "subcontractors",
    "supplychain", "customerservice", "marketing", "media", "hr",
    "careers", "jobs", "noreply", "no-reply", "mail", "webmaster",
    "postmaster", "abuse", "help", "service", "orders", "billing",
    "payments", "reservations", "newsletter", "notifications",
    "feedback", "complaints", "info", "test", "demo", "training"
}

def get_email_prefix(email):
    """Extract the local part (prefix) from an email address."""
    if not email or "@" not in email:
        return ""
    return email.split("@")[0].lower().strip()

def is_generic_role_email(email):
    """Check if email uses a generic role-based prefix."""
    prefix = get_email_prefix(email)
    if not prefix:
        return False
    
    # Check for firstname.lastname pattern (personal email)
    if re.match(r'^[a-z]+(\.[a-z]+)+$', prefix):
        # This looks like a personal email (firstname.lastname)
        return False
    
    # Check if it's a single generic word
    if prefix in GENERIC_PREFIXES:
        return True
    
    # Check for compound prefixes like "info@" or "commercial@"
    # Also check if prefix contains a generic word
    for generic in GENERIC_PREFIXES:
        if prefix == generic or prefix.startswith(generic + ".") or prefix.startswith(generic + "-"):
            return True
    
    return False

def main():
    print("=" * 60)
    print("LEADS DATABASE CLEANUP")
    print("=" * 60)
    
    # Step 1: Read the current leads.json
    print(f"\n[1] Reading {LEADS_FILE}...")
    with open(LEADS_FILE, 'r') as f:
        data = json.load(f)
    
    total_leads = data.get("total_leads", 0)
    print(f"    Original total_leads: {total_leads}")
    
    leads_by_date = data.get("leads_by_date", {})
    total_entries = sum(len(leads) for leads in leads_by_date.values())
    print(f"    Actual entries in leads_by_date: {total_entries}")
    
    # Step 2: Create backup
    print(f"\n[2] Creating backup at {BACKUP_FILE}...")
    shutil.copy2(LEADS_FILE, BACKUP_FILE)
    print(f"    Backup created successfully")
    
    # Step 3: Analyze all entries
    print(f"\n[3] Analyzing all entries...")
    all_entries_flat = []
    for batch_key, entries in leads_by_date.items():
        for entry in entries:
            all_entries_flat.append((batch_key, entry))
    
    # Classify entries
    generic_entries = []
    personal_entries = []
    seen_emails = set()
    seen_personal_emails = set()
    
    for batch_key, entry in all_entries_flat:
        email = entry.get("email", "")
        contact = entry.get("contact", "")
        prefix = get_email_prefix(email)
        
        has_contact_name = bool(contact and contact.strip())
        is_generic = is_generic_role_email(email)
        
        # Check for firstname.lastname pattern
        is_personal_pattern = bool(re.match(r'^[a-z]+(\.[a-z]+)+$', prefix))
        
        if is_personal_pattern and email not in seen_personal_emails:
            personal_entries.append((batch_key, entry))
            seen_personal_emails.add(email)
        elif has_contact_name and not is_generic and email not in seen_personal_emails:
            personal_entries.append((batch_key, entry))
            seen_personal_emails.add(email)
        else:
            if email not in seen_emails:
                generic_entries.append((batch_key, entry))
                seen_emails.add(email)
    
    print(f"    Generic role-based entries found: {len(generic_entries)}")
    print(f"    Personal entries found: {len(personal_entries)}")
    
    # List all generic emails for transparency
    print(f"\n    --- Generic role-based emails (will be removed) ---")
    for batch_key, entry in sorted(generic_entries, key=lambda x: x[1].get("email", "")):
        email = entry.get("email", "")
        company = entry.get("company", "")
        print(f"    - {email:45s} ({company})")
    
    if personal_entries:
        print(f"\n    --- Personal contacts (will be kept) ---")
        for batch_key, entry in personal_entries:
            email = entry.get("email", "")
            company = entry.get("company", "")
            contact = entry.get("contact", "")
            print(f"    - {email:45s} ({company}) contact: {contact}")
    else:
        print(f"\n    --- No personal contacts found ---")
    
    # Step 4: Rebuild leads_by_date keeping only personal entries
    print(f"\n[4] Rebuilding leads.json with personal contacts only...")
    new_leads_by_date = OrderedDict()
    
    for batch_key, entries in leads_by_date.items():
        new_entries = []
        for entry in entries:
            email = entry.get("email", "")
            contact = entry.get("contact", "")
            prefix = get_email_prefix(email)
            
            has_contact_name = bool(contact and contact.strip())
            is_personal_pattern = bool(re.match(r'^[a-z]+(\.[a-z]+)+$', prefix))
            
            if is_personal_pattern or (has_contact_name and not is_generic_role_email(email)):
                new_entries.append(entry)
        
        if new_entries:
            new_leads_by_date[batch_key] = new_entries
    
    # Update total
    new_total = sum(len(entries) for entries in new_leads_by_date.values())
    data["total_leads"] = new_total
    data["leads_by_date"] = new_leads_by_date
    
    print(f"    Entries after cleaning: {new_total}")
    
    # Step 5: Write cleaned version
    print(f"\n[5] Writing cleaned leads.json...")
    with open(LEADS_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"    Done!")
    
    # Step 6: Create empty pipeline file
    print(f"\n[6] Creating empty pipeline file at {NEW_PIPELINE_FILE}...")
    pipeline_data = {
        "updated": "2026-05-15T07:00",
        "total_leads": 0,
        "businesses": [
            "PrimeScape Construction",
            "Prime Property Maintenance"
        ],
        "leads_by_date": {}
    }
    with open(NEW_PIPELINE_FILE, 'w') as f:
        json.dump(pipeline_data, f, indent=2, ensure_ascii=False)
    print(f"    Created!")
    
    # Step 7: Create email patterns reference file
    print(f"\n[7] Creating email patterns reference at {PATTERNS_FILE}...")
    patterns = {
        "updated": "2026-05-15T07:00",
        "description": "Email patterns for construction companies - use firstname.lastname@domain format for personal contacts",
        "generic_prefixes_to_avoid": sorted(GENERIC_PREFIXES),
        "company_email_patterns": {
            "Lendlease": "firstname.lastname@lendlease.com",
            "Brookfield Multiplex": "firstname.lastname@multiplex.global",
            "John Holland": "firstname.lastname@johnholland.com.au",
            "Metricon": "firstname.lastname@metricon.com.au",
            "Henley": "firstname.lastname@henley.com.au",
            "Hickory": "firstname.lastname@hickory.com.au",
            "Laing O'Rourke": "firstname.lastname@laingorourke.com",
            "Hansen Yuncken": "firstname.lastname@hansenyuncken.com.au",
            "Downer": "firstname.lastname@downergroup.com",
            "Built": "firstname.lastname@built.com.au",
            "Burbank": "firstname.lastname@burbank.com.au",
            "AVJennings": "firstname.lastname@avjennings.com.au",
            "Boutique": "firstname.lastname@boutiquehomes.com.au",
            "Carlton": "firstname.lastname@carltonhomes.com.au",
            "Probuild": "firstname.lastname@probuild.com.au",
            "Watpac": "firstname.lastname@watpac.com.au",
            "Fletcher": "firstname.lastname@fletcher.com.au"
        }
    }
    with open(PATTERNS_FILE, 'w') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)
    print(f"    Created!")
    
    # Summary
    print("\n" + "=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print(f"  Original entries:   {total_entries}")
    print(f"  Removed (generic):  {total_entries - new_total}")
    print(f"  Kept (personal):    {new_total}")
    print(f"  Backup saved:       {BACKUP_FILE}")
    print(f"  Cleaned file:       {LEADS_FILE}")
    print(f"  Pipeline template:  {NEW_PIPELINE_FILE}")
    print(f"  Email patterns:     {PATTERNS_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
