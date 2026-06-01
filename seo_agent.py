#!/usr/bin/env python3
"""
seo_agent.py — Auditoría SEO automática para antoniopaving.com y primepropertymaintenance.au.

Escanea:
  - HTTP status de todas las páginas
  - Meta descriptions faltantes
  - Tags title
  - Keywords objetivo en contenido
  - Sugiere nuevas páginas de contenido

Uso:
  python3 seo_agent.py                    # Auditoría completa
  python3 seo_agent.py --quick            # Solo HTTP + sitemap
  python3 seo_agent.py --keywords         # Solo análisis de keywords
  python3 seo_agent.py --content          # Genera sugerencias de contenido
  python3 seo_agent.py --report           # Muestra último reporte guardado
"""

import json, os, sys, re, urllib.request, urllib.error, urllib.parse
from datetime import datetime
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIR, "data")
LOG_DIR = os.path.join(DIR, "..", "business", "automations", "logs")
SEO_REPORT_FILE = os.path.join(DATA_DIR, "seo_report.json")
HEALTH_FILE = os.path.join(DATA_DIR, "health.json")

# ── Site Configuration ───────────────────────────────────────────
SITES = {
    "antoniopaving": {
        "url": "https://antoniopaving.com",
        "name": "Antonio Paving",
        "keywords": [
            "paving melbourne", "driveway paving", "exposed aggregate",
            "permeable paving", "concrete driveway", "paving contractors melbourne",
            "brick paving melbourne", "asphalt driveway", "crazy paving melbourne",
            "paving services melbourne"
        ],
    },
    "primeproperty": {
        "url": "https://primepropertymaintenance.au",
        "name": "Prime Property Maintenance",
        "keywords": [
            "decking melbourne", "fence installation", "gutter cleaning melbourne",
            "pressure washing melbourne", "lawn mowing melbourne",
            "handyman melbourne", "property maintenance melbourne",
            "deck builders melbourne", "fencing contractors melbourne",
            "strata maintenance melbourne"
        ],
    },
}

MELBOURNE_SUBURBS = [
    "South Yarra", "Richmond", "Carlton", "Fitzroy", "Brunswick",
    "Footscray", "St Kilda", "Prahran", "Hawthorn", "Kew",
    "Doncaster", "Box Hill", "Glen Waverley", "Dandenong", "Frankston",
    "Werribee", "Sunshine", "Essendon", "Moonee Ponds", "Camberwell",
    "Malvern", "Toorak", "Brighton", "Sandringham", "Elwood",
]

# ── HTML Parser ──────────────────────────────────────────────────
class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.meta_keywords = ""
        self.h1_tags = []
        self.h2_tags = []
        self._in_title = False
        self._in_h1 = False
        self._in_h2 = False
        self.text_content = []
        self.canonical = ""
        self.word_count = 0
        self.img_count = 0
        self.img_alts = 0
        self.links = []
        self.has_google_tag = False
        self.has_ga4 = False
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "h1":
            self._in_h1 = True
        if tag == "h2":
            self._in_h2 = True
        if tag == "meta":
            name = attrs_dict.get("name", "").lower()
            if name == "description":
                self.meta_description = attrs_dict.get("content", "")
            elif name == "keywords":
                self.meta_keywords = attrs_dict.get("content", "")
        if tag == "link" and attrs_dict.get("rel") == "canonical":
            self.canonical = attrs_dict.get("href", "")
        if tag == "img":
            self.img_count += 1
            if attrs_dict.get("alt", "").strip():
                self.img_alts += 1
        if tag == "a":
            href = attrs_dict.get("href", "")
            if href and not href.startswith("#") and not href.startswith("javascript"):
                self.links.append(href)
        if tag == "script":
            src = attrs_dict.get("src", "")
            if "googletagmanager" in src:
                self.has_google_tag = True
            if "gtag" in src or "ga4" in src:
                self.has_ga4 = True
    
    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "h1":
            self._in_h1 = False
        if tag == "h2":
            self._in_h2 = False
    
    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()
        elif self._in_h1:
            self.h1_tags.append(data.strip())
        elif self._in_h2:
            self.h2_tags.append(data.strip())
        elif data.strip():
            self.text_content.append(data.strip())

# ── Fetcher ──────────────────────────────────────────────────────
def fetch_url(url, timeout=15):
    """Fetch a URL and return (status, html)."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; SEOAgent/1.0; +https://midashboard)"}
        )
        resp = urllib.request.urlopen(req, timeout=timeout)
        html = resp.read().decode("utf-8", errors="replace")
        return resp.status, html
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)

def analyze_page(url, site_id=None):
    """Fetch and analyze a single page for SEO metrics."""
    status, html = fetch_url(url)
    result = {
        "url": url,
        "status": status,
        "analyzed_at": datetime.now().strftime("%Y-%m-%dT%H:%M"),
    }
    
    if status == 200 and html:
        parser = SEOParser()
        try:
            parser.feed(html)
        except:
            pass
        
        # Title analysis
        result["title"] = parser.title
        result["title_length"] = len(parser.title)
        result["title_too_short"] = len(parser.title) < 30 and len(parser.title) > 0
        result["title_too_long"] = len(parser.title) > 60
        result["title_missing"] = len(parser.title) == 0
        
        # Meta description analysis
        result["meta_description"] = parser.meta_description[:150] if parser.meta_description else ""
        result["meta_desc_length"] = len(parser.meta_description)
        result["meta_desc_missing"] = len(parser.meta_description) == 0
        result["meta_desc_too_short"] = 0 < len(parser.meta_description) < 120
        result["meta_desc_too_long"] = len(parser.meta_description) > 160
        
        # Content analysis
        result["word_count"] = len(" ".join(parser.text_content).split())
        result["h1_count"] = len(parser.h1_tags)
        result["h2_count"] = len(parser.h2_tags)
        result["has_h1"] = len(parser.h1_tags) > 0
        result["images"] = parser.img_count
        result["images_with_alt"] = parser.img_alts
        result["links"] = len(parser.links)
        result["has_canonical"] = bool(parser.canonical)
        
        # Keyword analysis (for target site keywords)
        content_lower = " ".join(parser.text_content).lower()
        result["keyword_hits"] = {}
        if site_id and site_id in SITES:
            for kw in SITES[site_id]["keywords"]:
                count = content_lower.count(kw.lower())
                if count > 0:
                    result["keyword_hits"][kw] = count
        
        # SEO score (0-100)
        score = 100
        if not parser.title: score -= 20
        elif len(parser.title) < 20: score -= 10
        elif len(parser.title) > 65: score -= 5
        
        if not parser.meta_description: score -= 20
        elif len(parser.meta_description) < 120: score -= 10
        
        if not parser.h1_tags: score -= 10
        if parser.img_count > 0 and parser.img_alts < parser.img_count: score -= 5
        if parser.word_count < 300: score -= 10
        if not parser.canonical: score -= 5
        
        result["seo_score"] = max(0, score)
        
        # Issues
        result["issues"] = []
        if result["title_missing"]:
            result["issues"].append("❌ Missing <title> tag")
        elif result["title_too_short"]:
            result["issues"].append(f"⚠️ Title too short ({len(parser.title)} chars)")
        elif result["title_too_long"]:
            result["issues"].append(f"⚠️ Title too long ({len(parser.title)} chars)")
        if result["meta_desc_missing"]:
            result["issues"].append("❌ Missing meta description")
        elif result["meta_desc_too_short"]:
            result["issues"].append(f"⚠️ Meta description too short ({len(parser.meta_description)} chars)")
        if not result["has_h1"]:
            result["issues"].append("❌ No H1 tag found")
        if parser.word_count < 200:
            result["issues"].append(f"⚠️ Very thin content ({parser.word_count} words)")
        if parser.img_count > 0 and parser.img_alts == 0:
            result["issues"].append("❌ No images have alt text")
        elif parser.img_count > 0 and parser.img_alts < parser.img_count:
            result["issues"].append(f"⚠️ Only {parser.img_alts}/{parser.img_count} images have alt text")
        if not result["has_canonical"]:
            result["issues"].append("⚠️ No canonical URL")
    else:
        result["seo_score"] = 0
        result["issues"] = [f"❌ HTTP {status}: Page not accessible"]
    
    return result

# ── Sitemap Parser ───────────────────────────────────────────────
def get_sitemap_urls(site_url):
    """Get all URLs from a sitemap (including nested sitemaps)."""
    urls = []
    sitemap_url = site_url.rstrip("/") + "/sitemap.xml"
    
    status, xml = fetch_url(sitemap_url)
    if status != 200:
        # Try /sitemap-index.xml
        sitemap_url = site_url.rstrip("/") + "/sitemap-index.xml"
        status, xml = fetch_url(sitemap_url)
    
    if status == 200 and xml:
        # Find all <loc> tags
        locs = re.findall(r'<loc>([^<]+)</loc>', xml, re.IGNORECASE)
        if locs:
            # Check if this is a sitemap index
            if any("sitemap" in loc.lower() for loc in locs):
                for loc in locs:
                    if "sitemap" in loc.lower():
                        _, sub_xml = fetch_url(loc)
                        if sub_xml:
                            sub_locs = re.findall(r'<loc>([^<]+)</loc>', sub_xml, re.IGNORECASE)
                            urls.extend(sub_locs)
            else:
                urls = locs
    
    return urls

# ── Content Suggestions ──────────────────────────────────────────
def generate_content_suggestions(site_id):
    """Generate new SEO content page suggestions."""
    site = SITES.get(site_id)
    if not site:
        return []
    
    suggestions = []
    site_name = site["name"]
    site_url = site["url"]
    
    if site_id == "antoniopaving":
        # Paving content by suburb
        for suburb in MELBOURNE_SUBURBS[:10]:
            suggestions.append({
                "title": f"Paving Services in {suburb}, Melbourne | {site_name}",
                "slug": f"paving-{suburb.lower().replace(' ', '-')}-melbourne",
                "keywords": [f"paving {suburb.lower()}", f"driveway paving {suburb.lower()}"],
                "focus_keyword": f"paving {suburb.lower()} melbourne",
                "content_type": "service-location",
                "reason": f"Location-specific landing page for {suburb}",
                "estimated_competition": "medium",
            })
        
        # Service pages
        suggestions.extend([
            {
                "title": f"Concrete Driveway Paving Melbourne | {site_name}",
                "slug": "concrete-driveway-paving-melbourne",
                "keywords": ["concrete driveway", "concrete driveway melbourne"],
                "focus_keyword": "concrete driveway paving melbourne",
                "content_type": "service",
                "reason": "High-volume keyword targeting homeowners",
                "estimated_competition": "high",
            },
            {
                "title": f"How Much Does Driveway Paving Cost in Melbourne?",
                "slug": "driveway-paving-cost-melbourne",
                "keywords": ["driveway paving cost", "paving cost melbourne"],
                "focus_keyword": "driveway paving cost melbourne",
                "content_type": "guide",
                "reason": "Cost guides rank well for local intent",
                "estimated_competition": "medium",
            },
            {
                "title": f"Commercial Paving Contractors Melbourne | {site_name}",
                "slug": "commercial-paving-contractors-melbourne",
                "keywords": ["commercial paving", "paving contractors melbourne"],
                "focus_keyword": "commercial paving contractors melbourne",
                "content_type": "service",
                "reason": "B2B targeting builders and developers",
                "estimated_competition": "medium",
            },
        ])
    
    elif site_id == "primeproperty":
        # Decking by suburb
        for suburb in MELBOURNE_SUBURBS[:10]:
            suggestions.append({
                "title": f"Decking Services in {suburb} | {site_name}",
                "slug": f"decking-{suburb.lower().replace(' ', '-')}-melbourne",
                "keywords": [f"decking {suburb.lower()}", f"deck builders {suburb.lower()}"],
                "focus_keyword": f"decking {suburb.lower()} melbourne",
                "content_type": "service-location",
                "reason": f"Location-specific page for {suburb} decking",
                "estimated_competition": "medium",
            })
        
        # Service pages
        suggestions.extend([
            {
                "title": f"Complete Property Maintenance Melbourne | {site_name}",
                "slug": "property-maintenance-melbourne",
                "keywords": ["property maintenance melbourne", "strata maintenance"],
                "focus_keyword": "property maintenance melbourne",
                "content_type": "service",
                "reason": "Main umbrella page for all services",
                "estimated_competition": "high",
            },
            {
                "title": f"Strata Property Maintenance Melbourne | {site_name}",
                "slug": "strata-property-maintenance-melbourne",
                "keywords": ["strata maintenance melbourne", "body corporate maintenance"],
                "focus_keyword": "strata property maintenance melbourne",
                "content_type": "service",
                "reason": "Target strata managers and body corporates",
                "estimated_competition": "medium",
            },
            {
                "title": f"Gutter Cleaning Cost Melbourne | {site_name}",
                "slug": "gutter-cleaning-cost-melbourne",
                "keywords": ["gutter cleaning cost", "gutter cleaning price melbourne"],
                "focus_keyword": "gutter cleaning cost melbourne",
                "content_type": "guide",
                "reason": "Cost guide for high-intent search",
                "estimated_competition": "medium",
            },
            {
                "title": f"Fencing Installation Guide Melbourne | Types & Costs",
                "slug": "fencing-installation-melbourne",
                "keywords": ["fence installation", "fencing melbourne", "fencing cost melbourne"],
                "focus_keyword": "fencing installation melbourne",
                "content_type": "guide",
                "reason": "Comprehensive guide for homeowners",
                "estimated_competition": "medium",
            },
        ])
    
    return suggestions

# ─── Analyzer ────────────────────────────────────────────────────
def run_audit(site_id=None, quick=False):
    """Run full SEO audit on one or all sites."""
    report = {
        "updated": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "sites": {},
        "summary": {},
    }
    
    targets = [site_id] if site_id else list(SITES.keys())
    
    for sid in targets:
        site = SITES[sid]
        log_prefix = f"[{sid.upper()}]"
        print(f"\n{'='*60}")
        print(f"{log_prefix} Auditing {site['name']} — {site['url']}")
        print(f"{'='*60}")
        
        site_report = {
            "url": site["url"],
            "name": site["name"],
            "analyzed_at": datetime.now().strftime("%Y-%m-%dT%H:%M"),
            "pages": [],
            "issues": [],
            "keywords": site["keywords"],
            "content_suggestions": [],
        }
        
        if not quick:
            # Get all pages from sitemap
            print(f"  📍 Fetching sitemap...")
            sitemap_urls = get_sitemap_urls(site["url"])
            print(f"  📄 Found {len(sitemap_urls)} URLs in sitemap")
            
            # Analyze first 50 pages (to avoid rate limiting)
            pages_to_scan = sitemap_urls[:50] if sitemap_urls else [site["url"]]
            if not sitemap_urls:
                pages_to_scan = [site["url"]]
            
            print(f"  🔍 Analyzing {len(pages_to_scan)} pages...")
            
            with ThreadPoolExecutor(max_workers=5) as pool:
                futures = {}
                for url in pages_to_scan:
                    future = pool.submit(analyze_page, url, sid)
                    futures[future] = url
                
                for future in as_completed(futures):
                    url = futures[future]
                    try:
                        result = future.result(timeout=30)
                        site_report["pages"].append(result)
                        
                        # Collect issues
                        for issue in result.get("issues", []):
                            site_report["issues"].append(f"{url}: {issue}")
                        
                        score = result.get("seo_score", 0)
                        status = "✅" if score >= 80 else "⚠️" if score >= 50 else "❌"
                        print(f"  {status} {url[:60]:60s} Score: {score}")
                    except TimeoutError:
                        print(f"  ⏰ {url[:60]:60s} Timeout")
                    except Exception as e:
                        print(f"  ❌ {url[:60]:60s} Error: {e}")
            
            # Generate content suggestions
            print(f"  💡 Generating content suggestions...")
            suggestions = generate_content_suggestions(sid)
            site_report["content_suggestions"] = suggestions
            for s in suggestions:
                print(f"     → {s['title'][:70]}")
            
            # Compile statistics
            pages_analyzed = len(site_report["pages"])
            pages_ok = sum(1 for p in site_report["pages"] if p.get("seo_score", 0) >= 80)
            pages_warn = sum(1 for p in site_report["pages"] if 50 <= p.get("seo_score", 0) < 80)
            pages_bad = sum(1 for p in site_report["pages"] if p.get("seo_score", 0) < 50)
            missing_meta = sum(1 for p in site_report["pages"] if p.get("meta_desc_missing"))
            missing_title = sum(1 for p in site_report["pages"] if p.get("title_missing"))
            
            site_report["stats"] = {
                "pages_analyzed": pages_analyzed,
                "pages_good": pages_ok,
                "pages_warning": pages_warn,
                "pages_bad": pages_bad,
                "missing_meta_descriptions": missing_meta,
                "missing_titles": missing_title,
            }
            
            report["summary"][sid] = {
                "score": "good" if pages_ok > pages_bad else "needs_work",
                "pages_ok": pages_ok,
                "pages_bad": pages_bad,
                "total_pages": pages_analyzed,
                "issues_count": len(site_report["issues"]),
                "content_suggestions": len(suggestions),
            }
        else:
            # Quick check: just homepage + sitemap count
            print(f"  🔍 Quick check...")
            homepage = analyze_page(site["url"], sid)
            site_report["pages"].append(homepage)
            sitemap_urls = get_sitemap_urls(site["url"])
            site_report["sitemap_count"] = len(sitemap_urls)
            site_report["quick_homepage_score"] = homepage.get("seo_score", 0)
            
            print(f"  Homepage SEO Score: {homepage.get('seo_score', 'N/A')}")
            print(f"  Sitemap URLs: {len(sitemap_urls)}")
        
        report["sites"][sid] = site_report
    
    # Save report
    save_json(SEO_REPORT_FILE, report)
    
    # Also update health.json
    update_health_with_seo(report)
    
    print(f"\n{'='*60}")
    print(f"✅ SEO Audit complete! Report saved to data/seo_report.json")
    print(f"{'='*60}")
    
    return report

def update_health_with_seo(report):
    """Update health.json with SEO scores."""
    health = load_json(HEALTH_FILE, {"sites": []})
    health["seo_audit"] = {
        "updated": report["updated"],
        "summary": report.get("summary", {}),
    }
    # Update individual site seo_metrics in health
    for site_entry in health.get("sites", []):
        for sid, sreport in report.get("sites", {}).items():
            if sid in site_entry.get("url", "").lower() or sid.replace("antoniopaving", "antoniopaving.com") in site_entry.get("url", "").lower():
                stats = sreport.get("stats", {})
                site_entry["seo_metrics"] = {
                    "pages_analyzed": stats.get("pages_analyzed", 0),
                    "pages_good": stats.get("pages_good", 0),
                    "pages_bad": stats.get("pages_bad", 0),
                    "missing_meta": stats.get("missing_meta_descriptions", 0),
                    "missing_titles": stats.get("missing_titles", 0),
                    "content_suggestions": len(sreport.get("content_suggestions", [])),
                }
                site_entry["seo_score"] = sreport.get("stats", {}).get("pages_good", 0) / max(stats.get("pages_analyzed", 1), 1) * 100
    
    save_json(HEALTH_FILE, health)

def load_json(path, default=None):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default or {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ── CLI ──────────────────────────────────────────────────────────
def main():
    if "--report" in sys.argv:
        report = load_json(SEO_REPORT_FILE, {})
        if not report.get("sites"):
            print("📋 No hay reporte SEO guardado. Ejecuta sin flags para generar uno.")
            return
        print(f"📋 Último reporte SEO: {report.get('updated', 'N/A')}")
        for sid, sreport in report.get("sites", {}).items():
            stats = sreport.get("stats", {})
            print(f"\n  🌐 {sreport.get('name', sid)}")
            print(f"     Páginas analizadas: {stats.get('pages_analyzed', 0)}")
            print(f"     ✅ Buenas: {stats.get('pages_good', 0)}")
            print(f"     ⚠️  Advertencia: {stats.get('pages_warning', 0)}")
            print(f"     ❌ Malas: {stats.get('pages_bad', 0)}")
            print(f"     Sin meta description: {stats.get('missing_meta_descriptions', 0)}")
            print(f"     Sugerencias: {stats.get('content_suggestions', len(sreport.get('content_suggestions', [])))}")
        return
    
    quick = "--quick" in sys.argv
    site_id = None
    if "--site" in sys.argv:
        idx = sys.argv.index("--site")
        if idx + 1 < len(sys.argv):
            site_id = sys.argv[idx + 1]
    
    run_audit(site_id=site_id, quick=quick)

if __name__ == "__main__":
    main()
