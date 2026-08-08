import os
import dotenv
import json

from langchain_google_genai import ChatGoogleGenerativeAI

from src.agent.state import State
from src.agent.node.initialise.create_state import create_deduction


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
                    "reason": {"type": "string", "description": "Short note on why this deduction is worth exploring for the user's situation. Frame it as a suggestion to check, not an eligibility decision, and make clear this is not advice from a registered tax agent (end with: 'Confirm eligibility with a registered tax agent.')."},
                },
                "required": ["name"],
            },
        }
    },
}

def get_prompt(state: State) -> str:
    existing_deductions = [d["name"] for d in state["deductions"]]

    prompt = f"""
    You suggest ADDITIONAL Australian tax deductions that may be worth exploring,
    based on their profile. Only suggest deductions that are plausibly relevant to
    their occupation(s) and work situation.

    You are an orchestrator that points to deductions worth checking. You are NOT a
    registered tax agent and you do NOT give tax advice or confirm eligibility.

    Rules:
    - Do NOT suggest any deduction already identified: {existing_deductions}
    - Do not invent facts about the user.
    - Use canonical snake_case names.
    - Write each reason as WHY it's worth exploring for their situation. Do NOT
      assert the user is eligible or can claim it. Phrase it as a suggestion to
      check, and end the reason with: 'Confirm eligibility with a registered tax agent.'

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

    return {"suggestions": response.get("suggestions", [])}

def add_suggestions(state: State) -> dict:
    existing_deductions = {d["name"] for d in state["deductions"]}

    deductions = list(state["deductions"])
    for s in state.get("accepted", []):
        if s["name"] not in existing_deductions:
            deductions.append(create_deduction(s["name"], {}))
            existing_deductions.add(s["name"])

    return {"deductions": deductions}