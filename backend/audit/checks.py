import re
from bs4 import BeautifulSoup

def extract_text_word_count(soup: BeautifulSoup) -> int:
    text = soup.get_text(" ", strip=True)
    # remove repeated whitespace
    text = re.sub(r"\s+", " ", text)
    words = [w for w in text.split(" ") if w]
    return len(words)

def get_title(soup: BeautifulSoup) -> str | None:
    t = soup.find("title")
    if not t:
        return None
    val = t.get_text(strip=True)
    return val or None

def get_meta_description(soup: BeautifulSoup) -> str | None:
    m = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    if not m:
        return None
    content = (m.get("content") or "").strip()
    return content or None

def heading_counts(soup: BeautifulSoup) -> dict:
    counts = {}
    for lvl in range(1, 7):
        counts[f"h{lvl}"] = len(soup.find_all(f"h{lvl}"))
    return counts

def get_h1_texts(soup: BeautifulSoup) -> list[str]:
    return [h.get_text(" ", strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]

def image_alt_counts(soup: BeautifulSoup) -> tuple[int, int]:
    imgs = soup.find_all("img")
    total = len(imgs)
    missing = 0
    for img in imgs:
        alt = img.get("alt")
        if alt is None or str(alt).strip() == "":
            missing += 1
    return total, missing

def basic_speed_tips(soup: BeautifulSoup) -> list[str]:
    tips = []
    scripts = soup.find_all("script")
    if len(scripts) > 20:
        tips.append("Many <script> tags detected. Consider bundling/minifying JS and loading non-critical scripts with defer/async.")
    css = soup.find_all("link", rel=lambda v: v and "stylesheet" in v)
    if len(css) > 10:
        tips.append("Many CSS files detected. Consider bundling/minifying and removing unused CSS.")
    images = soup.find_all("img")
    if len(images) > 25:
        tips.append("Many images on this page. Ensure compression + lazy-loading for offscreen images.")
    # check for missing width/height attributes (layout shifts)
    wh_missing = 0
    for img in images:
        if not img.get("width") or not img.get("height"):
            wh_missing += 1
    if wh_missing >= 10:
        tips.append("Many images missing width/height. Add dimensions to reduce layout shifts (CLS).")
    return tips