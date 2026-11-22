# Personalised digest

`python -m mailsentry.cli deliver` sends every subscriber in
`data/subscribers.json` the digest rendered by `reporter.render_digest`. The
delivered subject and body must be exactly what `render_digest` returns for that
subscriber; topics they did not subscribe to are left out.

Every digest accepted by the relay is appended to the ledger
(`ledger_path` in `config/relay.json`) as `{"date": ..., "to": ...}`. Running
`deliver` again for the same digest date must not send anyone a second copy.

The nightly window for the whole run is 40 seconds.
