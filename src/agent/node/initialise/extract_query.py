def get_prompt(query: str) -> str:
    prompt = f"""
    You extract structured facts from an Australian tax deduction question.

    Rules:
    - Capture only what the user explicitly states.
    - Do not infer, guess, or add deductions the user did not mention.
    - Omit any field that is not stated in the query.
    - For each deduction, use a canonical snake_case name (e.g. working_from_home,
      car_and_travel, clothing_and_laundry, self_education, tools_and_equipment).

    Question: {query}
    """

    return prompt