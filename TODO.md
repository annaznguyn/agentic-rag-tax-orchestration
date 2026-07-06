# Later / optimisations

## Local download cache for `fetch.py`

Right now `fetch()` hits the network on every run. Add a local cache so
re-running ingestion doesn't re-download pages we already have.

How it should work:

1. Cache file path: `data/raw/<sha256(url)>.html`
   - `hashlib.sha256(url.encode()).hexdigest()` for the filename
   - create `data/raw/` with `mkdir(parents=True, exist_ok=True)` so it
     works on a fresh clone
2. Cache hit: file exists -> read and return it. No network call, no sleep.
3. Cache miss: download, `raise_for_status()` (so we never cache an error
   page), write `resp.text` to the cache file, `time.sleep(2)`, return it.
4. To force a re-fetch of an updated page: just delete its cache file.
   No TTL/expiry logic needed.

How to verify: run `python -m src.ingestion.fetch` twice.
First run is slow (~2s per page) and creates 4 files in `data/raw/`.
Second run is near-instant and the file count doesn't change.

Bonus this unlocks: if ato.gov.au's bot protection (Akamai) starts blocking
requests, we can save pages manually from the browser into `data/raw/`
under the expected hash filename, and the rest of the pipeline never knows
the difference.
