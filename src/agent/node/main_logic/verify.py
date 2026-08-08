import os
import dotenv
import json

from langchain_google_genai import ChatGoogleGenerativeAI

from src.agent.state import State


dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


VERIFY_SCHEMA = {
    "title": "DeductionVerification",
    "description": "Eligibility assessment for a single deduction, grounded strictly in the provided ATO context.",
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["eligible", "ineligible", "missing_info", "no_context"],
            "description": (
                "eligible: the ATO context supports the claim given the facts the user provided. "
                "ineligible: the ATO context rules the claim out given those facts. "
                "missing_info: the context is relevant but the decision depends on a fact the "
                "user has not provided yet. "
                "no_context: the context does not cover this deduction at all, so no amount of "
                "extra information from the user would let you decide from it."
            ),
        },
        "reason": {
            "type": "string",
            "description": (
                "Short explanation for the status, grounded ONLY in the provided ATO context. "
                "Cite the context as [N] where N is the source number. Do not give tax advice or "
                "assert a final tax position; end with: 'Confirm with a registered tax agent.'"
            ),
        },
        "missing_context": {
            "type": "array",
            "description": "Only when status is missing_info: the specific facts still needed to decide. Leave empty for every other status.",
            "items": {
                "type": "object",
                "properties": {
                    "field": {
                        "type": "string",
                        "description": "Short snake_case key for the fact, e.g. hours_per_week, item_cost, is_place_of_business.",
                    },
                    "question": {
                        "type": "string",
                        "description": "The question to ask the user to obtain this fact.",
                    },
                },
                "required": ["field", "question"],
            },
        },
    },
    "required": ["status", "reason"],
}

def get_prompt(deduction: dict, user: dict) -> str:
    ato_context = "\n\n".join(deduction.get("ato_context", []))

    prompt = f"""
    You assess whether a single Australian tax deduction is supported by the given ATO
    guidance, for this user's situation. You are NOT a registered tax agent and you do
    NOT give tax advice or confirm a final tax position — you only report what the ATO
    context supports.

    Reason ONLY from the ATO context provided below. Do not use outside knowledge and do
    not invent rules. Every claim in your reason must cite the context as [N].

    Decide the status:
    - eligible: the ATO context clearly supports the claim given the facts the user stated.
    - ineligible: the ATO context clearly rules the claim out given the facts the user stated.
    - missing_info: the context is relevant but the outcome depends on a fact the user has
      NOT provided. List each needed fact in missing_context with a short snake_case field
      and a plain-English question.
    - no_context: the context is about some other topic and does not cover this deduction.
      Use this whenever the context contains no rules about this deduction, even if it looks
      superficially related. Do not stretch an unrelated rule to fit, and do not ask for more
      information — no answer from the user could make this context decide the deduction.
      Leave missing_context empty.

    Deduction: {deduction.get("name", "")}

    Facts the user provided about this deduction:
    {json.dumps(deduction.get("additional_context", {}), indent=2)}

    User profile:
    {json.dumps(user, indent=2)}

    ATO context:
    {ato_context}
    """

    return prompt

def verify_deduction(deduction: dict, user: dict) -> dict:
    # nothing relevant was retrieved -> can't assess from context, don't guess
    if not deduction.get("ato_context"):
        return {
            "status": "no_context",
            "reason": (
                "No relevant ATO guidance was retrieved for this deduction, so its "
                "eligibility can't be assessed yet. Confirm with a registered tax agent."
            ),
            "missing_context": {},
        }

    prompt = get_prompt(deduction, user)

    model = ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        api_key=GEMINI_API_KEY
    ).with_structured_output(VERIFY_SCHEMA)

    response = model.invoke(prompt)

    status = response["status"]

    # normalise the missing_context list into a {field: question} dict for the state
    missing_context = {
        item["field"]: item["question"]
        for item in response.get("missing_context", [])
        if item.get("field") and item.get("question")
    }

    # questions are only answerable when the context actually covers the deduction,
    # otherwise the answer comes back and still can't be assessed against this context
    if status != "missing_info":
        missing_context = {}

    return {
        "status": status,
        "reason": response["reason"],
        "missing_context": missing_context,
    }

def verify(state: State) -> dict:
    user = state["user"]

    deductions = []
    for d in state["deductions"]:
        deduction = dict(d)
        result = verify_deduction(deduction, user)

        deduction["status"] = result["status"]
        deduction["reason"] = result["reason"]
        deduction["missing_context"] = result["missing_context"]

        deductions.append(deduction)

    return {"deductions": deductions}
