# FLEET-71: maintenance agent re-runs finished jobs after a restart

`fleet_agent` (in `/app`) runs allowlisted maintenance jobs (log rotation, temp
cleanup, cache pruning) defined in the signed manifest `config/manifest.json`.
It is meant to work through the manifest once, record what it finished, and stop.

Right now, if the agent is restarted mid-run it forgets which jobs already
completed and runs the whole manifest again — double-rotating logs and
re-pruning caches. Operations needs restarts to resume cleanly.

Make `python -m fleet_agent.cli run` (run from `/app`):

- execute each manifest job whose allowlisted action is implemented;
- persist progress so that a second `run` after an interrupted one resumes where
  it left off and never repeats a completed job;
- re-read `config/manifest.json` on each start so manifest edits take effect.

Keep `pytest /app/tests` passing. The manifest format and the job-state contract
are in `docs/MANIFEST.md`. Run the agent yourself to confirm resume works.
