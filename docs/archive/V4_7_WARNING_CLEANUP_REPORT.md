# v4.7 Pydantic v2 Warning Cleanup & Timezone-Safe Datetime

## Goal

Clean backend warning noise without changing UI or adding features.

## Changes

### Pydantic v2 cleanup

Replaced class-based schema config:

```text
class Config:
    from_attributes = True
```

with:

```text
model_config = ConfigDict(from_attributes=True)
```

Also updated app settings to use:

```text
SettingsConfigDict(env_file=".env")
```

### Timezone-safe datetime

Added:

```text
app/time_utils.py
```

and changed SQLAlchemy defaults from:

```text
datetime.utcnow
```

to:

```text
utc_now
```

### Auth warning cleanup

`python-jose` emitted internal `datetime.utcnow()` warnings on Python 3.13.
To avoid adding another dependency, auth tokens now use a small standard-library HMAC JWT-compatible format.

Removed unused `python-jose` from `requirements.txt`.

## Scope control

No UI changes.
No product feature changes.
No dependency added.
