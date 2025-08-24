# scraper.py
"""
Updated scraper with toggle for Codeforces page fetching.
- Set CF_FETCH_PAGES = False to avoid fetching problem HTML from Codeforces (fast, avoids 403).
- Set CF_FETCH_PAGES = True to attempt fetching page HTML (may require Playwright browser install).
"""

import json
import time
import sys
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup

# ------------ Configuration -------------
OUT_FILE = "problems.json"

# Codeforces: whether to fetch problem pages for description.
# If False: only use API results (title, tags, url) and skip HTML fetching to avoid 403s.
# If True: attempt page fetch using requests.Session + Playwright fallback (requires playwright + browsers).
CF_FETCH_PAGES = True

# How many Codeforces problems to attempt (from API list)
CF_LIMIT = 50

# GeeksforGeeks: which tags and how many pages per tag to fetch
GFG_TAGS = ("arrays", "dynamic-programming", "graph", "greedy")
GFG_PAGES = 2

# Pause times (seconds)
PAUSE_SHORT = 0.15
PAUSE_LONG = 0.3

# Browser-like User-Agent (keeps requests realistic)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://codeforces.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# ------------ Session setup (requests) -------------
_session = requests.Session()
_session.headers.update(DEFAULT_HEADERS)
retries = Retry(total=3, backoff_factor=0.6, status_forcelist=(429, 502, 503, 504))
_adapter = HTTPAdapter(max_retries=retries)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

# Try an initial request to collect cookies
try:
    _session.get("https://codeforces.com", timeout=10)
except Exception:
    pass

# ------------ Playwright helper (optional) -------------
def _playwright_fetch(url, timeout=30000):
    """
    Use Playwright to fetch page HTML. Raises ImportError if Playwright is not installed.
    Caller should catch exceptions as needed.
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        raise ImportError("Playwright not installed. Run: pip install playwright; python -m playwright install")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = browser.new_page(user_agent=USER_AGENT, locale="en-US")
            # visit home first to set cookies (helps some sites)
            try:
                page.goto("https://codeforces.com", timeout=timeout)
            except Exception:
                pass
            page.goto(url, timeout=timeout)
            content = page.content()
            browser.close()
            return content
    except Exception as e:
        # bubble up to caller
        raise

# ------------ Robust fetch function (session + optional playwright fallback) -------------
def safe_get(url, timeout=20, use_playwright_fallback=True):
    """
    Attempt to fetch `url` using a persistent requests.Session.
    If requests fails and use_playwright_fallback=True, try Playwright (if installed).
    Returns HTML string or None.
    """
    try:
        r = _session.get(url, timeout=timeout)
        r.raise_for_status()
        return r.text
    except requests.exceptions.HTTPError as e:
        print(f"GET error {url}: {e}")
    except Exception as e:
        print(f"GET error {url}: {e}")

    if use_playwright_fallback:
        try:
            html = _playwright_fetch(url)
            print(f"Playwright fetched: {url}")
            return html
        except ImportError as ie:
            # remind the user to install browsers
            print(f"Playwright not available ({ie}). To enable Playwright fallback, run:\n  pip install playwright\n  python -m playwright install")
        except Exception as pe:
            print(f"Playwright fallback failed for {url}: {pe}")

    return None

# ------------ Scrapers -------------
def scrape_codeforces(limit=CF_LIMIT, pause=PAUSE_SHORT, fetch_pages=CF_FETCH_PAGES):
    """
    Use Codeforces API to list problems. If fetch_pages=True, attempt to fetch each problem page for description.
    Returns list of dicts: {source, title, description, tags, url}
    """
    print("Fetching Codeforces problem list via API...")
    try:
        resp = _session.get("https://codeforces.com/api/problemset.problems", timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print("Failed to fetch Codeforces API:", e)
        return []

    data = resp.json()
    problems = data.get("result", {}).get("problems", [])
    out = []
    count = 0

    for p in problems:
        if count >= limit:
            break
        contestId = p.get("contestId")
        index = p.get("index")
        if not contestId or not index:
            continue
        url = f"https://codeforces.com/problemset/problem/{contestId}/{index}"
        title = (p.get("name") or "").strip()
        tags = p.get("tags", []) or []

        description = ""
        if fetch_pages:
            html = safe_get(url, timeout=20, use_playwright_fallback=True)
            if html:
                try:
                    soup = BeautifulSoup(html, "html.parser")
                    stmt = soup.find("div", class_="problem-statement")
                    if stmt:
                        for bad in stmt.find_all(["script", "style", "noscript"]):
                            bad.decompose()
                        pieces = []
                        for t in stmt.find_all(["p", "div", "span", "pre", "li"]):
                            txt = t.get_text(separator=" ", strip=True)
                            if txt:
                                pieces.append(txt)
                        description = "\n".join(pieces)
                    else:
                        print(f"No HTML for {url}; storing without description.")
                except Exception as e:
                    print(f"Parsing error for {url}: {e}")
            else:
                print(f"No HTML for {url}; storing without description.")
        else:
            # skipping page fetch (fast, avoids 403)
            description = ""

        out.append({
            "source": "codeforces",
            "title": title,
            "description": description,
            "tags": tags,
            "url": url
        })

        count += 1
        time.sleep(pause)

    print(f"Collected {len(out)} Codeforces problems (attempted up to {limit}).")
    return out

def scrape_geeksforgeeks(tag_list=GFG_TAGS, pages_per_tag=GFG_PAGES, pause=PAUSE_LONG):
    """
    Scrape GeeksforGeeks articles from tag pages. Returns list of items with title, description, tags, url.
    (Playwright fallback disabled for speed; can be enabled if needed.)
    """
    base = "https://www.geeksforgeeks.org"
    out = []
    for tag in tag_list:
        for page in range(1, pages_per_tag + 1):
            tag_url = f"{base}/tag/{tag}/page/{page}/"
            print("Fetching GfG tag page:", tag_url)
            html = safe_get(tag_url, timeout=20, use_playwright_fallback=False)
            if not html:
                print(f"Failed to get tag page {tag_url}; skipping.")
                continue
            try:
                soup = BeautifulSoup(html, "html.parser")
                anchors = soup.select("a[href]")
                found = set()
                for a in anchors:
                    href = a.get("href")
                    if not href:
                        continue
                    if href.startswith("/"):
                        href = urljoin(base, href)
                    if not href.startswith(base):
                        continue
                    if "/tag/" in href or "/category/" in href:
                        continue
                    if href in found:
                        continue
                    found.add(href)

                    art_html = safe_get(href, timeout=20, use_playwright_fallback=False)
                    if not art_html:
                        print(f"Skipping article (no HTML): {href}")
                        continue
                    s2 = BeautifulSoup(art_html, "html.parser")
                    title_el = s2.find("h1")
                    title = title_el.get_text(strip=True) if title_el else (a.get_text(strip=True) or "")
                    content_el = s2.find("div", class_="entry-content") or s2.find("div", class_="entry")
                    description = ""
                    if content_el:
                        for bad in content_el.find_all(["script", "style", "aside", "figure"]):
                            bad.decompose()
                        paras = [p.get_text(separator=" ", strip=True) for p in content_el.find_all(["p", "li", "pre"])]
                        description = "\n".join([p for p in paras if p])
                    out.append({
                        "source": "geeksforgeeks",
                        "title": title,
                        "description": description,
                        "tags": [tag],
                        "url": href
                    })
                    time.sleep(pause)
            except Exception as e:
                print(f"Error parsing GfG tag page {tag_url}: {e}")
                continue
    print(f"Collected {len(out)} GeeksforGeeks items.")
    return out

# ------------ Main runner -------------
def main():
    print("Starting scraping run")
    all_problems = []
    try:
        cf = scrape_codeforces(limit=CF_LIMIT, pause=PAUSE_SHORT, fetch_pages=CF_FETCH_PAGES)
        gg = scrape_geeksforgeeks(tag_list=GFG_TAGS, pages_per_tag=GFG_PAGES, pause=PAUSE_LONG)
        all_problems.extend(cf)
        all_problems.extend(gg)

        # deduplicate by URL (preserve first seen)
        seen = set()
        dedup = []
        for p in all_problems:
            url = p.get("url")
            if not url:
                continue
            if url in seen:
                continue
            seen.add(url)
            dedup.append(p)

        print(f"Total problems collected (deduped): {len(dedup)}")
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(dedup, f, ensure_ascii=False, indent=2)
        print("Saved to", OUT_FILE)
    except KeyboardInterrupt:
        print("Interrupted by user. Writing whatever we have so far...")
        try:
            with open(OUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_problems, f, ensure_ascii=False, indent=2)
            print("Partial results saved to", OUT_FILE)
        except Exception as e:
            print("Failed to save partial results:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
