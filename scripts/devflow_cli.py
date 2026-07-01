#!/usr/bin/env python3
import argparse
import csv
import io
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

# Default Configuration
DEFAULT_URL = "http://127.0.0.1:8000"
DEFAULT_EMAIL = "admin@example.com"
DEFAULT_PASSWORD = "password123"
DEFAULT_PROJECT_ID = 1


def send_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}

    req = urllib.request.Request(url, method=method, headers=headers)
    if data is not None:
        req.data = data

    try:
        with urllib.request.urlopen(req) as res:
            return res.read().decode("utf-8"), res.status
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            return err_body, e.code
        except Exception:
            return str(e), e.code
    except urllib.error.URLError as e:
        return str(e.reason), 503
    except Exception as e:
        return str(e), 500


def login(base_url, email, password):
    url = f"{base_url}/api/auth/login"
    payload = json.dumps({"email": email, "password": password}).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    body, code = send_request(url, "POST", data=payload, headers=headers)
    if code == 200:
        try:
            return json.loads(body).get("access_token")
        except Exception as e:
            print(f"Error parsing login token response: {e}")
            return None
    else:
        print(f"Login failed (HTTP {code}): {body}")
        return None


def get_local_git_commits():
    try:
        # Run git log and extract the last 10 commits with changed files
        res = subprocess.run(
            ["git", "log", "-n", "10", "--name-only", "--pretty=format:COMMIT:%H|%an|%s"],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = res.stdout.splitlines()

        commits = []
        current_commit = None
        for line in lines:
            if line.startswith("COMMIT:"):
                if current_commit:
                    commits.append(current_commit)
                parts = line[7:].split("|", 2)
                sha = parts[0] if len(parts) > 0 else ""
                author = parts[1] if len(parts) > 1 else ""
                msg = parts[2] if len(parts) > 2 else ""
                current_commit = {"ref": sha, "author": author, "title": msg, "status": "committed", "files": []}
            elif line.strip() and current_commit:
                current_commit["files"].append(line.strip())
        if current_commit:
            commits.append(current_commit)

        # Format as CSV content matching DevFlow expected structure
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["ref", "title", "author", "status", "changed_files"])
        writer.writeheader()
        for c in commits:
            writer.writerow(
                {
                    "ref": c["ref"],
                    "title": c["title"],
                    "author": c["author"],
                    "status": c["status"],
                    "changed_files": ";".join(c["files"]),
                }
            )
        return output.getvalue()
    except subprocess.SubprocessError:
        # Git command failed (e.g. not a git repo or git not installed)
        return None
    except Exception as e:
        print(f"Error getting git commits: {e}")
        return None


def build_multipart(filename, content, fieldname="file"):
    boundary = "----DevFlowFormBoundary" + os.urandom(16).hex()
    header = {"Content-Type": f"multipart/form-data; boundary={boundary}"}

    # Ensure binary format
    if isinstance(content, str):
        content_bytes = content.encode("utf-8", errors="ignore")
    else:
        content_bytes = content

    body = (
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{fieldname}"; filename="{filename}"\r\n'
            f"Content-Type: text/plain\r\n\r\n"
        ).encode()
        + content_bytes
        + f"\r\n--{boundary}--\r\n".encode()
    )

    return body, header


def scan_command(args):
    print("Initializing compliance scan...")
    token = login(args.url, args.email, args.password)
    if not token:
        print("Authentication failed. Aborting scan.")
        sys.exit(1)

    auth_headers = {"Authorization": f"Bearer {token}"}

    # 1. Scan Git commits
    git_csv = get_local_git_commits()
    if git_csv:
        print("Scanning latest local Git commits...")
        import_url = f"{args.url}/api/projects/{args.project}/git-import"
        import_payload = json.dumps({"content": git_csv, "item_type": "commit"}).encode("utf-8")
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

        body, code = send_request(import_url, "POST", data=import_payload, headers=headers)
        if code == 200:
            print("Successfully synchronized local Git commits.")
        else:
            print(f"Warning: Failed to sync Git commits (HTTP {code}): {body}")
    else:
        print("Note: Git commits scan skipped (not in a git repository or command failed).")

    # 2. Scan SQL migrations folder
    migrations_dir = args.migrations
    if os.path.exists(migrations_dir) and os.path.isdir(migrations_dir):
        print(f"Scanning SQL migration files in {migrations_dir}...")
        for fname in os.listdir(migrations_dir):
            if fname.endswith(".sql"):
                fpath = os.path.join(migrations_dir, fname)
                try:
                    with open(fpath, encoding="utf-8", errors="ignore") as f:
                        sql_content = f.read()

                    upload_url = f"{args.url}/api/projects/{args.project}/guards/sql"
                    body_data, multi_headers = build_multipart(fname, sql_content)
                    multi_headers.update(auth_headers)

                    body, code = send_request(upload_url, "POST", data=body_data, headers=multi_headers)
                    if code == 200:
                        print(f"  [OK] SQL Scan: {fname}")
                    else:
                        print(f"  [ERROR] SQL Scan {fname} failed (HTTP {code}): {body}")
                except Exception as e:
                    print(f"  [ERROR] Reading {fname}: {e}")
    else:
        print(f"Note: Migrations directory '{migrations_dir}' not found. Skipping SQL guard scans.")

    # 3. Scan test logs if specified or found
    test_logs_path = args.test_logs
    if not test_logs_path:
        # Check standard default filenames
        for p in ["pytest.log", "tests.log", "test.log"]:
            if os.path.exists(p):
                test_logs_path = p
                break

    if test_logs_path and os.path.exists(test_logs_path):
        print(f"Scanning test logs file '{test_logs_path}'...")
        try:
            with open(test_logs_path, encoding="utf-8", errors="ignore") as f:
                log_content = f.read()

            upload_url = f"{args.url}/api/projects/{args.project}/guards/tests"
            body_data, multi_headers = build_multipart(os.path.basename(test_logs_path), log_content)
            multi_headers.update(auth_headers)

            body, code = send_request(upload_url, "POST", data=body_data, headers=multi_headers)
            if code == 200:
                print(f"  [OK] Test Logs Scan: {os.path.basename(test_logs_path)}")
            else:
                # Try logs route if tests fails
                upload_url = f"{args.url}/api/projects/{args.project}/guards/logs"
                body, code = send_request(upload_url, "POST", data=body_data, headers=multi_headers)
                if code == 200:
                    print(f"  [OK] General Logs Scan: {os.path.basename(test_logs_path)}")
                else:
                    print(f"  [ERROR] Log scan failed (HTTP {code}): {body}")
        except Exception as e:
            print(f"  [ERROR] Reading test logs {test_logs_path}: {e}")
    else:
        print("Note: No test logs found or specified. Skipping test guard scans.")

    # 4. Fetch active compliance findings to determine if blockages exist
    print("Checking active governance guards and risk gates...")
    findings_url = f"{args.url}/api/projects/{args.project}/guards"
    body, code = send_request(findings_url, "GET", headers=auth_headers)

    blockers = []
    if code == 200:
        try:
            findings = json.loads(body)
            for f in findings:
                if f.get("blocking"):
                    blockers.append(f)
        except Exception as e:
            print(f"Error parsing compliance findings: {e}")
    else:
        print(f"Error checking findings (HTTP {code}): {body}")

    # Fetch risks as well
    risks_url = f"{args.url}/api/projects/{args.project}/risks"
    body, code = send_request(risks_url, "GET", headers=auth_headers)
    if code == 200:
        try:
            risks = json.loads(body)
            for r in risks:
                if r.get("blocking"):
                    blockers.append(r)
        except Exception:
            pass

    if blockers:
        print("\n" + "=" * 60)
        print("🔴 DEVFLOW GOVERNANCE GATE BLOCKED!")
        print("The following critical blockers must be resolved before pushing:")
        for b in blockers:
            filename_str = f" in {b.get('filename')}" if b.get("filename") else ""
            print(f"  - [{b.get('severity', 'UNKNOWN')}] {b.get('title')}{filename_str}")
            print(f"    Reason: {b.get('message')}")
        print("=" * 60 + "\n")
        sys.exit(1)
    else:
        print("\n🟢 DEVFLOW COMPLIANCE SCAN PASSED. No blocking violations detected.")
        sys.exit(0)


def status_command(args):
    print("Checking local DevFlow Engine status...")

    # 1. Health check
    health_url = f"{args.url}/api/health"
    body, code = send_request(health_url, "GET")
    if code != 200:
        print(f"🔴 Local DevFlow server is offline or unreachable at {args.url}.")
        print("Please start the server (e.g. `npm run dev` or `uvicorn app.main:app --reload`) and try again.")
        sys.exit(1)

    print(f"🟢 Server status: ONLINE (running at {args.url})")

    # 2. Cryptographic Ledger validation
    print("Verifying local audit log ledger integrity...")
    verify_url = f"{args.url}/api/governance/verify-ledger"
    body, code = send_request(verify_url, "GET")

    if code == 200:
        try:
            res = json.loads(body)
            if res.get("status") == "verified":
                print(f"🔒 Cryptographic Ledger: SECURE (verified {res.get('count')} log chain hashes)")
            else:
                print("⚠️  CRYPTOGRAPHIC LEDGER IS TAMPERED OR INCONSISTENT!")
                print(f"   Reason: {res.get('reason')}")
                print(f"   Target record ID: {res.get('record_id')}")
        except Exception as e:
            print(f"⚠️  Failed to parse ledger response: {e}")
    else:
        print(f"⚠️  Ledger verification failed with HTTP {code}: {body}")

    # 3. Retrieve general findings
    token = login(args.url, args.email, args.password)
    if token:
        auth_headers = {"Authorization": f"Bearer {token}"}
        findings_url = f"{args.url}/api/projects/{args.project}/guards"
        body, code = send_request(findings_url, "GET", headers=auth_headers)
        if code == 200:
            try:
                findings = json.loads(body)
                total = len(findings)
                blockers = sum(1 for f in findings if f.get("blocking"))
                print(f"📊 Compliance findings: {total} active finding(s), {blockers} blocker(s)")
            except Exception:
                pass
    else:
        print("Note: Could not login to retrieve project statistics.")


def install_hook_command(args):
    print("Installing DevFlow Git pre-push compliance hook...")

    # Find .git directory by walking up
    curr = os.path.abspath(os.getcwd())
    git_dir = None
    while True:
        candidate = os.path.join(curr, ".git")
        if os.path.exists(candidate) and os.path.isdir(candidate):
            git_dir = candidate
            break
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent

    if not git_dir:
        print("🔴 Error: Could not locate a `.git` folder in this directory or any parent directories.")
        print("Please run this command inside a initialized Git repository.")
        sys.exit(1)

    hooks_dir = os.path.join(git_dir, "hooks")
    if not os.path.exists(hooks_dir):
        os.makedirs(hooks_dir)

    hook_path = os.path.join(hooks_dir, "pre-push")

    # Detect appropriate python executable command
    python_cmd = "python"
    # If a virtual environment is active or exists in current directory, reference it
    if os.path.exists(os.path.join(".venv", "Scripts", "python.exe")):
        python_cmd = ".venv/Scripts/python"
    elif os.path.exists(os.path.join(".venv", "bin", "python")):
        python_cmd = ".venv/bin/python"

    hook_content = f"""#!/bin/sh
# DevFlow personal compliance pre-push hook
# Generated by DevFlow CLI

echo "DevFlow: Starting local Git compliance checks..."
{python_cmd} scripts/devflow_cli.py scan --url {args.url} --project {args.project} --email {args.email} --password {args.password}

exit_code=$?
if [ $exit_code -ne 0 ]; then
  echo "DevFlow: 🔴 Push blocked by governance guards. Resolve issues or run scan manually."
  exit $exit_code
fi

echo "DevFlow: 🟢 Compliance check passed. Proceeding with push."
exit 0
"""

    try:
        with open(hook_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(hook_content)

        # Make the file executable
        try:
            os.chmod(hook_path, 0o755)
        except Exception:
            pass

        print(f"🟢 Git hook successfully installed at: {hook_path}")
        print("Every time you run `git push`, the compliance engine will automatically evaluate your code safety!")
    except Exception as e:
        print(f"🔴 Error writing pre-push hook: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="DevFlow Guard Personal Command-line compliance interface.")

    # Global arguments
    parser.add_argument("--url", default=DEFAULT_URL, help="Base URL of the DevFlow API server")
    parser.add_argument("--email", default=DEFAULT_EMAIL, help="User email to authenticate")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="User password to authenticate")
    parser.add_argument("--project", type=int, default=DEFAULT_PROJECT_ID, help="Project ID for governance context")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Scan command subparser
    scan_parser = subparsers.add_parser("scan", help="Synchronize local state and run compliance checks")
    scan_parser.add_argument("--migrations", default="./migrations", help="Path to SQL migrations folder")
    scan_parser.add_argument("--test-logs", default=None, help="Path to a test log file")

    # Status command subparser
    subparsers.add_parser("status", help="Query local server and ledger cryptographic status")

    # Install hook subparser
    subparsers.add_parser("install-hook", help="Install a pre-push hook in the active local git directory")

    args = parser.parse_args()

    if args.command == "scan":
        scan_command(args)
    elif args.command == "status":
        status_command(args)
    elif args.command == "install-hook":
        install_hook_command(args)


if __name__ == "__main__":
    main()
