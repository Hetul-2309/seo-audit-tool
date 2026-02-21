from fastapi import FastAPI, Query, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from audit.crawler import run_audit
from audit.pdf_report import build_pdf

app = FastAPI(title="SEO Quick Audit Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PdfRequest(BaseModel):
    report: dict

@app.get("/api/audit")
def api_audit(
    url: str = Query(..., description="Homepage URL"),
    target_keyword: str | None = Query(None),
    max_pages: int = Query(25, ge=1, le=200),
    max_depth: int = Query(2, ge=0, le=5),
):
    report = run_audit(url=url, target_keyword=target_keyword, max_pages=max_pages, max_depth=max_depth)
    return report

@app.post("/api/pdf")
def api_pdf(payload: PdfRequest = Body(...)):
    pdf_bytes = build_pdf(payload.report)
    return Response(content=pdf_bytes, media_type="application/pdf")