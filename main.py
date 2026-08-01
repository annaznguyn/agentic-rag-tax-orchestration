from config.sources import SOURCES

from src.ingestion.fetch import fetch
from src.ingestion.clean import clean
from src.ingestion.chunk import chunk
from src.ingestion.store import store
from src.ingestion.store import get_store

from src.retrieval.get_response import get_response
from src.retrieval.get_response import get_prompt as get_response_prompt
from src.retrieval.get_response import retrieve_context

from src.agent.graph import build_graph


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

    query = "Can I claim rent for my home office? I'm a software engineer and work from home."

    initial_state = {
        "user": {},
        "deductions": [],
        "query": query,
        "final_responses": [],
        "next": "",
        "suggestions": [],
        "accepted": [],
    }

    graph = build_graph()
    final_state = graph.invoke(initial_state)
    print(final_state)

if __name__ == "__main__":
    main()