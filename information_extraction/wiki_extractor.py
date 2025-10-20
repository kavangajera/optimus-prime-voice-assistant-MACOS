"""
wikipedia_scraper.py
Search Wikipedia (like the Main Page search box), open nearest page, extract structured data.
Dependencies: requests, beautifulsoup4
Install: pip install requests beautifulsoup4
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import json
import time
import re

BASE = "https://en.wikipedia.org"
SEARCH_ENDPOINT = BASE + "/w/index.php"

HEADERS = {
    "User-Agent": "UniversalInformatorBot/1.0 (your_email@example.com) - script to fetch wiki article data; please contact if problem",
    # keep polite contact info in UA
}

def search_wikipedia(query, sleep=0.5):
    """Perform the same search that Main Page search uses, follow redirects if needed.
    Returns the `url` of the best match or None."""
    params = {
        "search": query,
        "title": "Special:Search",
        "fulltext": "1",
        "ns0": "1",
    }
    resp = requests.get(SEARCH_ENDPOINT, params=params, headers=HEADERS, allow_redirects=True, timeout=10)
    time.sleep(sleep)
    # If it redirected to an article page, resp.url will be that article
    final_url = resp.url
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    # If final_url looks like an article (contains /wiki/Title) return it.
    if "/wiki/" in final_url and "Special:Search" not in final_url:
        return final_url

    # Otherwise parse the search results page and pick the first result link.
    # Search results show up under div.mw-search-result-heading > a
    first = soup.select_one("div.mw-search-result-heading > a")
    if first and first.get("href"):
        return urljoin(BASE, first["href"])

    # Another fallback: suggested result (sometimes there's a suggestion box)
    suggested = soup.select_one("a.mw-search-createlink, .searchdidyoumean a")
    if suggested and suggested.get("href"):
        return urljoin(BASE, suggested["href"])

    # Sometimes search returns a link list in 'mw-search-result' list items with <a>
    li_first = soup.select_one("ul.mw-search-results li a")
    if li_first and li_first.get("href"):
        return urljoin(BASE, li_first["href"])

    return None

def fetch_html(url, sleep=0.5):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    time.sleep(sleep)
    resp.raise_for_status()
    return resp.text

def parse_infobox(soup):
    box = soup.find("table", class_=lambda c: c and "infobox" in c)
    if not box:
        return {}
    info = {}
    # Rows are tr, keys often in th, values in td
    for tr in box.find_all("tr"):
        th = tr.find("th")
        td = tr.find("td")
        if th and td:
            key = " ".join(th.stripped_strings)
            # convert value to text but keep links/images as small html fragments if needed
            val = " ".join(td.stripped_strings)
            info[key] = val
    return info

def extract_sections(soup):
    content = soup.find(id="mw-content-text")
    if not content:
        return []

    sections = []
    # iterate through children and group paragraphs under the current heading
    current = {"heading": "Lead", "text": ""}
    for child in content.find_all(recursive=False):
        # Many pages wrap the body in a <div class="mw-parser-output">
        if child.name == "div" and "mw-parser-output" in (child.get("class") or []):
            for item in child.children:
                if getattr(item, "name", None) and re.match(r"h[2-6]", item.name):
                    # new heading
                    heading_text = " ".join(item.stripped_strings)
                    if current["text"].strip():
                        sections.append(current)
                    current = {"heading": heading_text, "text": ""}
                elif getattr(item, "name", None) in ("p", "ul", "ol", "dl"):
                    text = " ".join(item.stripped_strings)
                    if text:
                        current["text"] += (text + "\n\n")
            break

    # append last
    if current and current["text"].strip():
        sections.append(current)
    return sections

def extract_images(soup):
    images = []
    # article images typically inside .mw-parser-output img
    for img in soup.select(".mw-parser-output img"):
        src = img.get("src")
        if not src:
            continue
        # normalize scheme-relative URLs
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = urljoin(BASE, src)
        images.append({
            "alt": img.get("alt"),
            "src": src,
            "width": img.get("width"),
            "height": img.get("height"),
        })
    # dedupe preserving order
    seen = set()
    out = []
    for im in images:
        if im["src"] not in seen:
            seen.add(im["src"])
            out.append(im)
    return out

def extract_categories(soup):
    cats = []
    for a in soup.select("#mw-normal-catlinks ul li a"):
        cats.append(a.text.strip())
    return cats

def extract_references(soup):
    refs = []
    for li in soup.select("ol.references li"):
        txt = " ".join(li.stripped_strings)
        refs.append(txt)
    return refs

def parse_article(url):
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    # title
    title_tag = soup.find(id="firstHeading")
    title = title_tag.text.strip() if title_tag else None

    # lead/summary: first meaningful <p> under .mw-parser-output
    summary = ""
    content_div = soup.select_one(".mw-parser-output")
    if content_div:
        for p in content_div.find_all("p", recursive=False):
            text = p.get_text(strip=True)
            if text:
                summary = text
                break

    infobox = parse_infobox(soup)
    sections = extract_sections(soup)
    images = extract_images(soup)
    categories = extract_categories(soup)
    references = extract_references(soup)

    # detect if this is a disambiguation page
    is_disambig = bool(soup.find(class_=lambda c: c and "disambiguation" in c))

    data = {
        "url": url,
        "title": title,
        "summary": summary,
        "infobox": infobox,
        "sections": sections,
        "images": images,
        "categories": categories,
        "references": references,
        "is_disambiguation": is_disambig
    }
    return data

def save_json(data, filename="article.json"):
    filename = f"/Users/kavan/Documents/GitHub/optimus-prime-voice-assistant-MACOS/information_extraction/{filename}"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved to {filename}")

def main():
    query = input("Enter search query: ").strip()
    if not query:
        print("Empty.")
        return
    print("Searching Wikipedia for:", query)
    url = search_wikipedia(query)
    if not url:
        print("No results found.")
        return
    print("Opening:", url)
    article = parse_article(url)
    # If disambiguation, show possible pages (first section often lists links)
    if article["is_disambiguation"]:
        print("Result is a disambiguation page. Consider selecting one of these categories/titles:")
        for sec in article["sections"][:5]:
            print("-", sec["heading"])
    save_json(article, f"{re.sub(r'[^A-Za-z0-9]+','_', query)[:40]}.json")
    print("Title:", article["title"])
    print("Summary:", article["summary"][:400], "...")
    print("Infobox keys:", list(article["infobox"].keys()))
    print("Top sections:", [s["heading"] for s in article["sections"][:6]])
    print("Images:", len(article["images"]))
    print("Categories:", article["categories"])

if __name__ == "__main__":
    main()
