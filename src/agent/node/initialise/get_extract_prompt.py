def get_extract_prompt(query: str) -> str:
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