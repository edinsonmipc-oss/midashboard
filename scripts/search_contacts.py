"""Find real personal contacts at construction companies using Playwright."""
import asyncio
import re
import json
from playwright.async_api import async_playwright

async def search_google_via_bing(search_terms):
    """Search for people at construction companies."""
    all_people = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        
        for company, terms in search_terms.items():
            print(f"\n{'='*60}")
            print(f"  {company}")
            print(f"{'='*60}")
            all_people[company] = {"names": set(), "urls": [], "emails": []}
            
            for term in terms:
                page = await context.new_page()
                try:
                    q = term.replace(' ', '+').replace("'", '%27')
                    url = f"https://www.bing.com/search?q={q}"
                    print(f"\n  Search: {term}")
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(2)
                    
                    # Get the page text content
                    content = await page.content()
                    
                    # Extract all links
                    links = await page.evaluate("""() => {
                        const results = [];
                        const items = document.querySelectorAll('h2 a, .b_algo h2 a');
                        items.forEach(a => {
                            results.push({
                                url: a.href,
                                title: a.textContent.trim()
                            });
                        });
                        return results;
                    }""")
                    
                    # Extract snippets
                    snippets = await page.evaluate("""() => {
                        const results = [];
                        const items = document.querySelectorAll('.b_caption p');
                        items.forEach(p => results.push(p.textContent.trim()));
                        return results;
                    }""")
                    
                    for i, link in enumerate(links[:10]):
                        title = link['title']
                        url = link['url']
                        snippet = snippets[i] if i < len(snippets) else ''
                        
                        all_people[company]["urls"].append({"url": url, "title": title})
                        
                        # Extract potential names from title and snippet
                        names = re.findall(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', f"{title} {snippet}")
                        for n in names:
                            if len(n) > 4 and len(n) < 40 and not any(
                                x in n.lower() for x in ['bing', 'google', 'search', 'result', 'page', 'website',
                                                       'home', 'about', 'contact', 'australia', 'melbourne',
                                                       'linkedin', 'facebook', 'twitter', 'youtube', 'instagram',
                                                       'cookie', 'policy', 'terms', 'privacy', 'copyright',
                                                       'lendlease', 'multiplex', 'john holland', 'metricon',
                                                       'henley', 'hickory', 'hansen yuncken', 'downer', 'built',
                                                       'burbank', 'avjennings', 'carlton', 'boutique']
                            ):
                                all_people[company]["names"].add(n)
                    
                    print(f"    Found {len(links)} results, {len(all_people[company]['names'])} potential names")
                    
                except Exception as e:
                    print(f"    Error: {e}")
                finally:
                    await page.close()
                    await asyncio.sleep(2)
        
        await browser.close()
    
    # Convert sets to lists for JSON
    for company in all_people:
        all_people[company]["names"] = list(all_people[company]["names"])
    
    return all_people

async def main():
    # Search queries for each company: targeting construction managers, project managers, site managers
    search_terms = {
        "Lendlease": [
            '"Lendlease" "construction" Melbourne "director" OR "manager" linkedin',
            '"Lendlease" Melbourne site:"linkedin.com/in/" construction',
            '"Lendlease" Melbourne "project manager" email OR contact',
        ],
        "Brookfield Multiplex": [
            '"Multiplex" Melbourne "construction manager" linkedin',
            '"Brookfield Multiplex" Melbourne "project director" linkedin',
        ],
        "John Holland": [
            '"John Holland" Melbourne "construction manager" OR "project manager" linkedin',
            '"John Holland" Melbourne site:linkedin.com/in/ construction',
        ],
        "Metricon": [
            '"Metricon" Melbourne "construction manager" OR "site manager" linkedin',
        ],
        "Henley Homes": [
            '"Henley" "construction manager" Melbourne linkedin',
        ],
        "Hickory Group": [
            '"Hickory" Melbourne "project manager" construction linkedin',
        ],
        "Laing O\'Rourke": [
            '"Laing O\'Rourke" Melbourne "project manager" OR "construction manager" linkedin',
        ],
        "Hansen Yuncken": [
            '"Hansen Yuncken" Melbourne "project manager" linkedin',
        ],
        "Downer Group": [
            '"Downer" Melbourne "project manager" construction linkedin',
        ],
        "Built": [
            '"Built" construction Melbourne "project manager" OR "construction manager" linkedin',
        ],
    }
    
    results = await search_google_via_bing(search_terms)
    
    # Save results
    with open('/home/edinsonmipc/midashboard/data/search_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"\n\n{'='*60}")
    print("SUMMARY - POTENTIAL CONTACTS FOUND")
    print(f"{'='*60}")
    for company, data in results.items():
        print(f"\n{company}:")
        print(f"  Names found: {len(data['names'])}")
        if data['names']:
            for n in data['names'][:5]:
                print(f"    - {n}")
        print(f"  URLs: {len(data['urls'])}")

if __name__ == "__main__":
    asyncio.run(main())
