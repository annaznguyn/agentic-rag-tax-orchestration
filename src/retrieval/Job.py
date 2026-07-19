from typing import TypedDict

class Job(TypedDict):
    occupation: str,
    income: int,
    employment_type: str,
    is_work_from_home: bool