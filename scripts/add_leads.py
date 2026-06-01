#!/usr/bin/env python3
"""Add new contacts to leads database and verify DNS MX."""
import json
import dns.resolver
import sys

with open('/home/edinsonmipc/midashboard/data/leads.json') as f:
    data = json.load(f)

new_batches = {
    "2026-05-15_hickory-group": [
        {"company": "Hickory Group", "email": "steve.stavrou@hickory.com.au", "website": "hickory.com.au", "type": "constructora", "contact": "Steve Stavrou", "title": "Strategic Procurement Director", "notes": "Toma decisiones de contratacion de subcontratistas. Fuente: hickory.com.au", "verified": "verified", "verified_reason": "MX verified - hickory.com.au via Mimecast", "contacted": "", "contact_status": "never", "sent": False},
        {"company": "Hickory Group", "email": "ben.williams@hickory.com.au", "website": "hickory.com.au", "type": "constructora", "contact": "Ben Williams", "title": "Construction Director - Victoria", "notes": "Director de construccion Victoria - contrata sub en Melbourne", "verified": "verified", "verified_reason": "MX verified - hickory.com.au via Mimecast", "contacted": "", "contact_status": "never", "sent": False},
        {"company": "Hickory Group", "email": "george.abraham@hickory.com.au", "website": "hickory.com.au", "type": "constructora", "contact": "George Abraham", "title": "Managing Director", "notes": "Managing Director", "verified": "verified", "verified_reason": "MX verified - hickory.com.au via Mimecast", "contacted": "", "contact_status": "never", "sent": False},
        {"company": "Hickory Group", "email": "michael.argyrou@hickory.com.au", "website": "hickory.com.au", "type": "constructora", "contact": "Michael Argyrou", "title": "Group CEO", "notes": "CEO", "verified": "verified", "verified_reason": "MX verified - hickory.com.au via Mimecast", "contacted": "", "contact_status": "never", "sent": False},
    ],
    "2026-05-15_hansen-yuncken": [
        {"company": "Hansen Yuncken", "email": "daniel.crawley@hansenyuncken.com.au", "website": "hansenyuncken.com.au", "type": "constructora", "contact": "Daniel Crawley", "title": "General Manager - Victoria", "notes": "GM Victoria - contrata sub en Melbourne", "verified": "verified", "verified_reason": "MX verified - hansenyuncken.com.au", "contacted": "", "contact_status": "never", "sent": False},
        {"company": "Hansen Yuncken", "email": "george.bardas@hansenyuncken.com.au", "website": "hansenyuncken.com.au", "type": "constructora", "contact": "George Bardas", "title": "CEO", "notes": "CEO", "verified": "verified", "verified_reason": "MX verified - hansenyuncken.com.au", "contacted": "", "contact_status": "never", "sent": False},
        {"company": "Hansen Yuncken", "email": "mark.rosenboom@hansenyuncken.com.au", "website": "hansenyuncken.com.au", "type": "constructora", "contact": "Mark Rosenboom", "title": "Executive General Manager", "notes": "EGM - supervisa construccion", "verified": "verified", "verified_reason": "MX verified - hansenyuncken.com.au", "contacted": "", "contact_status": "never", "sent": False},
    ],
    "2026-05-15_lendlease": [
        {"company": "Lendlease", "email": "stephanie.graham@lendlease.com", "website": "lendlease.com", "type": "constructora", "contact": "Stephanie Graham", "title": "CEO, Construction", "notes": "CEO de Construction. Fuente: lendlease.com", "verified": "unverified", "verified_reason": "Domain MX needs check", "contacted": "", "contact_status": "never", "sent": False},
    ],
    "2026-05-15_laing-orourke": [
        {"company": "Laing O'Rourke", "email": "cathal.orourke@laingorourke.com", "website": "laingorourke.com", "type": "constructora", "contact": "Cathal O'Rourke", "title": "Group CEO", "notes": "CEO. Fuente: laingorourke.com", "verified": "unverified", "verified_reason": "Domain MX needs check", "contacted": "", "contact_status": "never", "sent": False},
    ],
    "2026-05-15_downer-group": [
        {"company": "Downer Group", "email": "doug.moss@downergroup.com", "website": "downergroup.com", "type": "constructora", "contact": "Doug Moss", "title": "COO Transport & Infrastructure", "notes": "COO Transport - contrata sub para infraestructura", "verified": "unverified", "verified_reason": "Domain MX needs check", "contacted": "", "contact_status": "never", "sent": False},
        {"company": "Downer Group", "email": "peter.tompkins@downergroup.com", "website": "downergroup.com", "type": "constructora", "contact": "Peter Tompkins", "title": "MD & CEO", "notes": "CEO", "verified": "unverified", "verified_reason": "Domain MX needs check", "contacted": "", "contact_status": "never", "sent": False},
    ],
}

data["leads_by_date"].update(new_batches)
data["total_leads"] = sum(len(b) for b in data["leads_by_date"].values())

with open('/home/edinsonmipc/midashboard/data/leads.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Total leads now: {data['total_leads']}")
print()
print("Companies in database:")
for batch_name, batch in data["leads_by_date"].items():
    company = batch[0]["company"]
    contacts = len(batch)
    statuses = set(l.get("verified","?") for l in batch)
    print(f"  [{', '.join(statuses)}] {company}: {contacts} contacts")

# Verify DNS MX
print("\nVerifying DNS MX for unverified domains...")
unverified_emails = []
for batch in data["leads_by_date"].values():
    for lead in batch:
        if lead.get("verified") == "unverified":
            unverified_emails.append(lead["email"])

for email in unverified_emails:
    domain = email.split("@")[1]
    try:
        mx = dns.resolver.resolve(domain, "MX")
        print(f"  ✅ {email:50s}  MX OK ({len(mx)} servers)")
    except Exception as e:
        print(f"  ❌ {email:50s}  NO MX: {e}")
