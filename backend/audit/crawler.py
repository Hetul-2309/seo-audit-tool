import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
from collections import deque, defaultdict

from .utils import normalize_url, same_host, is_http_url, is_private_host
from .checks import (
    get_title, get_meta_description, heading_counts, get_h1_texts,
    image_alt_counts, extract_text_word_count, basic_speed_tips
)
from .models import PageData, Issue
from .prioritize import classify_issues
from .suggest import suggest_title, suggest_description, keyword_hits, content_tips

HEADERS = {"User-Agent": "SEOQuickAuditBot/1.0 (+https://example.com)"}
TIMEOUT = 15

def _strip_www(u: str) -> str:
    p = urlparse(u)
    host = p.netloc
    if host.startswith("www."):
        host = host[4:]
        return urlunparse((p.scheme, host, p.path, p.params, p.query, p.fragment))
    return u

def fetch(url: str) -> tuple[int, str, float, str | None, str]:
    """
    Returns: (status, html, seconds, error, final_url_used)
    status=0 means network/DNS failure.
    """
    t0 = time.time()
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code, (r.text or ""), time.time() - t0, None, url
    except requests.RequestException as e:
        # quick fallback: if www fails, try without www once
        alt = _strip_www(url)
        if alt != url:
            try:
                r = requests.get(alt, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
                return r.status_code, (r.text or ""), time.time() - t0, None, alt
            except requests.RequestException as e2:
                return 0, "", time.time() - t0, f"{e} | fallback: {e2}", alt
        return 0, "", time.time() - t0, str(e), url

def check_link(url: str) -> int:
    try:
        r = requests.head(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code >= 400 or r.status_code == 405:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code
    except Exception:
        return 0  # unknown / failed

def run_audit(url: str, target_keyword: str | None, max_pages: int = 25, max_depth: int = 2) -> dict:
    if not is_http_url(url) or is_private_host(url):
        return {"error": "Invalid or blocked URL."}

    home = url
    host = urlparse(home).netloc.lower()

    visited = set()
    pages: list[PageData] = []
    q = deque([(home, 0)])

    # Track duplicates
    titles_map = defaultdict(list)
    desc_map = defaultdict(list)

    # Link problems
    broken_links: list[dict] = []

    while q and len(visited) < max_pages:
        current, depth = q.popleft()
        if current in visited or depth > max_depth:
            continue
        if not same_host(home, current):
            continue

        visited.add(current)

        status, html, ttfb, err, final_url = fetch(current)
        soup = BeautifulSoup(html, "lxml") if html else None

        page = PageData(
            if status == 0:
    page.issues.append(Issue(
        priority="P1",
        code="FETCH_FAILED",
        message=f"Failed to fetch page (DNS/network): {err}",
        url=current,
        fix="Try again later or audit a different URL. Some hosts fail DNS resolution from cloud servers intermittently."
    ))
    pages.append(page)
    continue
            url=current,
            status=status,
        )

        if soup and status < 400:
            page.title = get_title(soup)
            page.meta_description = get_meta_description(soup)
            page.headings = heading_counts(soup)
            page.h1 = get_h1_texts(soup)
            page.images_total, page.images_missing_alt = image_alt_counts(soup)
            page.word_count = extract_text_word_count(soup)
            page.speed_tips = basic_speed_tips(soup)

            # links
            internal = external = 0
            links = []
            for a in soup.find_all("a"):
                href = a.get("href")
                full = normalize_url(current, href)
                if not full or not is_http_url(full):
                    continue
                links.append(full)
                if same_host(home, full):
                    internal += 1
                    # enqueue internal pages
                    if full not in visited:
                        q.append((full, depth + 1))
                else:
                    external += 1
            page.internal_links = internal
            page.external_links = external

            # keyword analysis (basic)
            if target_keyword:
                visible_text = soup.get_text(" ", strip=True)
                hits = keyword_hits(visible_text, target_keyword)
                page.keyword_hits = {
                    "in_text": hits,
                    "in_title": keyword_hits(page.title or "", target_keyword),
                    "in_h1": keyword_hits(" ".join(page.h1), target_keyword),
                }

            # suggestions
            page.suggestions = {
                "suggested_title": suggest_title(page.title, page.h1, target_keyword),
                "suggested_meta_description": suggest_description(page.meta_description, target_keyword),
            }

            # issues
            page.issues.extend(classify_issues(page))

            # content tips
            if target_keyword:
                tips = content_tips(
                    word_count=page.word_count,
                    has_h1=(page.headings.get("h1", 0) > 0),
                    keyword=target_keyword,
                    keyword_count=page.keyword_hits.get("in_text", 0),
                )
                for tip in tips:
                    page.issues.append(Issue(priority="P3", code="CONTENT_TIP", message=tip, url=page.url))

            # duplicates tracking
            if page.title:
                titles_map[page.title.strip().lower()].append(page.url)
            if page.meta_description:
                desc_map[page.meta_description.strip().lower()].append(page.url)

            # Check a small subset of links for broken (MVP: cap per page)
            for link in links[:30]:
                code = check_link(link)
                if code == 0 or code >= 400:
                    broken_links.append({"from": current, "to": link, "status": code})

        pages.append(page)

    # Global duplicate issues
    global_issues: list[Issue] = []
    for t, urls in titles_map.items():
        if len(urls) >= 2:
            for u in urls:
                global_issues.append(Issue(priority="P2", code="DUPLICATE_TITLE",
                                           message=f"Duplicate title used on {len(urls)} pages.", url=u,
                                           fix="Make each page title unique and specific to that page."))

    # Broken links summary issues
    if broken_links:
        global_issues.append(Issue(priority="P1", code="BROKEN_LINKS_FOUND",
                                   message=f"Found {len(broken_links)} broken link(s).",
                                   details={"examples": broken_links[:20]},
                                   fix="Fix or remove broken links. Redirect removed pages, update old URLs."))

    # Build priority buckets
    def bucket(priority: str) -> list[dict]:
        out = []
        for p in pages:
            for issue in p.issues:
                if issue.priority == priority:
                    out.append(issue.model_dump())
        for gi in global_issues:
            if gi.priority == priority:
                out.append(gi.model_dump())
        return out

    report = {
        "site": {"url": home, "host": host, "pages_crawled": len(pages)},
        "inputs": {"target_keyword": target_keyword, "max_pages": max_pages, "max_depth": max_depth},
        "priority_fixes": {
            "P1": bucket("P1"),
            "P2": bucket("P2"),
            "P3": bucket("P3"),
        },
        "pages": [p.model_dump() for p in pages],
        "broken_links": broken_links[:200],
    }

    return report

