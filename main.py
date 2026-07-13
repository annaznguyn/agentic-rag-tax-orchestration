from config.sources import SOURCES

from src.ingestion.fetch import fetch
from src.ingestion.clean import clean
from src.ingestion.chunk import chunk
from src.ingestion.store import store
from src.ingestion.store import get_store


def main():
    src = SOURCES[0]
    text, title = clean(fetch(src["url"]))

    docs = chunk(text, title, src["url"], src["income_year"])
    store(docs)

    print(f"stored {len(docs)} chunks from {title}")
    for doc in get_store().similarity_search("electricity costs working from home", k=3):
        print(doc.metadata["chunk_index"], "|", doc.page_content[:80])

if __name__ == "__main__":
    main()