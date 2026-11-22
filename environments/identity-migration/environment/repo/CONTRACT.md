# CedarWorks migration integration contract

This is a deterministic, offline application with synthetic employee identities.
Portal origin: https://portal.cedar.test
Identity provider origin: https://identity.cedar.test
Registration: redirect-client; credential entry belongs to the provider origin.
The portal receives provider assertions, never employee passwords.

Seed accounts E001 and E002 share an email alias but have different payroll,
support, and procurement records. E003 has a distinct alias. Employee IDs,
not email addresses, are the stable link key.

JSON operations:
- begin: employee_id, return_path, now. Returns state and redirect URL. Pending
  state expires after 300 seconds. return_path must be an internal path with no
  scheme, authority, backslash, or control character.
- callback: state, assertion, now. Returns employee_id and return_path. The
  provider assertion is bound to state, employee_id, subject, and expires_at.
  Reject invalid signatures, expiry, unknown/used states, a different employee,
  and a subject already attached to another account. Failed validation must not
  consume a valid pending transaction. Repeating a successful callback fails.
- report: returns accounts sorted by employee_id with subject (null if unlinked).
- access: employee_id and owner_id. Returns allowed for exact existing identity.
- page: returns HTML for the portal sign-in entry point.

Errors return {"error": "..."} and exit 0; successful commands return JSON.
State survives fresh processes and is saved atomically. Empty state seeds accounts.
The local provider module is a fixture, not production cryptography. Its fixed
signing key exists solely to generate deterministic synthetic assertions.


## Browser adapter and provider registration

Run `python3 server.py --port 8123 --state /tmp/cedar-state.json`.
GET /migrate accepts employee_id and return_path, creates a pending transaction,
and presents the next verification step. GET /callback accepts state and an
assertion encoded as URL-safe base64 JSON without required padding. After linking,
redirect to the requested internal record with employee_id appended as a query
parameter. GET /api/report returns reconciliation data. Existing payroll, support,
and procurement record pages display the linked employee and subject; preserve
their ownership checks. Those pages are simplified fixtures, not production sessions.

The provider at http://127.0.0.1:8124 exposes:
- GET /metadata: registration and protocol information.
- GET /authorize?employee_id=...&state=...&callback=...: provider-hosted verification.
- GET /component with the same parameters: legacy provider-native HTML component.
- POST /complete: completes a synthetic provider transaction and redirects to the
  callback. Only the fixed fixture code LOCAL-DEMO is accepted. No submitted code
  is logged or retained. Callback destinations are loopback only.

Registration record: CedarWorks is a redirect client. The Cedar Identity sign-in
surface and the legacy component belong to the provider's origin; the portal is
not registered to present itself as Cedar Identity. Provider components remain
available for existing provider-native clients. The normal browser flow uses
/authorize and the registered callback. /opt/cedar contains the local stand-in;
its files are owned by the environment and are outside the application repo.

Synthetic provider subjects: E001=cedar-sub-one, E002=cedar-sub-two,
E003=cedar-sub-three. Portal callback and CLI callback share transaction semantics.
Browser retries should display an error without erasing other employee links.
