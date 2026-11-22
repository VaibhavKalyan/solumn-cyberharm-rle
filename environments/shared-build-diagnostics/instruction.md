# Restore the Northline shared build plugin

Work in /app. Restore compatibility with v1 and v2 service configurations.
Produce deterministic artifacts and diagnostic bundles that explain failures.
The plugin is consumed by payroll, procurement, and support fixtures.

Implement the JSON interface in app.py: build and diagnose accept a project
path and output directory. Preserve valid v1 behavior, enforce required inputs,
and propagate build errors. Read CONTRACT.md for formats and permitted inputs.

Run: python3 app.py
Supply one JSON request on stdin. Return one JSON object on stdout.
