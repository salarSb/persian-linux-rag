#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polite scraper for internal HTML pages on stallman.org.
Saves files under data/html by default.

Usage:
  python scripts/stallman_scrape.py --base-url https://stallman.org --out-dir data/html --max-pages 500

Notes:
- Respects robots.txt.
- Adds a browser-like User-Agent.
- Retries on transient errors, with polite randomized delays.
- Only saves .html pages from the same site.
"""
import argparse
import os
import time
import random
import sys
import re
from urllib.parse import urljoin, urlparse, urldefrag, urlunparse
import requests
from bs4 import BeautifulSoup
from urllib import robotparser

DEF_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
SEEN = set()

def clean_url(u: str) -> str:
    """Normalize URL (remove fragments, strip tracking querystrings)."""
    u, _frag = urldefrag(u)
    parsed = urlparse(u)
    safe_query = "&".join([q for q in parsed.query.split("&") if q and len(q) < 100]) if parsed.query else ""
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", safe_query, ""))

def is_internal_html(href: str, base_netloc: str) -> bool:
    if not href or href.startswith("#") or href.startswith("tel:") or href.startswith("mailto:"):
        return False
    p = urlparse(href)
    if p.netloc and p.netloc != base_netloc:
        return False
    return href.endswith(".html")

def safe_filename_from_url(u: str) -> str:
    path = urlparse(u).path.strip("/")
    if not path or path.endswith("/"):
        path = path + "index.html"
    if path.endswith(".html"):
        name = path.replace("/", "_")
    else:
        name = path.replace("/", "_") + ".html"
    name = re.sub(r"[^A-Za-z0-9._\-]", "_", name)
    return name

def request_get(session: requests.Session, url: str, retries=3, timeout=20):
    for i in range(retries):
        try:
            resp = session.get(url, timeout=timeout)
            if 200 <= resp.status_code < 300:
                return resp
            if resp.status_code in (429, 500, 502, 503, 504):
                delay = (2 ** i) + random.uniform(0.0, 0.8)
                time.sleep(delay)
                continue
            return resp
        except requests.RequestException:
            delay = (2 ** i) + random.uniform(0.0, 0.8)
            time.sleep(delay)
    return None

def crawl(base_url: str, out_dir: str, max_pages: int = 0, delay_min=0.5, delay_max=1.5, user_agent=DEF_UA):
    os.makedirs(out_dir, exist_ok=True)
    parsed_base = urlparse(base_url)
    base_netloc = parsed_base.netloc

    rp = robotparser.RobotFileParser()
    robots_url = f"{parsed_base.scheme}://{base_netloc}/robots.txt"
    try:
        rp.set_url(robots_url)
        rp.read()
    except Exception:
        pass

    sess = requests.Session()
    sess.headers.update({"User-Agent": user_agent})

    to_visit = [base_url]
    saved = 0

    while to_visit:
        url = to_visit.pop(0)
        url = clean_url(url)
        if url in SEEN:
            continue
        SEEN.add(url)

        if not rp.can_fetch(user_agent, url):
            print(f"Skip by robots: {url}")
            continue

        resp = request_get(sess, url)
        if resp is None:
            print(f"Failed: {url} (no response)")
            continue
        if resp.status_code != 200:
            print(f"HTTP {resp.status_code}: {url}")
            continue
        ct = resp.headers.get("Content-Type", "")
        if "text/html" not in ct:
            continue

        fname = safe_filename_from_url(url)
        fpath = os.path.join(out_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(resp.text)
        saved += 1
        print(f"Saved: {fpath}")

        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            links = set()
            for a in soup.find_all("a", href=True):
                href = a["href"]
                full = urljoin(url, href)
                full = clean_url(full)
                if is_internal_html(full, base_netloc):
                    links.add(full)
            for link in sorted(links):
                if link not in SEEN and link not in to_visit:
                    to_visit.append(link)
        except Exception as e:
            print(f"Parse error on {url}: {e}")

        if max_pages and saved >= max_pages:
            break

        time.sleep(random.uniform(delay_min, delay_max))

    print(f"Done. Saved {saved} HTML files to {out_dir}.")

def main():
    ap = argparse.ArgumentParser(description="Download internal HTML pages from stallman.org (polite crawler)." )
    ap.add_argument("--base-url", default="https://stallman.org", help="Starting URL (default: https://stallman.org)")
    ap.add_argument("--out-dir", default="data/html", help="Destination directory (default: data/html)")
    ap.add_argument("--max-pages", type=int, default=0, help="Max pages to save (0 = no limit)")
    ap.add_argument("--delay-min", type=float, default=0.5)
    ap.add_argument("--delay-max", type=float, default=1.5)
    ap.add_argument("--user-agent", default=DEF_UA)
    args = ap.parse_args()
    crawl(args.base_url, args.out_dir, max_pages=args.max_pages,
          delay_min=args.delay_min, delay_max=args.delay_max, user_agent=args.user_agent)

if __name__ == "__main__":
    main()
