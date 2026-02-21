from pydantic import BaseModel
from typing import List, Optional, Dict

class Issue(BaseModel):
    priority: str  # P1/P2/P3
    code: str
    message: str
    url: Optional[str] = None
    details: Optional[Dict] = None
    fix: Optional[str] = None

class PageData(BaseModel):
    url: str
    status: int
    title: str | None = None
    meta_description: str | None = None
    h1: List[str] = []
    headings: Dict[str, int] = {}
    images_total: int = 0
    images_missing_alt: int = 0
    internal_links: int = 0
    external_links: int = 0
    word_count: int = 0
    keyword_hits: Dict[str, int] = {}
    issues: List[Issue] = []
    suggestions: Dict[str, str] = {}
    speed_tips: List[str] = []