from config.sources import SOURCES

from src.ingestion.fetch import fetch
from src.ingestion.clean import clean
from src.ingestion.chunk import chunk
from src.ingestion.store import store
from src.ingestion.store import get_store


def ingest() -> None:
    for src in SOURCES:
        text, title = clean(fetch(src["url"]))

        chunks = chunk(text, title, src["url"], src["income_year"])
        store(chunks)
        print(f"stored {len(chunks)} chunks from {title}")

def main():
    ingest()

if __name__ == "__main__":
    main()