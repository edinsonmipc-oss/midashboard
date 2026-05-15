"""Find real personal contacts at construction companies in Melbourne."""
import cloudscraper
import re
import json

scraper = cloudscraper.create_scraper()

companies = {
    "Lendlease": {
        "website": "lendlease.com",
        "urls": [
            "https://www.lendlease.com/au/what-we-do/construction/",
            "https://www.lendlease.com/au/about-us/leadership/",
        ]
    },
    "Brookfield Multiplex": {
        "website": "multiplex.global",
        "urls": [
            "https://www.multiplex.global/about-us/our-people/",
            "https://www.multiplex.global/contact-us/",
        ]
    },
    "John Holland": {
        "website": "johnholland.com.au",
        "urls": [
            "https://www.johnholland.com.au/about-us/our-people/",
            "https://www.johnholland.com.au/contact-us/",
        ]
    },
    "Metricon": {
        "website": "metricon.com.au",
        "urls": [
            "https://www.metricon.com.au/about-us/our-team",
            "https://www.metricon.com.au/contact-us",
        ]
    },
    "Henley Homes": {
        "website": "henley.com.au",
        "urls": [
            "https://www.henley.com.au/about-us",
            "https://www.henley.com.au/contact-us",
        ]
    },
    "Hickory Group": {
        "website": "hickory.com.au",
        "urls": [
            "https://hickory.com.au/about/",
            "https://hickory.com.au/contact/",
        ]
    },
    "Laing O'Rourke": {
        "website": "laingorourke.com",
        "urls": [
            "https://www.laingorourke.com/people/",
        ]
    },
    "Hansen Yuncken": {
        "website": "hansenyuncken.com.au",
        "urls": [
            "https://www.hansenyuncken.com.au/about-us/people/",
        ]
    },
    "Downer Group": {
        "website": "downergroup.com",
        "urls": [
            "https://www.downergroup.com/about-us/our-leadership",
        ]
    },
    "Built": {
        "website": "built.com.au",
        "urls": [
            "https://www.built.com.au/about/leadership/",
        ]
    }
}

results = {}

for company, info in companies.items():
    print(f"\n{'='*60}")
    print(f"  {company}")
    print(f"{'='*60}")
    results[company] = {"emails": [], "names": []}
    
    for url in info["urls"]:
        try:
            r = scraper.get(url, timeout=15)
            print(f"  URL: {url}")
            print(f"  Status: {r.status_code}")
            
            if r.status_code == 200:
                text = r.text[:100000]  # First 100K chars
                
                # Find email addresses
                emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
                # Filter out generic/system emails
                generic = {'info', 'admin', 'contact', 'sales', 'support', 'noreply',
                          'procurement', 'suppliers', 'trades', 'commercial', 'property',
                          'facilities', 'leasing', 'projects', 'estimating', 'community',
                          'accounts', 'bookings', 'enquiries', 'reception', 'hello', 'team',
                          'office', 'enquiry', 'marketing', 'media', 'careers', 'jobs',
                          'hr', 'privacy', 'webmaster', 'help', 'service', 'mail'}
                real_emails = []
                for e in emails:
                    prefix = e.split('@')[0].lower()
                    if prefix not in generic and '.' in prefix and not prefix.startswith('@'):
                        real_emails.append(e)
                
                if real_emails:
                    print(f"  Personal emails found: {len(real_emails)}")
                    for e in real_emails[:10]:
                        print(f"    - {e}")
                        results[company]["emails"].append(e)
                
                # Find names with job titles (construction related)
                name_patterns = [
                    r'([A-Z][a-z]+ [A-Z][a-z]+)[^.]{0,100}(?:Construction|Project Director|Project Manager|Site Manager|Build)',
                    r'(?:Construction|Project Director|Project Manager|Site Manager)[^.]{0,100}([A-Z][a-z]+ [A-Z][a-z]+)',
                ]
                for pat in name_patterns:
                    matches = re.findall(pat, text)
                    for m in matches[:5]:
                        name = m.strip()
                        if len(name.split()) >= 2 and not any(x in name.lower() for x in ['cookie', 'policy', 'privacy', 'copyright', 'all rights']):
                            print(f"    Potential name: {name}")
                            results[company]["names"].append(name)
                
        except Exception as e:
            print(f"  Error: {e}")
    
    if not results[company]["emails"] and not results[company]["names"]:
        print(f"  No contacts found directly. Will need alternative research.")

# Save results
with open('/home/edinsonmipc/midashboard/data/contact_research.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*60}")
print("Results saved to contact_research.json")
print(f"{'='*60}")
