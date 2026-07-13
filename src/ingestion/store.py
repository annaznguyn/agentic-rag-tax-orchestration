import hashlib
import os

from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

from dotenv import load_dotenv


load_dotenv()

def get_store() -> PGVector:
    return PGVector(
        embeddings=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2"),
        collection_name="tax_orchestrator",
        connection=os.getenv("DATABASE_URL")
    )


def store(docs: list[Document]) -> None:
    ids = []

    for d in docs:
        hash = hashlib.sha256(f'{d.metadata['url']}|{d.metadata['chunk_index']}|{d.page_content}'.encode()).hexdigest()
        ids.append(hash)

    get_store().add_documents(docs, ids=ids)