SCHEMA = {
            "title": "QueryExtraction",
            "description": "Facts explicitly stated in the user's Australian tax question.",
            "type": "object",
            "properties": {
                "residency_status": {"type": "string"},
                "income_year": {"type": "string"},
                "has_help_debt": {"type": "boolean"},
                "jobs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "occupation": {"type": "string"},
                            "income_amount": {"type": "integer"},
                            "employment_type": {"type": "string"},
                            "is_work_from_home": {"type": "boolean"}
                        }
                    }
                },
                "deductions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Canonical deduction name, snake_case, e.g. working_from_home, car_and_travel, clothing_and_laundry, self_education, tools_and_equipment."
                            },
                            "additional_context": {
                                "type": "object",
                                "description": "Facts the user stated about this deduction (hours/week, cost, etc.)."
                            }
                        },
                        "required": ["name"]
                    }
                }
            }
        }

def extract_query(query: str) -> str:
    