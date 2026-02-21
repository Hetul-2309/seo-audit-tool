import re

def suggest_title(base_title: str | None, h1s: list[str], keyword: str | None) -> str:
    core = (h1s[0] if h1s else "Your Service")
    if keyword:
        # Keep it readable, not spammy
        return f"{core} | {keyword.title()} Services"
    if base_title:
        return base_title
    return f"{core} | Local Business"

def suggest_description(existing: str | None, keyword: str | None) -> str:
    if existing and 70 <= len(existing) <= 170:
        return existing
    if keyword:
        return f"Learn how our {keyword} helps you get better results. Transparent pricing, fast turnaround, and friendly support."
    return "Discover our services, pricing, and how we help customers get better results with consistent, high-quality work."

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