import requests

from config.sources import SOURCES

def fetch(url: str) -> str:
    res = requests.get(
        url, 
        headers={
            "User-Agent": "tax-orchestrator/1.0",
        },
        timeout=30)
    res.raise_for_status()
    return res.text

if __name__ == "__main__":
    for s in SOURCES:
        html = fetch(s["url"])
        print(f'{html}\n\n')