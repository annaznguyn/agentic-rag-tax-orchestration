def confirm_user(suggestions: dict) -> list[dict]:
    accepted_suggestions = []

    for s in suggestions:
        print(f'\n{s["name"]}: {s['reason']}\n')
        user_input = input('Include this deduction? (y/n): ').strip().lower()
        if user_input == 'y':
            accepted_suggestions.append(s)

    return accepted_suggestions