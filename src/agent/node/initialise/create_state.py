from src.agent.state import State, User, Job, DeductionItem


def create_deduction(name: str, additional_context: dict) -> DeductionItem:
    return DeductionItem(
        name=name,
        status="todo",
        ato_context=[],
        additional_context=additional_context or {},
        missing_context={},
        reason=""
    )

def create_state(extracted_data: dict, query: str) -> State:
    jobs = []
    deductions = []

    user = User(
        residency_status=extracted_data.get("residency_status", ""),
        income_year=extracted_data.get("income_year", ""),
        has_help_debt=extracted_data.get("has_help_debt", False),
        jobs=jobs,
        extra_info={},
    )

    for j in extracted_data.get("jobs", []):
        jobs.append(Job(
            occupation=j.get("occupation", ""),
            income_amount=j.get("income_amount", 0),
            employment_type=j.get("employment_type", ""),
            is_work_from_home=j.get("is_work_from_home", False),
        ))

    for d in extracted_data.get("deductions", []):
        deductions.append(create_deduction(d.get("name", ""), d.get("additional_context", {})))

    return State(
        user=user,
        deductions=deductions,
        query=query,
        final_responses=[],
        next="",
    )
