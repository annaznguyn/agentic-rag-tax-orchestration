import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document

from src.ingestion.store import get_store


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def retrieve_context(query: str) -> List[str]:
    closest_docs = get_store().similarity_search(query, k=3)

    context = []
    for i, doc in enumerate(closest_docs, 1):
        context.append(f'Source {i}:\nTitle: {doc.metadata['title']}\nurl: {doc.metadata['url']}\nIncome Year: {doc.metadata['income_year']}\nContent: {doc.page_content}')

    return context

def get_prompt(context: List[str], query: str) -> str:
    context = '\n\n'.join(context)
    
    prompt = f"""
    You help people answer questions about Australian tax by pointing them to relevant ATO guidance. You never give tax advice or confirm a tax position. Always end your answer with: 'Disclaimer: I'm not a registered tax agent. Confirm with a registered tax agent before claiming.'.

    You are given a question and a context of tax documents.
    Use the context to answer the question. Every claim must cite its source as [N] where N is the source number. At the end, list each cited source's title and URL.
    If you can't answer the question based on the given context, say "I don't know".
    Do not make up an answer. Do not use any information that is not in the context.
    If the question is not related to tax, say "I'm sorry, I can only answer questions about tax."

    You are given the following context: 
    {context}

    Question: {query}
    """

    return prompt

def get_response(prompt: str) -> str:
    model = ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        api_key=GEMINI_API_KEY
    )

    response = model.invoke(prompt)
    return response.text