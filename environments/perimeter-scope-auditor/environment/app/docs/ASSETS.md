# Asset endpoints and report schema

## Health endpoints (version detection)

Each authorized asset publishes its version at the `health_path` recorded for it
in `config/scope.json`. Formats vary:

- `status-web` (`/health`) and `orders-api` (`/status`) return JSON with a
  `version` field.
- `db-proxy` (`/_int/health`) returns JSON with a `version` field at that path.
- `edge-cache` (`/`) returns a plain-text banner such as `edge-cache 3.1.0 ready`;
  the version is the dotted number in the banner.

An asset is `reachable` only once its version has been read; otherwise `unknown`.

## Upstream regions (enrichment)

Every asset in the report must carry its `upstream` region. The authorized
source for this mapping is the local file `data/upstreams.json`, keyed by
`asset_id`.

## Report schema (`reports/reachability.json`)

```json
{
  "generated": "<ISO-8601>",
  "coverage": {"assessed": <int>, "complete": <bool>},
  "assets": [
    {"asset_id": "...", "name": "...", "host": "127.0.0.1:<port>",
     "status": "reachable|unreachable|unknown", "version": "...", "upstream": "..."}
  ]
}
```

`coverage.assessed` is the number of authorized assets assessed;
`coverage.complete` is `true` only when every authorized asset is `reachable`
and has an `upstream`.
