"""Provider-mediated account linking with persistent single-use transactions."""
import secrets
from urllib.parse import urlencode, urlsplit
from provider import ISSUER, verify


def begin(db, employee_id, return_path, now):
    if employee_id not in db["accounts"]:
        raise ValueError("unknown employee")
    parsed = urlsplit(return_path)
    if (not return_path.startswith("/") or return_path.startswith("//")
            or parsed.scheme or parsed.netloc or "\\" in return_path
            or any(ord(c) < 32 for c in return_path)):
        raise ValueError("invalid return path")
    state = secrets.token_urlsafe(24)
    db["pending"][state] = {"employee_id": employee_id,
                            "return_path": return_path, "expires_at": now + 300}
    return {"state": state, "redirect": ISSUER + "/authorize?" + urlencode({"state": state})}


def callback(db, state, assertion, now):
    pending = db["pending"].get(state)
    if pending is None or pending["expires_at"] <= now:
        raise ValueError("unknown or expired state")
    claims = verify(assertion, now)
    if claims["state"] != state or claims["employee_id"] != pending["employee_id"]:
        raise ValueError("transaction mismatch")
    employee = pending["employee_id"]
    subject = claims["subject"]
    for key, account in db["accounts"].items():
        if key != employee and account["subject"] == subject:
            raise ValueError("subject already linked")
    existing = db["accounts"][employee]["subject"]
    if existing is not None and existing != subject:
        raise ValueError("account already linked to different subject")
    db["accounts"][employee]["subject"] = subject
    del db["pending"][state]
    return {"employee_id": employee, "return_path": pending["return_path"]}
