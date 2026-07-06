import json
import re

from bs4 import BeautifulSoup

from config.sources import SOURCES
from src.ingestion.fetch import fetch

def clean(html: str) -> tuple[str, str]:
    """
    Clean the HTML content of a page.

    Args:
        html: The HTML content of the page.

    Returns:
        A tuple containing the text content and the title of the page.
    """
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html, re.S,
    )
    data = json.loads(m.group(1))
    route = data["props"]["pageProps"]["layoutData"]["sitecore"]["route"]
    title = route["fields"]["pageTitle"]["value"]
    body_html = _find_page_content(route)
    soup = BeautifulSoup(body_html, "html.parser")
    # Extract text per block element (space-separated within each block) so
    # inline tags like <a> don't split sentences across lines.
    blocks = [
        el.get_text(" ", strip=True)
        for el in soup.find_all(["h2", "h3", "p", "li"])
    ]
    text = "\n\n".join(b for b in blocks if b)
    return text, title

def _find_page_content(node: dict|list) -> str|None:
    """
    Walk the nested layout JSON (aka node tree) until the page content is found.

    Args:
        node: The node to find the page content in.

    Returns:
        The page content.
    """
    if isinstance(node, dict):
        if node.get("componentName") == "PageContent":
            return node["fields"]["contentBody"]["value"]
        
        for val in node.values():
            found = _find_page_content(val)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _find_page_content(item)
            if found:
                return found
    
    return None

if __name__ == "__main__":
    text, title = clean(fetch(SOURCES[0]["url"]))
    print(f"=== {title} ===")
    print(text[:2000])