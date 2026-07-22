from src.agent.state import State, User, Job, DeductionItem


def create_state(extracted_data: dict, query: str = "") -> State:
    jobs = []
    deductions = []

    user = User(
        residency_status=extracted_data.get("residency_status", ""),
        income_year=extracted_data.get("income_year", ""),
        has_help_debt=extracted_data.get("has_help_debt", False),
        jobs=jobs,
        extra_info={},
    )

    for job in extracted_data.get("jobs", []):
        jobs.append(Job(
            occupation=job.get("occupation", ""),
            income_amount=job.get("income_amount", 0),
            employment_type=job.get("employment_type", ""),
            is_work_from_home=job.get("is_work_from_home", False),
        ))

    for deduction in extracted_data.get("deductions", []):
        deductions.append(DeductionItem(
            name=deduction.get("name", ""),
            status="todo",
            ato_context=[],
            additional_context=deduction.get("additional_context", {}),
            missing_context={},
        ))

    return State(
        user=user,
        deductions=deductions,
        query=query,
        final_responses=[],
        next="",
    )
