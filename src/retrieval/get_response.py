import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_response(prompt: str) -> str:
    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        api_key=GEMINI_API_KEY
    )

    response = model.invoke(prompt)
    return response.text  # response.text instead of response.content to get the text of the response, response.content returns bytes
    
if __name__ == "__main__":
    prompt = "What is the capital of Vietnam?"
    response = get_response(prompt)
    print(response)