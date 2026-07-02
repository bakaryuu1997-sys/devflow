"""Global test configuration.

Isolates the test run from the developer's real ``devflow.db`` by pointing the
app at a throwaway SQLite database, and seeds the default admin so the auth
tests have an account to log in with. This runs before any test module is
imported, so ``app.config`` reads the overridden ``DATABASE_URL``.
"""

import os
import pathlib
import tempfile

# Route the app at a dedicated test database (never the real devflow.db).
_TEST_DB = pathlib.Path(tempfile.gettempdir()) / "devflow_test.db"
if _TEST_DB.exists():
    _TEST_DB.unlink()
os.environ["DATABASE_URL"] = "sqlite:///" + _TEST_DB.as_posix()
# Tests exercise the real auth flow; keep login enabled unless a test opts out.
os.environ["LOCAL_NO_AUTH"] = "false"

from app import seed  # noqa: E402  (must follow the env setup above)

# Create the schema and the default admin@example.com / password123 account.
seed.main()
