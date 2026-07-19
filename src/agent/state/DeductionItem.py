from typing import TypedDict


class DeductionItem(TypedDict):
    name: str
    is_deductible: bool
    status: str
    ato_context: dict
    additional_context: dict  # additional context from user
    missing_context: dict  # missing context, to be asked by agent