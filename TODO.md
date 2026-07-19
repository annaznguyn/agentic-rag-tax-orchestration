# Later / optimisations

1. [Heading-aware splitting in `chunk.py`](#1-heading-aware-splitting-in-chunkpy)
2. [Redis caching in `fetch.py`](#2-redis-caching-in-fetchpy)
3. [Expose the agent as an API](#3-expose-the-agent-as-an-api)
4. [LangGraph checkpointer for the agent](#4-langgraph-checkpointer-for-the-agent)

---

## 1. Heading-aware splitting in `chunk.py`

**Why:** `chunk()` splits on character count alone, so chunks cut across
sections and headings get separated from their body. ATO pages are short
sections under `h2`/`h3`, so splitting per section retrieves better.

**Steps:**

1. `clean.py`: keep heading structure — prefix `h2` text with `## ` and
   `h3` text with `### `.
2. `chunk.py`: split on headings first (`MarkdownHeaderTextSplitter`),
   then character-split only sections longer than `chunk_size`.
3. Prepend the section heading to each chunk's `page_content` and store
   it as `section` in metadata.
4. Shrink or drop `chunk_overlap` — it mainly compensated for mid-topic
   cuts.

**Verify:**

1. Run `python -m src.ingestion.chunk`.
2. Every chunk starts with its section heading; no dangling headings.
3. Test a query like "record keeping fixed rate" — the matching chunk
   should be the whole relevant section.

## 2. Redis caching in `fetch.py`

**Why:** practice with Redis; gives TTL-based expiry (file cache never
expires) and a shared cache if the app ever runs as multiple processes.

**Steps:**

1. Add `redis` service to `docker-compose.yml` and `redis` to
   `requirements.txt`.
2. In `fetch()`: try Redis by URL hash key first; on miss, download and
   `SET` with a TTL (e.g. 7 days).
3. Keep the file cache as fallback if Redis is down.

## 3. Expose the agent as an API

**Why:** makes the RAG pipeline usable outside the terminal (web UI, other
apps), and is the point where Redis/shared caching starts to matter.

**Steps:**

1. FastAPI app with a `POST /ask` endpoint: question in, answer +
   source citations out.
2. Add the API service to `docker-compose.yml` alongside `db`.
3. Later: streaming responses, auth, rate limiting.

## 4. LangGraph checkpointer for the agent

**Why:** persist agent state (`Job`, `DeductionItem`, message history)
across turns and restarts so a conversation can pause and resume, and so
a crash mid-run doesn't lose progress. Enables multi-turn threads and
human-in-the-loop review.

**Steps:**

1. Add `langgraph` and `langgraph-checkpoint-postgres` to
   `requirements.txt`.
2. Reuse the existing Postgres `db` service — construct a
   `PostgresSaver` (or `AsyncPostgresSaver`) from the same connection
   string, and call `.setup()` once to create the checkpoint tables.
3. Pass the saver as `checkpointer=` when compiling the `StateGraph`,
   and invoke with a `thread_id` in `config` so each conversation gets
   its own persisted thread.

**Verify:**

1. Run the agent, interrupt it mid-conversation, then re-invoke with the
   same `thread_id` — earlier state and messages are restored.
2. Checkpoint rows appear in Postgres for the thread.
