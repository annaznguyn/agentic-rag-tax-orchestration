from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


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