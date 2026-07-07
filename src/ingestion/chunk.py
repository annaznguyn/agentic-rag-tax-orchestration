from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.ingestion.clean import clean
from src.ingestion.fetch import fetch

from config.sources import SOURCES

def chunk(text: str, title: str, url: str, income_year: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200)
    chunks = splitter.split_text(text)

    documents = []
    for i in range(len(chunks)):
        documents.append(Document(
            page_content=chunks[i],
            metadata={
                "title": title,
                "url": url,
                "income_year": income_year,
                "chunk_index": i
            }
        ))
    
    return documents

if __name__ == "__main__":
    src = SOURCES[0]
    text, title = clean(fetch(src["url"]))

    docs = chunk(text, title, src["url"], src["income_year"])
    print(docs)