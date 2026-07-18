from config.sources import SOURCES

from src.ingestion.fetch import fetch
from src.ingestion.clean import clean
from src.ingestion.chunk import chunk
from src.ingestion.store import store
from src.ingestion.store import get_store

from src.retrieval.get_response import get_response
from src.retrieval.get_response import get_prompt


def ingest():
    for src in SOURCES:
        text, title = clean(fetch(src["url"]))

        chunks = chunk(text, title, src["url"], src["income_year"])
        store(chunks)
        print(f"stored {len(chunks)} chunks from {title}")

def retrieve(query: str) -> str:
    prompt = get_prompt(query)
    response = get_response(prompt)

    return response

def main():
    # ingest()

    query = "What is the work from home deduction for the year 2025?"

    response = retrieve(query)
    print(response)

if __name__ == "__main__":
    main()