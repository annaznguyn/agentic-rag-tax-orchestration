import requests

def fetch(url: str) -> str:
    res = requests.get(
        url, 
        headers={
            "User-Agent": "tax-orchestrator/1.0",
        },
        timeout=30)
    res.raise_for_status()
    return res.text