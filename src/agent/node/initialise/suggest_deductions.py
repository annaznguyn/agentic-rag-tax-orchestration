import os
import dotenv
import json

from langchain_google_genai import ChatGoogleGenerativeAI

from src.agent.state import State


dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


SUGGESTION_SCHEMA = {
    "title": "DeductionSuggestions",
    "description": "Additional deductions the user may be eligible for.",
    "type": "object",
    "properties": {
        "suggestions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Canonical snake_case name."},
                    "reason": {"type": "string", "description": "Short why-relevant note."},
                },
                "required": ["name"],
            },
        }
    },
}

def get_prompt(state: State) -> str:
    existing_deductions = [d["name"] for d in state["deductions"]]

    prompt = f"""
    You suggest ADDITIONAL Australian tax deductions the user may be eligible for,
    based on their profile. Only suggest deductions that are plausibly relevant to
    their occupation(s) and work situation.

    Rules:
    - Do NOT suggest any deduction already identified: {existing_deductions}
    - Do not invent facts about the user.
    - Use canonical snake_case names (e.g. working_from_home, car_and_travel,
      clothing_and_laundry, self_education, tools_and_equipment).

    User profile:
    {json.dumps(state["user"], indent=2)}

    Original question: {state["query"]}
    """

    return prompt

def suggest_deductions(state: State) -> dict:
    prompt = get_prompt(state)

    model = ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        api_key=GEMINI_API_KEY
    ).with_structured_output(SUGGESTION_SCHEMA)

    response = model.invoke(prompt)

    return response