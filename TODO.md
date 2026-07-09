# Later / optimisations

## Heading-aware splitting in `chunk.py`

Why: `chunk()` splits on character count alone, so chunks cut across
sections and headings get separated from their body. ATO pages are short
sections under `h2`/`h3`, so splitting per section retrieves better.

Steps:

1. `clean.py`: keep heading structure — prefix `h2` text with `## ` and
   `h3` text with `### `.
2. `chunk.py`: split on headings first (`MarkdownHeaderTextSplitter`),
   then character-split only sections longer than `chunk_size`.
3. Prepend the section heading to each chunk's `page_content` and store
   it as `section` in metadata.
4. Shrink or drop `chunk_overlap` — it mainly compensated for mid-topic
   cuts.

Verify:

1. Run `python -m src.ingestion.chunk`.
2. Every chunk starts with its section heading; no dangling headings.
3. Test a query like "record keeping fixed rate" — the matching chunk
   should be the whole relevant section.

## Local download cache for `fetch.py`

Why: `fetch()` hits the network on every run. Cache pages locally so
re-running ingestion is instant.

Steps:

1. Cache path: `data/raw/<sha256(url)>.html`. Create `data/raw/` with
   `mkdir(parents=True, exist_ok=True)`.
2. Cache hit: read the file and return it. No network call, no sleep.
3. Cache miss: download, `raise_for_status()` (never cache an error
   page), write `resp.text`, `time.sleep(2)`, return.
4. Force a re-fetch by deleting the cache file. No TTL logic.

Verify:

1. Run `python -m src.ingestion.fetch` twice.
2. First run: slow (~2s per page), creates 4 files in `data/raw/`.
3. Second run: near-instant, file count unchanged.

Bonus: if ATO bot protection blocks us, save pages manually from the
browser into `data/raw/` under the hash filename — the pipeline won't
know the difference.
