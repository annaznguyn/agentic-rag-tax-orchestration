from typing import TypedDict


class Job(TypedDict):
    occupation: str
    income_amount: int
    employment_type: str  # full time, part time, contract, etc.
    is_work_from_home: bool

class User(TypedDict):
    residency_status: str
    income_year: str
    has_help_debt: bool
    jobs: list[Job]
    extra_info: dict

class DeductionItem(TypedDict):
    name: str
    status: str               # todo / missing_info / eligible / ineligible
    ato_context: list[str]
    additional_context: dict  # additional context from user
    missing_context: dict     # missing context, to be asked by agent

# question to be asked by agent
class PendingQuestion(TypedDict):
    question: str
    category: str      # User/Job/DeductionItem
    ref: str           # which job/deduction item (empty for User)
    category: str      # field to be filled (e.g. employment_type)

class State(TypedDict):
    user: User
    deductions: list[DeductionItem]
    query: str
    final_responses: list[str]  # list of responses sent to user, excluding agent's questions
    next: str                   # router's next step