from src.agent.state import State
from src.retrieval.get_response import retrieve_context


def build_query(deduction: dict, user: dict) -> str:
    occupations = ", ".join(j.get("occupation", "") for j in user.get("jobs", []))
    context_bits = " ".join(str(v) for v in deduction.get("additional_context", {}).values())
    income_year = user.get("income_year", "")

    parts = [
        deduction["name"].replace("_", " "),
        "deduction",
        occupations,
        context_bits,
        income_year,
    ]

    return " ".join(p for p in parts if p).strip()

def retrieve(state: State) -> dict:
    user = state["user"]

    deductions = []
    for d in state["deductions"]:
        deduction = dict(d)

        if not deduction.get("ato_context"):
            query = build_query(deduction, user)
            deduction["ato_context"] = retrieve_context(query)

        deductions.append(deduction)

    return {"deductions": deductions}