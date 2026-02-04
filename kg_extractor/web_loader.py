import re
from typing import Tuple

import requests
from bs4 import BeautifulSoup

try:
    import trafilatura
except ImportError:  # pragma: no cover - optional dependency
    trafilatura = None


def fetch_main_text(url: str, timeout: int = 20) -> Tuple[str, str]:
    """Fetch raw HTML and extract main text content."""
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    html = response.text

    if trafilatura:
        extracted = trafilatura.extract(html, url=url)
        if extracted:
            return extracted.strip(), html

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip(), html
