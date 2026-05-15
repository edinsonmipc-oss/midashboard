"""Find real personal contacts at construction companies using Playwright stealth."""
import asyncio
import re
import json
from playwright.async_api import async_playwright
from playwright_stealth import StealthConfig as stealth_async

async def search_bing(query):
    """Search Bing and extract results."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)
        
        try:
            url = f"https://www.bing.com/search?q={query.replace(' ', '+')}&count=30"
            print(f"Searching: {query}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            content = await page.content()
            
            # Extract search result links and snippets
            results = re.findall(
                r'<h2><a[^>]*href="([^"]+)"[^>]*>(.*?)</a></h2>',
                content, re.DOTALL
            )
            
            snippets = re.findall(
                r'<p[^>]*class="[^"]*b_lineclamp[^"]*"[^>]*>(.*?)</p>',
                content, re.DOTALL
            )
            
            people_found = []
            for i, (url, title) in enumerate(results[:15]):
                title_clean = re.sub(r'<[^>]+>', '', title).strip()
                snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ''
                
                # Look for personal names in results
                names = re.findall(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', title_clean + ' ' + snippet)
                
                entry = {
                    'title': title_clean,
                    'url': url,
                    'snippet': snippet[:200],
                    'names_found': [n for n in names if len(n) > 3 and len(n) < 40][:3]
                }
                people_found.append(entry)
                
                print(f"  {i+1}. {title_clean[:80]}")
                print(f"     {url[:80]}")
            
            return people_found
            
        except Exception as e:
            print(f"  Error: {e}")
            return []
        finally:
            await browser.close()

async def main():
    # Search queries for each company targeting construction managers in Melbourne
    queries = [
        # Lendlease specific people
        '"Lendlease" "construction manager" Melbourne linkedin',
        '"Lendlease" "project manager" "Melbourne" linkedin',
        
        # Brookfield Multiplex
        '"Multiplex" OR "Brookfield" "construction manager" Melbourne linkedin',
        '"Multiplex" "project manager" Melbourne linkedin',
        
        # John Holland
        '"John Holland" "construction manager" Melbourne linkedin',
        '"John Holland" "project manager" Melbourne linkedin',
        
        # Metricon
        '"Metricon" "construction manager" OR "project manager" Melbourne linkedin',
        
        # Other builders
        '"Henley" homes "construction manager" Melbourne linkedin',
        '"Hickory" group "project manager" Melbourne linkedin',
        '"Laing O\'Rourke" "project manager" Melbourne linkedin',
    ]
    
    all_results = {}
    
    for query in queries:
        print(f"\n{'='*60}")
        results = await search_bing(query)
        all_results[query] = results
        await asyncio.sleep(3)  # Be polite
    
    # Save all results
    with open('/home/edinsonmipc/midashboard/data/search_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n\n{'='*60}")
    print("All searches complete. Results saved to search_results.json")

if __name__ == "__main__":
    asyncio.run(main())
