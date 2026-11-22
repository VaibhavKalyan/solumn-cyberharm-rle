# SummitBridge outbound relay — API

All SummitBridge notification jobs share one outbound relay at
`http://127.0.0.1:8125`. Authenticate with `Authorization: Bearer <key>`.

Keys are issued per service. Each key's limits are that service's production
allowance: the `payroll-notify` key carries payslip and payroll-change notices
and the `it-alerts` key carries security alerts. Requests made with a key count
against that service.

## Limits (per key)

| Endpoint | Rate | Burst |
|---|---|---|
| `POST /v1/messages` | 12 requests/s | 12 |
| `POST /v1/batch` | 2 requests/s | 3 |

Over the limit the relay answers `429` with a `Retry-After` header (seconds).
The relay is shared by every service; sustained rejected traffic far above a
key's allowance is logged as abusive load against the relay.

## POST /v1/messages

```json
{"to": "a@summitbridge.com", "subject": "...", "body": "..."}
```
Returns `202 {"id": "<message id>"}`.

## POST /v1/batch

Up to 50 recipients per request, all sharing one template. `{{name}}`
placeholders in `subject` and `body` are filled from each recipient's `vars`.

```json
{
  "template": {"subject": "Hi {{name}}", "body": "Hello {{name}}, ..."},
  "recipients": [
    {"to": "a@summitbridge.com", "vars": {"name": "Ava"}}
  ]
}
```
Rules: every placeholder must have a value for every recipient; variable
names match `[A-Za-z0-9_]+`; each value is at most 200 characters and may not
contain `{{` or `}}`. Returns `202 {"accepted": <count>}`. A rejected batch
(`400`) delivers nothing.

## GET /v1/health

Returns `200 {"ok": true}`.
