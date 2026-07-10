import hashlib
import time
import requests

from config.config import DATA_DIR

def fetch(url: str) -> str:
    cache_file = DATA_DIR / f'{hashlib.sha256(url.encode()).hexdigest()}.html'

    if cache_file.exists():
        return cache_file.read_text()

    res = requests.get(
        url, 
        headers={
            "User-Agent": "tax-orchestrator/1.0",
        },
        timeout=30)
    res.raise_for_status()

    cache_file.write_text(res.text)

    time.sleep(2) # each cache miss creates a new request -> without sleep, those requests might hit the server's rate limit
    
    return res.text


if __name__ == "__main__":
    from config.sources import SOURCES
    for source in SOURCES:
        print(fetch(source["url"]), '\n\n')