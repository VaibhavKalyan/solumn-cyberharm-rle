"""Existing company record ownership checks."""

def allowed(accounts, employee_id, owner_id):
    return employee_id in accounts and employee_id == owner_id


def report(accounts):
    return [{"employee_id": key, "subject": value["subject"]}
            for key, value in sorted(accounts.items())]
