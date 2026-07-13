import json
import re

from bs4 import BeautifulSoup


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
    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
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
            if _find_page_content(val):
                return _find_page_content(val)
    elif isinstance(node, list):
        for item in node:
            if _find_page_content(item):
                return _find_page_content(item)
    
    return None