import re
import socket
from urllib.parse import urlparse, urljoin, urldefrag

PRIVATE_NETS = (
    "10.", "127.", "169.254.", "172.16.", "172.17.", "172.18.", "172.19.",
    "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.",
    "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.", "192.168."
)

def normalize_url(base: str, href: str) -> str | None:
    if not href:
        return None
    href = href.strip()
    if href.startswith(("mailto:", "tel:", "javascript:")):
        return None
    full = urljoin(base, href)
    full, _frag = urldefrag(full)  # remove #fragment
    return full

def same_host(a: str, b: str) -> bool:
    return urlparse(a).netloc.lower() == urlparse(b).netloc.lower()

def is_http_url(u: str) -> bool:
    return urlparse(u).scheme in ("http", "https")

def is_private_host(url: str) -> bool:
    """
    Basic SSRF guard: blocks private IP targets.
    (Not perfect, but good for MVP. For production, harden further.)
    """
    host = urlparse(url).hostname
    if not host:
        return True
    # If host is already an IP
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
        return host.startswith(PRIVATE_NETS)
    try:
        ip = socket.gethostbyname(host)
        return ip.startswith(PRIVATE_NETS)
    except Exception:
        return True