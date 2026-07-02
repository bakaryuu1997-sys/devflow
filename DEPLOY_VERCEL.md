# Deploying DevFlow Guard to Vercel

DevFlow Guard is a FastAPI app. It runs on Vercel as a single Python
serverless function (`api/index.py`, routed by `vercel.json`). Because
serverless filesystems are **ephemeral and read-only**, you must use a hosted
database for anything to persist.

## 1. Create a Postgres database (required for persistence)

Use any hosted Postgres — [Neon](https://neon.tech) and
[Supabase](https://supabase.com) both have a free tier. Copy the connection
string and convert it to the SQLAlchemy + psycopg format:

```
# Neon gives you:      postgresql://USER:PASSWORD@HOST/DB?sslmode=require
# Use this in Vercel:  postgresql+psycopg://USER:PASSWORD@HOST/DB?sslmode=require
```

> Without `DATABASE_URL`, the app still boots on Vercel using a throwaway
> SQLite file in `/tmp`, but **all data is wiped on every cold start** (no
> saved users, no history). Only use that to confirm the page loads.

## 2. Set Environment Variables in Vercel

Project → **Settings → Environment Variables** (Production + Preview):

| Key | Value | Notes |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://…` | From step 1 |
| `JWT_SECRET_KEY` | 32+ random characters | Generate: `python -c "import secrets;print(secrets.token_urlsafe(48))"` |
| `ENVIRONMENT` | `production` | Enables the production security gate |
| `AUTH_MODE` | `production` | |
| `ALLOW_PUBLIC_REGISTER` | `false` | Set `true` if you want visitors to self-register for the demo |
| `ALLOW_DEMO_RESET` | `false` | |
| `AUTO_CREATE_TABLES` | `true` | Lets the app create tables on first boot |
| `ACCESS_TOKEN_MINUTES` | `60` | Production gate rejects values > 1440 |
| `CORS_ORIGINS` | `https://<your-app>.vercel.app` | |

> If you set `ENVIRONMENT=production` with a weak/short `JWT_SECRET_KEY`, the
> startup security check raises on purpose and Vercel shows
> `FUNCTION_INVOCATION_FAILED`. Use a strong secret, or keep
> `ENVIRONMENT=development` while testing.

## 3. Create the first admin user

Tables are created automatically, but you need a login. Either:

- **Register via the UI** (if `ALLOW_PUBLIC_REGISTER=true`), or
- **Seed locally against the same DB** — set the same `DATABASE_URL` in your
  shell and run:

  ```bash
  DATABASE_URL="postgresql+psycopg://…" python -m app.seed
  # creates admin@example.com / password123 — change the password after login
  ```

## 4. Redeploy

Push to `main` (Vercel auto-deploys) or hit **Redeploy**. Open
`https://<your-app>.vercel.app` — the login screen should load.

## Notes & limitations

- Every request (including each `/static/*` asset) is handled by the function,
  so cold starts are slower than a always-on server. Fine for a portfolio
  demo; for heavier use prefer an always-on host (Render/Railway/Fly.io).
- `requirements.txt` is installed as-is. If you hit the 250 MB function size
  limit, move test-only deps (`pytest`, `httpx`) into `requirements-dev.txt`.
