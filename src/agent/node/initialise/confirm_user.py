from langgraph.graph import END

from src.agent.state import State


def confirm_user(state: State) -> dict:
    accepted_suggestions = []

    for s in state.get("suggestions", []):
        print(f'\n{s["name"]}: {s.get("reason", "")}\n')
        user_input = input('Include this deduction? (y/n): ').strip().lower()
        if user_input == 'y':
            accepted_suggestions.append(s)

    return {"accepted": accepted_suggestions}

def route_after_confirm(state: State) -> str:
    # user accepted at least one suggestion -> add them; otherwise finish
    if state.get("accepted"):
        return "add_suggestions"
    return END
