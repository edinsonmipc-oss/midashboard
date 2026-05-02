#!/usr/bin/env python3
"""leadgen.py — Genera 10 leads de builders/constructoras/real estate en Melbourne
   y los agrega al dashboard. Se ejecuta 2 veces al día via cron."""

import json, os, random, sys
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

# Base de datos de empresas reales (se expandirá con el tiempo)
LEADS_DB = [
    # Builders / Construction Companies
    {"company": "Mirvac", "email": f"info@mirvac.com", "website": "mirvac.com", "type": "real_estate"},
    {"company": "Lendlease", "email": f"suppliers@lendlease.com", "website": "lendlease.com", "type": "constructora"},
    {"company": "Frasers Property", "email": f"procurement@frasersproperty.com.au", "website": "frasersproperty.com.au", "type": "real_estate"},
    {"company": "Stockland", "email": f"community@stockland.com.au", "website": "stockland.com.au", "type": "real_estate"},
    {"company": "Metricon", "email": f"trades@metricon.com.au", "website": "metricon.com.au", "type": "builder"},
    {"company": "Porter Davis", "email": f"supplier@porterdavis.com.au", "website": "porterdavis.com.au", "type": "builder"},
    {"company": "Hickory Group", "email": f"projects@hickory.com.au", "website": "hickory.com.au", "type": "constructora"},
    {"company": "Cbus Property", "email": f"info@cbusproperty.com.au", "website": "cbusproperty.com.au", "type": "real_estate"},
    {"company": "ISPT", "email": f"property@ispt.com.au", "website": "ispt.com.au", "type": "real_estate"},
    {"company": "Dexus", "email": f"leasing@dexus.com", "website": "dexus.com", "type": "real_estate"},
    {"company": "GPT Group", "email": f"info@gpt.com.au", "website": "gpt.com.au", "type": "real_estate"},
    {"company": "Charter Hall", "email": f"leasing@charterhall.com.au", "website": "charterhall.com.au", "type": "real_estate"},
    {"company": "Goodman Group", "email": f"property@goodman.com", "website": "goodman.com", "type": "real_estate"},
    {"company": "Mirvac", "email": f"partnerships@mirvac.com", "website": "mirvac.com", "type": "real_estate"},
    {"company": "AVJennings", "email": f"info@avjennings.com.au", "website": "avjennings.com.au", "type": "builder"},
    {"company": "Simonds Homes", "email": f"trades@simonds.com.au", "website": "simonds.com.au", "type": "builder"},
    {"company": "Carlton Homes", "email": f"info@carltonhomes.com.au", "website": "carltonhomes.com.au", "type": "builder"},
    {"company": "Burbank Homes", "email": f"supplier@burbank.com.au", "website": "burbank.com.au", "type": "builder"},
    {"company": "Henley Homes", "email": f"trades@henley.com.au", "website": "henley.com.au", "type": "builder"},
    {"company": "Boutique Homes", "email": f"info@boutiquehomes.com.au", "website": "boutiquehomes.com.au", "type": "builder"},
    {"company": "Kane Constructions", "email": f"projects@kane.com.au", "website": "kane.com.au", "type": "constructora"},
    {"company": "Built", "email": f"enquiries@built.com.au", "website": "built.com.au", "type": "constructora"},
    {"company": "Hansen Yuncken", "email": f"info@hansenyuncken.com.au", "website": "hansenyuncken.com.au", "type": "constructora"},
    {"company": "Watpac", "email": f"projects@watpac.com.au", "website": "watpac.com.au", "type": "constructora"},
    {"company": "Probuild", "email": f"estimating@probuild.com.au", "website": "probuild.com.au", "type": "constructora"},
    {"company": "Multiplex", "email": f"subcontractors@multiplex.com", "website": "multiplex.global", "type": "constructora"},
    {"company": "Brookfield Multiplex", "email": f"procurement@brookfieldmultiplex.com", "website": "brookfieldmultiplex.com", "type": "constructora"},
    {"company": "John Holland", "email": f"suppliers@johnholland.com.au", "website": "johnholland.com.au", "type": "constructora"},
    {"company": "Laing O'Rourke", "email": f"supplychain@laingorourke.com.au", "website": "laingorourke.com.au", "type": "constructora"},
    {"company": "Downer Group", "email": f"procurement@downergroup.com", "website": "downergroup.com", "type": "constructora"},
    # Real Estate Agencies
    {"company": "Ray White", "email": f"commercial@raywhite.com", "website": "raywhite.com", "type": "real_estate"},
    {"company": "Barry Plant", "email": f"property@barryplant.com.au", "website": "barryplant.com.au", "type": "real_estate"},
    {"company": "Jellis Craig", "email": f"commercial@jelliscraig.com.au", "website": "jelliscraig.com.au", "type": "real_estate"},
    {"company": "Marshall White", "email": f"projects@marshallwhite.com.au", "website": "marshallwhite.com.au", "type": "real_estate"},
    {"company": "Kay & Burton", "email": f"commercial@kayburton.com.au", "website": "kayburton.com.au", "type": "real_estate"},
    {"company": "Fletchers Real Estate", "email": f"property@fletcher.com.au", "website": "fletcher.com.au", "type": "real_estate"},
    {"company": "Collins Simms", "email": f"info@collinssimms.com.au", "website": "collinssimms.com.au", "type": "real_estate"},
    {"company": "Hockingstuart", "email": f"commercial@hockingstuart.com.au", "website": "hockingstuart.com.au", "type": "real_estate"},
    {"company": "Nelson Alexander", "email": f"property@nelsonalexander.com.au", "website": "nelsonalexander.com.au", "type": "real_estate"},
    {"company": "McGrath Estate Agents", "email": f"commercial@mcgrath.com.au", "website": "mcgrath.com.au", "type": "real_estate"},
    {"company": "LJ Hooker", "email": f"commercial@ljhooker.com", "website": "ljhooker.com", "type": "real_estate"},
    {"company": "Raine & Horne", "email": f"commercial@rainehorne.com.au", "website": "rainehorne.com.au", "type": "real_estate"},
    {"company": "Century 21", "email": f"commercial@century21.com.au", "website": "century21.com.au", "type": "real_estate"},
    {"company": "First National Real Estate", "email": f"commercial@fnre.com.au", "website": "fnre.com.au", "type": "real_estate"},
    {"company": "PRDnationwide", "email": f"commercial@prd.com.au", "website": "prd.com.au", "type": "real_estate"},
    # Property / Strata / Facilities Management
    {"company": "CBRE Australia", "email": f"facilities@cbre.com.au", "website": "cbre.com.au", "type": "property_mgmt"},
    {"company": "JLL Australia", "email": f"property@jll.com.au", "website": "jll.com.au", "type": "property_mgmt"},
    {"company": "Colliers International", "email": f"property@colliers.com.au", "website": "colliers.com.au", "type": "property_mgmt"},
    {"company": "Savills Australia", "email": f"property@savills.com.au", "website": "savills.com.au", "type": "property_mgmt"},
    {"company": "Knight Frank Australia", "email": f"property@knightfrank.com.au", "website": "knightfrank.com.au", "type": "property_mgmt"},
    {"company": "Cushman & Wakefield", "email": f"property@cushwake.com", "website": "cushwake.com", "type": "property_mgmt"},
    {"company": "PICA Group", "email": f"info@picagroup.com.au", "website": "picagroup.com.au", "type": "strata"},
    {"company": "Strata Title Management", "email": f"info@stratatitle.com.au", "website": "stratatitle.com.au", "type": "strata"},
    {"company": "ACE Body Corporate", "email": f"info@acebodycorporate.com.au", "website": "acebodycorporate.com.au", "type": "strata"},
]

TYPE_EMOJI = {
    "constructora": "🏗️",
    "builder": "🔨",
    "real_estate": "🏢",
    "property_mgmt": "🏢",
    "strata": "🏠",
    "construction_supply": "🔩",
    "other": "📌",
}

NOTES = {
    "constructora": ["Grandes proyectos de construcción en Melbourne", "Contratistas principales nivel 1", "Proyectos comerciales y residenciales", "Buscan subcontratistas calificados"],
    "builder": ["Constructora de viviendas en Melbourne", "Volumen alto de proyectos", "Necesitan tradies para subcontratos"],
    "real_estate": ["Gestionan propiedades comerciales", "Necesitan mantenimiento regular", "Portfolio grande en Melbourne"],
    "property_mgmt": ["Administran propiedades comerciales y residenciales", "Contratan servicios de mantenimiento", "Multiples propiedades en su cartera"],
    "strata": ["Administran edificios y propiedades", "Buscan contractors para mantenimiento", "Necesitan servicios regulares"],
    "construction_supply": ["Proveen materiales de construcción", "Posible partnership estratégico"],
    "other": ["Posible lead para servicios de construcción", "Contactar para ofrecer servicios"],
}

def pick_leads(count=10):
    """Pick `count` unique leads from the DB using reservoir sampling."""
    selected = set()
    results = []
    # Shuffle and pick unique companies
    pool = list(LEADS_DB)
    random.shuffle(pool)
    used_companies = set()
    for item in pool:
        if item["company"] not in used_companies:
            used_companies.add(item["company"])
            results.append(item)
            if len(results) >= count:
                break
    # If not enough, re-shuffle
    while len(results) < count:
        extra = random.choice(pool)
        if extra["company"] not in used_companies:
            used_companies.add(extra["company"])
            results.append(extra)
    return results[:count]

def get_notes(typ):
    pool = NOTES.get(typ, NOTES["other"])
    return random.choice(pool)

def main():
    leads_file = os.path.join(DIR, "data", "leads.json")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Load existing leads
    if os.path.exists(leads_file):
        with open(leads_file) as f:
            data = json.load(f)
    else:
        data = {"updated": today, "total_leads": 0, "businesses": ["PrimeScape Construction", "Prime Property Maintenance", "Antonio Paving"], "leads_by_date": {}}
    
    # Check if we already generated today
    if today in data["leads_by_date"]:
        print(f"📋 Leads ya generados hoy ({today}): {len(data['leads_by_date'][today])} leads")
        # Still rotate - remove oldest and add new ones
        # Actually, just add a new batch with a unique key
    
    # Generate 10 new leads
    new_leads = pick_leads(10)
    
    # Format them
    formatted = []
    for l in new_leads:
        formatted.append({
            "company": l["company"],
            "email": l["email"],
            "website": l["website"],
            "type": l["type"],
            "contact": "",
            "notes": get_notes(l["type"])
        })
    
    # Store with timestamp
    batch_key = f"{today}_batch{len(data['leads_by_date'])}"
    data["leads_by_date"][batch_key] = formatted
    
    # Keep only last 7 batches for cleanliness
    keys = sorted(data["leads_by_date"].keys(), reverse=True)
    for k in keys[14:]:  # Keep last 14 batches (~1 week at 2/day)
        del data["leads_by_date"][k]
    
    # Update stats
    total = sum(len(v) for v in data["leads_by_date"].values())
    data["total_leads"] = total
    data["updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M")
    
    # Save
    with open(leads_file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(formatted)} leads generados para {today}")
    for l in formatted:
        emoji = TYPE_EMOJI.get(l["type"], "📌")
        print(f"  {emoji} {l['company']:30s} → {l['email']:35s} ({l['type']})")
    print(f"\n📊 Total acumulado: {total} leads")
    return True

if __name__ == "__main__":
    main()
