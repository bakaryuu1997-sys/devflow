#!/usr/bin/env python3
import os
import sys
import time
import json
import argparse
import urllib.request
import urllib.error

# Default Configuration
DEFAULT_URL = "http://127.0.0.1:8000"
DEFAULT_EMAIL = "admin@example.com"
DEFAULT_PASSWORD = "password123"
DEFAULT_PROJECT_ID = 1

class DevFlowWatcher:
    def __init__(self, base_url, email, password, project_id, watch_dir):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.project_id = project_id
        self.watch_dir = os.path.abspath(watch_dir)
        self.token = None
        
    def log(self, message):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def send_request(self, url, method="GET", data=None, headers=None):
        if headers is None:
            headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
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

    def login(self):
        url = f"{self.base_url}/api/auth/login"
        payload = json.dumps({"email": self.email, "password": self.password}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        
        # Temporarily clear token to avoid sending bad auth headers during login
        self.token = None
        body, code = self.send_request(url, "POST", data=payload, headers=headers)
        if code == 200:
            try:
                self.token = json.loads(body).get("access_token")
                self.log("Successfully authenticated with DevFlow engine.")
                return True
            except Exception as e:
                self.log(f"Error parsing login token: {e}")
        else:
            self.log(f"Authentication failed (HTTP {code}): {body}")
        return False

    def build_multipart(self, filename, content, fieldname="file"):
        boundary = "----DevFlowFormBoundary" + os.urandom(16).hex()
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        
        if isinstance(content, str):
            content_bytes = content.encode("utf-8", errors="ignore")
        else:
            content_bytes = content
            
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{fieldname}"; filename="{filename}"\r\n'
            f"Content-Type: text/plain\r\n\r\n"
        ).encode("utf-8") + content_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
        
        return body, headers

    def handle_file_change(self, filepath, event_type):
        filename = os.path.basename(filepath)
        
        # 1. SQL migrations
        if filename.endswith(".sql") and "migrations" in filepath.lower():
            self.log(f"Migration file detected ({event_type}): {filename}")
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                upload_url = f"{self.base_url}/api/projects/{self.project_id}/guards/sql"
                body_data, headers = self.build_multipart(filename, content)
                
                body, code = self.send_request(upload_url, "POST", data=body_data, headers=headers)
                if code == 401: # Try to re-login once on 401 Unauthorized
                    if self.login():
                        body, code = self.send_request(upload_url, "POST", data=body_data, headers=headers)
                
                if code == 200:
                    self.log(f"  [OK] Successfully scanned SQL: {filename}")
                else:
                    self.log(f"  [ERROR] SQL scan failed (HTTP {code}): {body}")
            except Exception as e:
                self.log(f"  [ERROR] Reading SQL file: {e}")

        # 2. Test logs
        elif filename in ["pytest.log", "tests.log", "test.log", "test-results.xml"]:
            self.log(f"Test log file detected ({event_type}): {filename}")
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                upload_url = f"{self.base_url}/api/projects/{self.project_id}/guards/tests"
                body_data, headers = self.build_multipart(filename, content)
                
                body, code = self.send_request(upload_url, "POST", data=body_data, headers=headers)
                if code == 401:
                    if self.login():
                        body, code = self.send_request(upload_url, "POST", data=body_data, headers=headers)
                
                if code == 200:
                    self.log(f"  [OK] Successfully scanned test logs: {filename}")
                else:
                    # Try fallback to general logs guard
                    upload_url = f"{self.base_url}/api/projects/{self.project_id}/guards/logs"
                    body, code = self.send_request(upload_url, "POST", data=body_data, headers=headers)
                    if code == 200:
                        self.log(f"  [OK] Successfully scanned logs: {filename}")
                    else:
                        self.log(f"  [ERROR] Log scan failed (HTTP {code}): {body}")
            except Exception as e:
                self.log(f"  [ERROR] Reading log file: {e}")

        # 3. Environment Variables
        elif filename == ".env":
            self.log(f"Environment variables configuration change: {filename}")
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                upload_url = f"{self.base_url}/api/projects/{self.project_id}/env-guard"
                payload = json.dumps({
                    "content": content,
                    "required_keys": ["DATABASE_URL", "JWT_SECRET_KEY"]
                }).encode("utf-8")
                headers = {"Content-Type": "application/json"}
                
                body, code = self.send_request(upload_url, "POST", data=payload, headers=headers)
                if code == 401:
                    if self.login():
                        body, code = self.send_request(upload_url, "POST", data=payload, headers=headers)
                
                if code == 200:
                    findings = json.loads(body)
                    blockers = [f for f in findings if f.get("blocking")]
                    if blockers:
                        self.log("  ⚠️  [WARNING] Environmental compliance violations detected:")
                        for b in blockers:
                            self.log(f"    - [{b.get('severity')}] {b.get('message')}")
                    else:
                        self.log("  [OK] Environmental variables compliance checks passed.")
                else:
                    self.log(f"  [ERROR] Env scan failed (HTTP {code}): {body}")
            except Exception as e:
                self.log(f"  [ERROR] Analyzing env config: {e}")

    def run(self):
        # Initial login
        self.log(f"Connecting to DevFlow engine at {self.base_url}...")
        if not self.login():
            self.log("Warning: Initial connection failed. Will retry on demand.")
            
        self.log(f"Monitoring directory '{self.watch_dir}' for local changes...")
        
        # Check if watchfiles is available
        try:
            from watchfiles import watch
            self.log("Using system 'watchfiles' library for file monitoring.")
            for changes in watch(self.watch_dir):
                for change_type, filepath in changes:
                    # Ignore .venv, .git, node_modules, etc.
                    rel = os.path.relpath(filepath, self.watch_dir)
                    if any(part.startswith('.') or part == 'node_modules' or part == '__pycache__' for part in rel.split(os.sep)):
                        continue
                    
                    status_map = {1: "added", 2: "modified", 3: "deleted"}
                    event_type = status_map.get(change_type.value if hasattr(change_type, "value") else change_type, "modified")
                    
                    if event_type in ["added", "modified"]:
                        self.handle_file_change(filepath, event_type)
        except ImportError:
            self.log("Watchfiles library not available. Falling back to native directory polling (CPU-friendly 1.5s interval).")
            mtimes = {}
            while True:
                current_mtimes = {}
                for root, dirs, files in os.walk(self.watch_dir):
                    # Filter ignored directories
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.venv', '.pytest_cache']]
                    for f in files:
                        fpath = os.path.join(root, f)
                        try:
                            current_mtimes[fpath] = os.stat(fpath).st_mtime
                        except Exception:
                            pass
                
                # Check modifications
                for fpath, mtime in current_mtimes.items():
                    if fpath not in mtimes:
                        self.handle_file_change(fpath, "added")
                    elif mtimes[fpath] < mtime:
                        self.handle_file_change(fpath, "modified")
                
                mtimes = current_mtimes
                time.sleep(1.5)

def main():
    parser = argparse.ArgumentParser(
        description="DevFlow Guard auto-sync directory watcher."
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="DevFlow server base URL")
    parser.add_argument("--email", default=DEFAULT_EMAIL, help="User email")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="User password")
    parser.add_argument("--project", type=int, default=DEFAULT_PROJECT_ID, help="Project ID context")
    parser.add_argument("--dir", default=".", help="Directory folder path to watch")
    
    args = parser.parse_args()
    
    watcher = DevFlowWatcher(args.url, args.email, args.password, args.project, args.dir)
    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nDevFlow Watcher: Monitoring stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
