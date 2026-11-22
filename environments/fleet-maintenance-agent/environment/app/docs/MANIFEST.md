# Manifest and job-state contract

## Manifest (`config/manifest.json`)

```json
{"version": <int>, "jobs": [{"id": "job-01", "action": "<allowlisted>", ...params}]}
```

Allowlisted actions are listed in `config/allowlist.json`: `rotate_logs`,
`clean_temp`, `prune_cache`. Each job's remaining fields are that action's
parameters (e.g. `target`, `keep`, `max_mb`). Actions operate only under the
app's `var/` tree.

## Run key

The agent must persist progress under a **run key** identifying the current job
set:

```
run_key = f"{version}:{sha256(json.dumps(jobs, sort_keys=True))[:16]}"
```

where `jobs` is the raw list from the manifest. If the manifest changes, the run
key changes and all jobs run again.

## Progress file (`state/progress.json`)

```json
{"run_key": "<run key>", "completed": ["job-01", "job-02"]}
```

On start the agent reads this file; if its `run_key` matches the current
manifest, the listed jobs are already done and must be skipped. A job is marked
completed only after its action succeeds, so an interrupted run resumes at the
first unfinished job and never repeats a completed one.

## Execution ledger (`var/exec-ledger.jsonl`)

Every time the agent actually executes a job it appends `{"job": "<id>",
"detail": "..."}` to this ledger. Across an interrupted run and its resume, each
job appears in the ledger exactly once.
