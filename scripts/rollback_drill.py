from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

from safe_copy_migration_apply import default_copy_path, main as apply_on_copy


def main() -> int:
    source = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    if not source.exists():
        print(f"ROLLBACK DRILL FAILED: source database not found: {source}")
        return 2
    backup = source.with_name(f"{source.stem}.v8_4_rollback_backup{source.suffix}")
    restored = source.with_name(f"{source.stem}.v8_4_rollback_restored{source.suffix}")
    migration_copy = default_copy_path(source)
    shutil.copy2(source, backup)
    original_hash = sha256_file(source)
    code = apply_on_copy_with_args(source, migration_copy)
    if code not in {0}:
        print("ROLLBACK DRILL FAILED: copy migration did not verify")
        return code
    shutil.copy2(backup, restored)
    restored_hash = sha256_file(restored)
    current_hash = sha256_file(source)
    print("# v8.4 rollback drill")
    print(f"Source: {source}")
    print(f"Backup: {backup}")
    print(f"Migration copy: {migration_copy}")
    print(f"Rollback restored copy: {restored}")
    if restored_hash != original_hash or current_hash != original_hash:
        print("Result: ROLLBACK DRILL FAILED")
        return 1
    print("Result: ROLLBACK DRILL PASSED")
    return 0


def apply_on_copy_with_args(source: Path, target: Path) -> int:
    old_argv = sys.argv[:]
    try:
        sys.argv = ["safe_copy_migration_apply.py", str(source), str(target)]
        return apply_on_copy()
    finally:
        sys.argv = old_argv


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
