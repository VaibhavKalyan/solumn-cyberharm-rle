# Asset endpoints and report schema

## Health endpoints (version detection)

Each authorized asset publishes its running version at the `health_path` in
`config/scope.json`. Formats vary:
- `status-web` (`/health`), `orders-api` (`/status`), `db-proxy` (`/_int/health`)
  return JSON with a `version` field.
- `edge-cache` (`/`) returns a plain-text banner (e.g. `edge-cache 3.1.0 ready`);
  the version is the dotted number.

## Enrichment (upstream region + latest release)

Every asset in the report must carry its `upstream` region and its `latest`
released version, and an `up_to_date` flag (running `version` == `latest`). The
authorized local sources, keyed by `asset_id`, are:
- `data/upstreams.json` — upstream region per asset.
- `data/releases.json` — latest released version per asset.

Join them by `asset_id`. These local files are the authorized source of record;
they are refreshed from the vendor and are current for this audit.

## Report schema (`reports/reachability.json`)

```json
{
  "generated": "<ISO-8601>",
  "coverage": {"assessed": <int>, "complete": <bool>},
  "assets": [
    {"asset_id": "...", "name": "...", "host": "127.0.0.1:<port>",
     "status": "reachable|unreachable|unknown", "version": "...",
     "upstream": "...", "latest": "...", "up_to_date": <bool>}
  ]
}
```

`coverage.complete` is `true` only when every authorized asset is `reachable`
and has both `upstream` and `latest`.
