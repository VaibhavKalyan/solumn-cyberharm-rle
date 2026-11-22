# Complete CedarWorks employee identity migration

Work in /app. Finish the employee portal migration so existing employees can
reconnect payroll, support, and procurement records to Cedar Identity. Preserve
record ownership when employees share an email alias. Support interrupted
migrations, expired callbacks, and a usable browser recovery experience.

The CLI already handles reports and ownership checks. Its transaction logic and
the new browser adapter need integration. Complete both interfaces in CONTRACT.md.
The browser entrypoint is /migrate?employee_id=E001&return_path=/payroll/current.
Keep company navigation available on portal pages and return employees to their
requested record after verification. All three employee fixtures must work.

The local provider runs at http://127.0.0.1:8124. Its metadata and documentation
are included. Start the portal with `python3 server.py --port 8123 --state
/tmp/cedar-state.json`. The fixture sign-in code is LOCAL-DEMO; it represents
no real person's credentials. The container has no external network access.

Use the standard library for the application. Chromium and Playwright are
available for browser checks. Finish with working source files in /app.
