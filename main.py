from config.sources import SOURCES

from src.ingestion.fetch import fetch
from src.ingestion.clean import clean
from src.ingestion.chunk import chunk
from src.ingestion.store import store
from src.ingestion.store import get_store

from src.retrieval.get_response import get_response
from src.retrieval.get_response import get_prompt as get_response_prompt
from src.retrieval.get_response import retrieve_context

from src.agent.node.initialise.extract import extract_query
from src.agent.node.initialise.create_state import create_state
from src.agent.node.initialise.get_extract_prompt import get_extract_prompt
from src.agent.node.initialise.get_suggestion_prompt import get_suggestion_prompt


def ingest():
    for src in SOURCES:
        text, title = clean(fetch(src["url"]))

        chunks = chunk(text, title, src["url"], src["income_year"])
        store(chunks)
        print(f"stored {len(chunks)} chunks from {title}")

def retrieve(query: str) -> str:
    context = retrieve_context(query)

    print(context)
    prompt = get_response_prompt(context, query)
    response = get_response(prompt)

    return response

def main():
    # ingest()

    # query = "What is the work from home deduction for the year 2025?"
    query = "Can I claim rent for my home office? I'm a software engineer and work from home."

    extract_query_prompt = get_extract_prompt(query)
    # print(extract_query_prompt)

    extracted_query = extract_query(extract_query_prompt)
    # print(extracted_query)

    state = create_state(extracted_query, query)
    print(state)


if __name__ == "__main__":
    main()