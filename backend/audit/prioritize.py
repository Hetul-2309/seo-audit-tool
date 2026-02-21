from .models import Issue

def classify_issues(page) -> list[Issue]:
    issues: list[Issue] = []

    # P1 - critical
    if page.status >= 400:
        issues.append(Issue(priority="P1", code="HTTP_ERROR", message=f"Page returns HTTP {page.status}.", url=page.url,
                            fix="Ensure the page returns 200 OK (fix routing, hosting, redirects, or removed content)."))
        return issues  # if page is broken, other checks are less relevant

    if not page.title:
        issues.append(Issue(priority="P1", code="MISSING_TITLE", message="Missing <title> tag.", url=page.url,
                            fix="Add a unique, descriptive title (50–60 chars) including primary topic/keyword."))
    if page.headings.get("h1", 0) == 0:
        issues.append(Issue(priority="P1", code="MISSING_H1", message="No H1 found.", url=page.url,
                            fix="Add exactly one H1 that describes the page’s main topic."))
    if page.headings.get("h1", 0) > 1:
        issues.append(Issue(priority="P2", code="MULTIPLE_H1", message="Multiple H1 tags found.", url=page.url,
                            fix="Keep one H1. Convert others to H2/H3."))

    # Meta description: important but not fatal
    if not page.meta_description:
        issues.append(Issue(priority="P2", code="MISSING_META_DESCRIPTION", message="Missing meta description.", url=page.url,
                            fix="Add a compelling description (140–160 chars) summarizing value + CTA."))

    # Images
    if page.images_total > 0 and page.images_missing_alt / max(1, page.images_total) > 0.3:
        issues.append(Issue(priority="P2", code="MANY_IMAGES_MISSING_ALT",
                            message=f"{page.images_missing_alt}/{page.images_total} images missing alt text.", url=page.url,
                            fix="Add descriptive alt text for important images (especially service/hero images)."))

    # Thin content
    if page.word_count < 200:
        issues.append(Issue(priority="P3", code="THIN_CONTENT",
                            message=f"Low visible word count (~{page.word_count}).", url=page.url,
                            fix="Add useful content: services, FAQs, proof, process, and location/service details."))

    return issues