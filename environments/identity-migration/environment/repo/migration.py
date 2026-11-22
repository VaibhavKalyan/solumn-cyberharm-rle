"""Migration transaction logic: legacy prototype awaiting callback integration."""
import secrets
from urllib.parse import urlencode
from provider import ISSUER


def begin(db, employee_id, return_path, now):
    if employee_id not in db["accounts"]:
        raise ValueError("unknown employee")
    state = secrets.token_urlsafe(24)
    db["pending"][state] = {"employee_id": employee_id,
                            "return_path": return_path, "expires_at": now + 300}
    return {"state": state, "redirect": ISSUER + "/authorize?" + urlencode({"state": state})}


def callback(db, state, assertion, now):
    # The new provider callback has not yet been integrated.
    raise ValueError("provider callback integration incomplete")
