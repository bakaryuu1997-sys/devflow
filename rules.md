# DevFlow Guard Engineering Rules

## 1. File size limit

Every checked source or documentation file should stay under 200 lines.

If a file grows beyond 200 lines, split it into:

```text
sub-components
helper modules
service modules
utility files
```

## 2. No business logic inside UI

UI files should focus on rendering and user interaction.

Complex logic must be moved into:

```text
API client helpers
service modules
utility functions
custom hooks if the project later moves to React/TypeScript
```

## 3. Responsive layout required

The UI must work on desktop and mobile.

For this vanilla HTML/CSS version:

```text
Use responsive CSS media queries.
Avoid fixed-width layouts that overflow.
Keep panels stackable on small screens.
```

If the project later moves to Tailwind/React:

```text
Use mobile-first classes.
Use md: and lg: breakpoints carefully.
```

## 4. No hardcoded secrets

Secrets must stay in environment files.

Allowed:

```text
.env
.env.local
deployment secret manager
```

Not allowed:

```text
committed API keys
OpenAI/Claude keys
Firebase secrets
production JWT secrets
database passwords in source code
```

## 5. Typed data contracts

The backend must use explicit Pydantic schemas.

Avoid:

```text
unstructured dictionaries in API boundaries
ambiguous payloads
```

If the frontend later moves to TypeScript:

```text
Enable strict mode.
Avoid any unless there is a strong reason.
```

## 6. Loading, error and empty states

Premium UX must include:

```text
loading state
friendly error state
empty state with next action
```

Do not leave users staring at blank panels or raw failures.

## 7. Avoid heavy dependencies

Before adding a dependency, ask:

```text
Can this be written safely in under 20 lines?
Does it increase build/runtime risk?
Is it needed for MVP quality?
```

## 8. Verify before packaging

Before producing a release ZIP, run:

```bash
python -m compileall app
pytest
python scripts/quality_check.py
```

For future JS/TS frontend:

```bash
npm run lint
npm run build
```
