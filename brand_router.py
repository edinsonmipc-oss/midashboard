#!/usr/bin/env python3
"""
brand_router.py — BRAND ROUTER: classifies leads and returns correct brand config.

Rules:
  builders, developers, constructors, architects
    → Antonio PrimeScape Construction (antoniopaving.com)
    → Premium paving, outdoor construction

  real estate, property management, strata, facilities, schools, aged care
    → Prime Property Maintenance (primepropertymaintenance.au)
    → Reliable maintenance, handyman, facilities

  NEVER mix brands. Classify the lead BEFORE sending.
"""

# ── Brand Definitions ──────────────────────────────────────────────
BRANDS = {
    "primescape": {
        "id": "primescape",
        "name": "Antonio PrimeScape Construction",
        "website": "antoniopaving.com",
        "instagram": "instagram.com/antonioprimescape",
        "phone": "0406 170 544",
        "address": "10 Elwood St, Notting Hill VIC 3168",
        "email_from": "antonioprimemaintenance@gmail.com",
        "positioning": "Premium paving & outdoor construction specialist",
        "tone": "premium, construction-focused, skilled contractor",
        "services": [
            "brick paving",
            "bluestone paving",
            "porcelain paving",
            "driveways & patios",
            "retaining walls",
            "commercial outdoor construction",
        ],
        "signature": (
            "Antonio PrimeScape Construction\n"
            "Premium Paving & Outdoor Construction\n"
            "antoniopaving.com | instagram.com/antonioprimescape\n"
            "0406 170 544 | 10 Elwood St, Notting Hill VIC 3168"
        ),
        "templates": {
            "builder": {
                "subject": "Premium paving contractor — Melbourne South-East",
                "body": """Hi {first_name},

I'm Antonio, owner of PrimeScape Construction in Notting Hill.

We specialise in premium outdoor construction — brick paving, bluestone, porcelain, driveways, patios, and retaining walls for both residential and commercial projects across Melbourne's south-east.

We have capacity for subcontract paving works this quarter and would welcome the opportunity to discuss your upcoming project pipeline.

Would you be open to a brief conversation about how we can add value to your next development?

Cheers,
Antonio
Antonio PrimeScape Construction
antoniopaving.com | instagram.com/antonioprimescape
0406 170 544"""
            },
            "developer": {
                "subject": "Subcontract paving partner — Melbourne South-East",
                "body": """Hi {first_name},

I'm writing from PrimeScape Construction, a premium paving contractor based in Notting Hill.

We deliver high-quality outdoor construction for commercial and residential developments — brick paving, bluestone finishes, porcelain surfaces, driveways, and retaining walls.

We currently have crew availability and would welcome the opportunity to quote on your upcoming projects.

Keen to discuss how we can support your next development?

Cheers,
Antonio
Antonio PrimeScape Construction
antoniopaving.com | instagram.com/antonioprimescape
0406 170 544"""
            },
        },
    },

    "primeproperty": {
        "id": "primeproperty",
        "name": "Prime Property Maintenance",
        "website": "primepropertymaintenance.au",
        "instagram": "instagram.com/primepropertymaintenance",
        "phone": "0468 166 249",
        "address": "10 Elwood St, Notting Hill VIC 3168",
        "email_from": "antonioprimemaintenance@gmail.com",
        "positioning": "Reliable property maintenance & facilities services",
        "tone": "reliable, clean, maintenance-focused, responsive",
        "services": [
            "property maintenance",
            "handyman services",
            "body corporate maintenance",
            "commercial facilities maintenance",
            "real estate support",
            "school & aged care maintenance",
        ],
        "signature": (
            "Prime Property Maintenance\n"
            "Reliable Maintenance & Property Services\n"
            "primepropertymaintenance.au\n"
            "0468 166 249 | 10 Elwood St, Notting Hill VIC 3168"
        ),
        "templates": {
            "real_estate": {
                "subject": "Property maintenance support — Melbourne South-East",
                "body": """Hi {first_name},

I'm writing from Prime Property Maintenance, based in Notting Hill.

We provide reliable maintenance services for real estate agencies and property managers across Melbourne's south-east — from routine repairs to emergency call-outs and end-of-lease make-readies.

We help keep properties tenant-ready and reduce downtime between leases. All work is fully insured and we report to agency specifications.

Would you be open to a quick chat about becoming your go-to maintenance contact?

Cheers,
Antonio
Prime Property Maintenance
primepropertymaintenance.au
0468 166 249"""
            },
            "strata": {
                "subject": "Maintenance contractor for body corporate — Melbourne",
                "body": """Hi {first_name},

I'm writing from Prime Property Maintenance in Notting Hill.

We provide responsive maintenance services for body corporate and strata properties — ongoing upkeep, repairs, and emergency call-outs for common areas and managed properties across Melbourne's south-east.

We work to committee specifications, provide written reports, and are fully insured.

Would you be open to a brief discussion about supporting your managed properties?

Cheers,
Antonio
Prime Property Maintenance
primepropertymaintenance.au
0468 166 249"""
            },
            "facilities": {
                "subject": "Commercial maintenance contractor — Melbourne",
                "body": """Hi {first_name},

I'm writing from Prime Property Maintenance in Notting Hill.

We provide ongoing facilities maintenance for commercial properties, schools, and aged care facilities — repairs, painting, guttering, fencing, and general upkeep across Melbourne's south-east.

We work with facilities managers to deliver reliable, schedule-compliant maintenance with minimal disruption.

Would you be open to a conversation about your maintenance requirements?

Cheers,
Antonio
Prime Property Maintenance
primepropertymaintenance.au
0468 166 249"""
            },
        },
    },
}


# ── Lead Type → Brand Mapping ──────────────────────────────────────
BRAND_MAP = {
    # Builder/development → PrimeScape
    "builder": "primescape",
    "constructora": "primescape",
    "developer": "primescape",
    "architect": "primescape",
    "commercial_paving": "primescape",
    "landscaping": "primescape",
    "construction": "primescape",
    # Property/facilities → Prime Property
    "property_mgmt": "primeproperty",
    "real_estate": "primeproperty",
    "strata": "primeproperty",
    "facilities": "primeproperty",
    "body_corporate": "primeproperty",
    "school": "primeproperty",
    "aged_care": "primeproperty",
    "commercial_maintenance": "primeproperty",
    "re_agency": "primeproperty",
    "facilities_mgr": "primeproperty",
    "council": "primeproperty",
}

# Fallback template for each brand
FALLBACK_TEMPLATES = {
    "primescape": "builder",
    "primeproperty": "real_estate",
}


def classify_lead(lead):
    """
    Classify a lead and return the correct brand config with selected template.

    Input: lead dict with at minimum {'type': ..., 'contact': ..., 'company': ...}
    Output: {
        'brand': brand_id,
        'brand_config': {...},
        'template': {...},
        'template_key': str,
    }

    The lead's 'type' field determines the brand.
    """
    lead_type = (lead.get("type") or "").strip().lower()
    brand_id = BRAND_MAP.get(lead_type)

    if not brand_id:
        # Fallback: try to infer from company name or notes
        company = (lead.get("company") or "").lower()
        notes = (lead.get("notes") or "").lower()
        combined = f"{company} {notes}"

        # Keywords favoring PrimeScape
        if any(kw in combined for kw in ["builder", "construction", "develop", "paving", "architect", "civil"]):
            brand_id = "primescape"
        # Keywords favoring Prime Property
        elif any(kw in combined for kw in ["real estate", "property", "strata", "re agency", "facilities", "management",
                                            "pm", "rental", "lease", "council", "school", "aged care",
                                            "maintenance", "body corporate", "commercial maintenance"]):
            brand_id = "primeproperty"
        else:
            # Default: PrimeScape for known builder-adjacent names, Prime Property for others
            if lead_type in ("unknown", ""):
                brand_id = "primeproperty"  # Conservative default
            else:
                brand_id = "primescape"

    brand_config = BRANDS[brand_id]

    # Select template
    template_key = FALLBACK_TEMPLATES[brand_id]
    # Try to find a template matching the lead type more closely
    if lead_type and lead_type in brand_config["templates"]:
        template_key = lead_type
    elif lead_type == "constructora":
        template_key = "builder"
    elif lead_type == "property_mgmt":
        template_key = "real_estate"

    template = brand_config["templates"].get(template_key, brand_config["templates"][FALLBACK_TEMPLATES[brand_id]])

    return {
        "brand": brand_id,
        "brand_config": brand_config,
        "template": template,
        "template_key": template_key,
    }


def get_first_name(contact_name):
    """Extract first name from full name."""
    if not contact_name:
        return "there"
    return contact_name.split()[0].strip()


def render_email(lead, brand_router_result=None):
    """
    Render a fully formed email for a lead.
    If brand_router_result is None, classifies the lead first.

    Returns: {
        'to_email': str,
        'subject': str,
        'body': str,  (full text with signature)
        'brand': str,
        'brand_name': str,
        'from_email': str,
        'from_name': str,
    }
    """
    if brand_router_result is None:
        brand_router_result = classify_lead(lead)

    brand_config = brand_router_result["brand_config"]
    template = brand_router_result["template"]

    first_name = get_first_name(lead.get("contact", ""))
    company = lead.get("company", "")

    subject = template["subject"]
    body = template["body"].format(first_name=first_name, company=company)

    # Add signature
    full_body = f"{body}\n\n{brand_config['signature']}"

    return {
        "to_email": lead.get("email", ""),
        "subject": subject,
        "body": full_body,
        "brand": brand_router_result["brand"],
        "brand_name": brand_config["name"],
        "from_email": brand_config["email_from"],
        "from_name": brand_config["name"],
    }


# ── CLI Test Interface ────────────────────────────────────────────
def test_classifications(leads_file="/home/edinsonmipc/midashboard/data/leads.json"):
    """Test classification on all leads in the file."""
    import json, os
    if not os.path.exists(leads_file):
        print("No leads file found")
        return

    with open(leads_file) as f:
        data = json.load(f)

    results = {"primescape": 0, "primeproperty": 0, "unsent_primescape": 0, "unsent_primeproperty": 0}
    print(f"\n{'='*80}")
    print(f"📊 BRAND CLASSIFICATION TEST — {data.get('total_leads', '?')} leads")
    print(f"{'='*80}")

    for batch_key in sorted(data.get("leads_by_date", {}).keys()):
        for lead in data["leads_by_date"][batch_key]:
            email = lead.get("email", "")
            if not email:
                continue

            lead_type = lead.get("type", "unknown")
            brand_result = classify_lead(lead)
            brand_id = brand_result["brand"]
            brand_name = brand_result["brand_config"]["name"]
            template_key = brand_result["template_key"]

            results[brand_id] += 1
            if not lead.get("sent"):
                results[f"unsent_{brand_id}"] += 1

            sent_marker = "✅ SENT" if lead.get("sent") else "📨 PENDING"
            print(f"{sent_marker:12s} | {brand_id.upper():15s} | {email:40s} | {lead_type:15s} | {brand_name}")

    print(f"\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"   PrimeScape Construction:   {results['primescape']} leads ({results['unsent_primescape']} unsent)")
    print(f"   Prime Property Maintenance: {results['primeproperty']} leads ({results['unsent_primeproperty']} unsent)")
    print(f"{'='*80}")

    return results


def render_sample(lead):
    """Render a sample email for a lead (for testing)."""
    result = classify_lead(lead)
    email = render_email(lead, result)
    print(f"\n{'='*80}")
    print(f"SAMPLE — {'TO: ' + email['to_email']}")
    print(f"FROM: {email['from_name']} <{email['from_email']}>")
    print(f"SUBJECT: {email['subject']}")
    print(f"{'='*80}")
    print(email["body"])
    print(f"{'='*80}")
    return email


if __name__ == "__main__":
    import sys

    if "--sample" in sys.argv:
        # Show a sample email for each lead type
        leads_file = "/home/edinsonmipc/midashboard/data/leads.json"
        import json, os
        with open(leads_file) as f:
            data = json.load(f)

        lead_types_seen = set()
        for batch_key in sorted(data.get("leads_by_date", {}).keys()):
            for lead in data["leads_by_date"][batch_key]:
                lt = lead.get("type", "unknown")
                if lt not in lead_types_seen and lead.get("email"):
                    lead_types_seen.add(lt)
                    render_sample(lead)
                    print()
    else:
        test_classifications()
