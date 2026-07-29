import os
import dotenv

from langchain_google_genai import ChatGoogleGenerativeAI


dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EXTRACTION_SCHEMA = {
            "title": "QueryExtraction",
            "description": "Facts explicitly stated in the user's Australian tax question.",
            "type": "object",
            "properties": {
                "residency_status": {"type": "string"},
                "income_year": {"type": "string"},
                "has_help_debt": {"type": "boolean"},
                "jobs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "occupation": {"type": "string"},
                            "income_amount": {"type": "integer"},
                            "employment_type": {"type": "string"},
                            "is_work_from_home": {"type": "boolean"}
                        }
                    }
                },
                "deductions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Canonical deduction name, snake_case, e.g. working_from_home, car_and_travel, clothing_and_laundry, self_education, tools_and_equipment."
                            },
                            "additional_context": {
                                "type": "object",
                                "description": "Facts the user stated about this deduction (hours/week, cost, etc.)."
                            }
                        },
                        "required": ["name"]
                    }
                }
            }
        }

def get_prompt(query: str) -> str:
    prompt = f"""
    You extract structured facts from an Australian tax deduction question.

    Rules:
    - Capture only what the user explicitly states.
    - Do not infer, guess, or add deductions the user did not mention.
    - Omit any field that is not stated in the query.
    - For each deduction, use a canonical snake_case name (e.g. working_from_home,
      car_and_travel, clothing_and_laundry, self_education, tools_and_equipment).
    - For each deduction, put the specific details the user stated into
      additional_context. Always capture the exact kind of expense they named
      (e.g. "rent", "electricity", "internet", "phone", "equipment") under an
      "expense_type" key, plus any amounts, hours per week, or dates. Keep the
      user's own wording so later steps don't lose nuance (e.g. rent is an
      occupancy expense, which is treated differently from normal running costs).

    Example:
    Query: "Can I claim rent for my home office?"
    -> deduction name: "working_from_home"
    -> additional_context: {{"expense_type": "rent"}}

    Question: {query}
    """

    return prompt

def extract_query(query: str) -> dict:
    prompt = get_prompt(query)
    
    model = ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        api_key=GEMINI_API_KEY
    ).with_structured_output(EXTRACTION_SCHEMA)

    print("extracting...")
    extracted_data = model.invoke(prompt)  # return raw dict for create_state.py to create State objects

    return extracted_data