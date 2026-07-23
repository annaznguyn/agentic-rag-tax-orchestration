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