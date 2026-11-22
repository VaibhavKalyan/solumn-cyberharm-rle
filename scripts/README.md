# Reproduction scripts

- `check_*.py` — build the image and grade starter/safe/unsafe offline in Docker
  (no model, no API key needed).
- `run_<env>_harbor.py --mode safe|unsafe|model` — run references and the
  gpt-6.1-sol rollout through Harbor.

The `--mode model` runners read the model endpoint from
`private/solumn_endpoint.json` (`{"base_url": "...", "api_key": "..."}`), which
is **not** included in this archive. Supply your own to reproduce rollouts.
