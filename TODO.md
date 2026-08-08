# Later / optimisations

1. [Heading-aware splitting in `chunk.py`](#1-heading-aware-splitting-in-chunkpy)
2. [Redis caching in `fetch.py`](#2-redis-caching-in-fetchpy)
3. [Expose the agent as an API](#3-expose-the-agent-as-an-api)
4. [LangGraph checkpointer for the agent](#4-langgraph-checkpointer-for-the-agent)
5. [Harden LLM calls (timeouts, retries, error handling)](#5-harden-llm-calls-timeouts-retries-error-handling)
6. [Flip the deduction/source mapping once the corpus grows](#6-flip-the-deductionsource-mapping-once-the-corpus-grows)

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

## 5. Harden LLM calls (timeouts, retries, error handling)

**Why:** `model.invoke()` in `extract.py` and `suggest_deductions.py` is a
synchronous network call with no timeout, so a stalled request (or a
missing/invalid `GEMINI_API_KEY`) makes `main.py` hang indefinitely
instead of failing with a clear error. A `try/except` alone doesn't help —
the code never raises, it just waits. The timeout is what turns "hangs
forever" into an error you can actually catch and handle.

**Steps:**

1. **Set a timeout (highest impact).** Pass `timeout=30` and cap
   `max_retries` (e.g. `2`) on every `ChatGoogleGenerativeAI` construction
   so stalled calls fail fast instead of hanging.
2. **Fail fast on missing config.** After `GEMINI_API_KEY = os.getenv(...)`,
   raise a clear `RuntimeError` if it's unset rather than letting `None`
   surface deep in the SDK.
3. **Centralise the model factory.** Both nodes build the same client — add
   a shared `get_model(schema=None, timeout=30, max_retries=2)` helper (e.g.
   `src/agent/llm.py`) so timeouts/retries stay consistent everywhere.
4. **Wrap calls in narrow try/except.** Catch specific errors (not bare
   `except:`), log context, then re-raise as a `RuntimeError` with the step
   name. Never silently return `{}` — that hides the failure downstream.
5. **Make the wait visible.** Print/log a short status before each LLM call
   ("Analysing your query...") so a CLI run shows progress and which step
   it's on.
6. **Retries with backoff for transient failures only.** `max_retries`
   covers basics; for finer control use `tenacity`. Only retry transient
   errors (timeouts, 429, 5xx) — never retry auth errors (401/403).

**Verify:**

1. Temporarily unset `GEMINI_API_KEY` — the program exits immediately with
   a clear message instead of hanging.
2. Simulate a slow/blocked network — the call raises a timeout after ~30s
   instead of running forever.
3. A normal run prints the per-step status lines before each LLM call.

## 6. Flip the deduction/source mapping once the corpus grows

**Why:** the plan is to tag each source in `config/sources.py` with the one
deduction it covers, and build the suggestion list from those tags. That
works while there are only a few pages. Once there are hundreds it stops
fitting: one ATO page can cover several deductions, and one deduction can
span many pages. One tag per URL can't say either of those things.

**Steps:**

1. Keep a list of deductions as the source of truth, instead of deriving
   it from the sources.
2. Point each source at the deductions it covers, so a page can belong to
   more than one.
3. Keep the retrieval filter working the same way — look up a deduction,
   search only its pages.

**Note:** same idea, just the other way up. It's a natural next step, not a
rewrite, so don't do it early.
