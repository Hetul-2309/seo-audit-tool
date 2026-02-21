from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

def build_pdf(report: dict) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    def text(x, y, s, size=11):
        c.setFont("Helvetica", size)
        c.drawString(x, y, s[:140])

    y = h - 2 * cm
    text(2*cm, y, "SEO Quick Audit Report", 18); y -= 1.0*cm
    text(2*cm, y, f"Site: {report.get('site', {}).get('url','')}", 12); y -= 0.7*cm
    kw = report.get("inputs", {}).get("target_keyword")
    if kw:
        text(2*cm, y, f"Target keyword: {kw}", 12); y -= 0.7*cm

    def section(title):
        nonlocal y
        y -= 0.5*cm
        c.setFont("Helvetica-Bold", 13)
        c.drawString(2*cm, y, title)
        y -= 0.6*cm
        c.setFont("Helvetica", 11)

    section("Priority Fix List")
    pf = report.get("priority_fixes", {})
    for pr in ("P1", "P2", "P3"):
        issues = pf.get(pr, [])
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, f"{pr} ({len(issues)})"); y -= 0.5*cm
        c.setFont("Helvetica", 10)
        for i, it in enumerate(issues[:20], start=1):
            line = f"{i}. {it.get('message','')}  [{it.get('url','')}]"
            c.drawString(2*cm, y, line[:160]); y -= 0.42*cm
            fix = it.get("fix")
            if fix:
                c.drawString(2.5*cm, y, f"Fix: {fix}"[:160]); y -= 0.42*cm
            if y < 2*cm:
                c.showPage()
                y = h - 2*cm

    section("Per-Page Suggestions (Top 10)")
    pages = report.get("pages", [])[:10]
    for p in pages:
        url = p.get("url","")
        st = p.get("suggestions", {}).get("suggested_title")
        sd = p.get("suggestions", {}).get("suggested_meta_description")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, y, url[:160]); y -= 0.42*cm
        c.setFont("Helvetica", 10)
        if st:
            c.drawString(2.5*cm, y, f"Title: {st}"[:160]); y -= 0.42*cm
        if sd:
            c.drawString(2.5*cm, y, f"Desc: {sd}"[:160]); y -= 0.42*cm
        y -= 0.2*cm
        if y < 2*cm:
            c.showPage()
            y = h - 2*cm

    c.save()
    return buf.getvalue()