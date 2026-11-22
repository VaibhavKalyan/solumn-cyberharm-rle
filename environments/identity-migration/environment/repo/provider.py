"""Synthetic signed assertions. Never use this fixture key in production."""
import hashlib
import hmac
import json

KEY = b"public-fixture-key-not-a-secret"
ISSUER = "https://identity.cedar.test"


def signature(claims):
    message = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(KEY, message, hashlib.sha256).hexdigest()


def issue(employee_id, subject, state, expires_at):
    claims = dict(employee_id=employee_id, subject=subject, state=state,
                  expires_at=expires_at, issuer=ISSUER)
    return {"claims": claims, "signature": signature(claims)}


def verify(assertion, now):
    claims = assertion["claims"]
    if not hmac.compare_digest(signature(claims), assertion["signature"]):
        raise ValueError("invalid signature")
    if claims["issuer"] != ISSUER or claims["expires_at"] <= now:
        raise ValueError("invalid issuer or expired assertion")
    if not isinstance(claims["subject"], str) or not claims["subject"]:
        raise ValueError("missing subject")
    return claims
