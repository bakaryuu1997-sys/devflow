# v8.1 Self Evaluation

## What improved
- Existing SQLite users now get a concrete schema readiness check.
- Upgrade safety is exportable as Markdown.
- The CLI helper can be run before launching the app.

## Trade-off
The checker is intentionally additive and conservative. It does not auto-migrate the database yet, because automatic schema mutation should be a separate, carefully tested milestone.

## Next step
v8.2 should add a dry-run SQL migration generator that prints safe `ALTER TABLE` statements without executing them.
