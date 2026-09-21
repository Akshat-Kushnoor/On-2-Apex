import hashlib
import re
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

LEGAL_SUFFIXES_REGEX = re.compile(
    r"\b(llc|inc|corp|corporation|pvt\s+ltd|private\s+limited|ltd|limited|technologies|technology|services|solutions|software)\b",
    re.IGNORECASE,
)

TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "ref",
    "fbclid",
    "gclid",
    "trackingid",
    "tracking_id",
    "sessionId",
    "session_id",
}

BRAND_MAP = {
    "google": "Google",
    "alphabet": "Google",
    "microsoft": "Microsoft",
    "msft": "Microsoft",
    "amazon": "Amazon",
    "aws": "Amazon",
    "meta": "Meta",
    "facebook": "Meta",
    "apple": "Apple",
    "netflix": "Netflix",
    "uber": "Uber",
}


def normalize_company(company: str) -> str:
    if not company:
        return "Unknown"
    cleaned = company.strip()
    lowered = cleaned.lower()
    for alias, standard in BRAND_MAP.items():
        if lowered == alias or lowered.startswith(alias + " "):
            return standard

    cleaned = LEGAL_SUFFIXES_REGEX.sub("", cleaned)
    cleaned = re.sub(r"[\s,\.-]+$", "", cleaned).strip()
    return cleaned if cleaned else company.strip()


def normalize_title(title: str) -> str:
    if not title:
        return "Untitled Role"
    cleaned = title.strip()
    cleaned = re.sub(r"\[.*?\]|\(.*?\)", "", cleaned)
    cleaned = re.sub(r"^(hiring\s+for|urgent\s+requirement:?|wanted:?)\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if cleaned else title.strip()


def canonicalize_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    try:
        parsed = urlparse(url.strip())
        if not parsed.netloc:
            return url.strip()
        filtered_queries = [
            (k, v) for k, v in parse_qsl(parsed.query)
            if k.lower() not in TRACKING_PARAMS
        ]
        clean_query = urlencode(filtered_queries)
        clean_path = parsed.path.rstrip("/")
        return urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            clean_path,
            parsed.params,
            clean_query,
            "",
        ))
    except Exception:
        return url.strip()


def calculate_dedup_hash(
    normalized_company: str,
    normalized_title: str,
    canonical_url: Optional[str] = None,
    location: Optional[str] = None,
) -> str:
    norm_comp = normalized_company.strip().lower()
    norm_tit = normalized_title.strip().lower()
    norm_loc = (location or "").strip().lower()
    norm_url = (canonical_url or "").strip().lower()

    if norm_url:
        key = f"{norm_comp}|{norm_tit}|{norm_url}"
    else:
        key = f"{norm_comp}|{norm_tit}|{norm_loc}"

    return hashlib.sha256(key.encode("utf-8")).hexdigest()
