"""Minimal NCBI E-utilities client (public, free; no proprietary resources)."""
import os
import re
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

import requests

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


class PubMedClient:
    """Thin wrapper around esearch/efetch with polite rate limiting.

    Set NCBI_EMAIL (and optionally NCBI_API_KEY) as environment variables.
    Without an API key NCBI allows ~3 requests/second.
    """

    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        self.email = email or os.getenv("NCBI_EMAIL", "")
        self.api_key = api_key or os.getenv("NCBI_API_KEY", "")
        self.pause = 0.12 if self.api_key else 0.4
        self.session = requests.Session()

    def _params(self, extra: Dict) -> Dict:
        params = {"tool": "glp1-literature-strategy"}
        if self.email:
            params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key
        params.update(extra)
        return params

    def _request(self, endpoint: str, params: Dict, post: bool = False) -> requests.Response:
        url = BASE + endpoint
        for attempt in range(3):
            try:
                if post:
                    resp = self.session.post(url, data=self._params(params), timeout=60)
                else:
                    resp = self.session.get(url, params=self._params(params), timeout=60)
                resp.raise_for_status()
                time.sleep(self.pause)
                return resp
            except requests.RequestException:
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
        raise RuntimeError("unreachable")

    def count(self, term: str, mindate: str = None, maxdate: str = None) -> int:
        params = {"db": "pubmed", "term": term, "retmode": "json", "retmax": 0}
        if mindate and maxdate:
            params.update({"datetype": "pdat", "mindate": mindate, "maxdate": maxdate})
        data = self._request("esearch.fcgi", params).json()
        return int(data["esearchresult"]["count"])

    def search_ids(self, term: str, retmax: int = 500, mindate: str = None,
                   maxdate: str = None) -> List[str]:
        params = {"db": "pubmed", "term": term, "retmode": "json",
                  "retmax": retmax, "sort": "relevance"}
        if mindate and maxdate:
            params.update({"datetype": "pdat", "mindate": mindate, "maxdate": maxdate})
        data = self._request("esearch.fcgi", params).json()
        return data["esearchresult"]["idlist"]

    def fetch_records(self, pmids: List[str], batch: int = 100) -> List[Dict]:
        records: List[Dict] = []
        for i in range(0, len(pmids), batch):
            chunk = pmids[i:i + batch]
            resp = self._request(
                "efetch.fcgi",
                {"db": "pubmed", "id": ",".join(chunk), "retmode": "xml"},
                post=True,
            )
            records.extend(parse_pubmed_xml(resp.text))
        return records


def _text(node) -> str:
    return "".join(node.itertext()).strip() if node is not None else ""


def parse_pubmed_xml(xml_text: str) -> List[Dict]:
    """Parse PubMed efetch XML into flat dictionaries."""
    root = ET.fromstring(xml_text)
    out = []
    for art in root.findall(".//PubmedArticle"):
        abstract_parts = []
        for ab in art.findall(".//Abstract/AbstractText"):
            label = ab.get("Label")
            body = _text(ab)
            abstract_parts.append(f"{label}: {body}" if label else body)

        year = art.findtext(".//JournalIssue/PubDate/Year") or ""
        if not year:
            m = re.search(r"(19|20)\d{2}", art.findtext(".//JournalIssue/PubDate/MedlineDate") or "")
            year = m.group(0) if m else ""

        doi = ""
        for aid in art.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if aid.get("IdType") == "doi":
                doi = (aid.text or "").strip()

        out.append({
            "pmid": art.findtext(".//MedlineCitation/PMID") or "",
            "title": _text(art.find(".//ArticleTitle")),
            "abstract": " ".join(abstract_parts),
            "journal": art.findtext(".//Journal/Title") or "",
            "year": year,
            "language": art.findtext(".//Language") or "",
            "pub_types": "; ".join(pt.text or "" for pt in art.findall(".//PublicationType")),
            "doi": doi,
        })
    return out
