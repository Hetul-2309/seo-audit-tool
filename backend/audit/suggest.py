import re
from urllib.parse import urlparse

def slug_to_words(url: str) -> str:
    path = urlparse(url).path.strip("/").split("/")[-1]
    path = path.replace("-", " ").replace("_", " ").replace("&", " and ")
    return " ".join([w.capitalize() for w in path.split() if w])

def suggest_title(base_title: str | None, h1s: list[str], keyword: str | None, brand: str = "Solanki Ship Care") -> str:
    core = (h1s[0] if h1s else "Marine Services")
    if keyword:
        # Put keyword early, brand at end
        return f"{core} | {keyword.title()} | {brand}"[:60].strip()
    return f"{core} | {brand}"[:60].strip()

def suggest_description(existing: str | None, keyword: str | None, city: str = "India") -> str:
    kw = (keyword or "marine supply").strip()
    # Always generate a fresh, CTA-style meta description
    s = f"{kw.title()} in {city}. Certified ship chandling, bonded stores & provisions. Fast delivery, compliant docs, 24/7 support. Get a quick quote."
    return s[:160].strip()

def keyword_hits(text: str, keyword: str) -> int:
    # very basic exact phrase match
    pattern = re.compile(re.escape(keyword), re.I)
    return len(pattern.findall(text))

def content_tips(word_count: int, has_h1: bool, keyword: str | None, keyword_count: int) -> list[str]:
    tips = []
    if not has_h1:
        tips.append("Add a clear H1 that matches the primary topic of the page.")
    if word_count < 300:
        tips.append("Content is thin (<300 words). Add helpful sections: services, FAQs, proof, location coverage, process, and next steps.")
    if keyword and keyword_count == 0:
        tips.append("Target keyword not found in visible page text. Add it naturally in H1 or first paragraph, and in one subheading.")
    if keyword and keyword_count > 20:
        tips.append("Keyword appears very frequently. Reduce repetition and use synonyms; keep copy natural.")

    return tips
