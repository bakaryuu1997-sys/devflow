# DevFlow Guard v3.1 — Offline First + Simple Account

## Added

- Simple account creation
- Duplicate email/account prevention
- Password minimum length: 8 characters
- Long-lived login token
- Logout button
- Local browser session persists until logout
- Demo account updated to `password123`
- UI can be used smoothly in offline local mode

## Account rules

- Email/account must be unique.
- Password must be at least 8 characters.
- Login persists through localStorage until manual logout.
- Public registration is enabled by default for offline/local use.

## Recommended local flow

1. Open app.
2. Click `Reset Demo`.
3. App logs in automatically.
4. Upload release artifacts.
5. Scan guards.
6. Run readiness.
7. Export evidence report.
