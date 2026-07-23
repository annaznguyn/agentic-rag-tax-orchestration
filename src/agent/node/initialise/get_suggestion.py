import os
import dotenv

from langchain_google_genai import ChatGoogleGenerativeAI


dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

