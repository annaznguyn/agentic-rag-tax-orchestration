import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document

from src.ingestion.store import get_store


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_prompt(query: str) -> str:
    closest_docs = get_store().similarity_search(query, k=3)

    context = ''
    for doc in closest_docs:
        context += f'Content: {doc.page_content}\n'
    
    prompt = f"""
    You are a helpful tax assistant that can answer questions about tax.

    You are given a question and a context of tax documents.
    Use the context to answer the question.
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
    
if __name__ == "__main__":
    query = "What is the work from home deduction for the year 2025?"

    prompt = get_prompt(query)
    print(prompt)
    
    response = get_response(prompt)
    print(response)