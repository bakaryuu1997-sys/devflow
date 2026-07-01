import subprocess
import sys


def test_cli_help_menu():
    # Invoke the devflow_cli.py help menu
    result = subprocess.run([sys.executable, "scripts/devflow_cli.py", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "DevFlow Guard Personal Command-line compliance interface" in result.stdout
    assert "scan" in result.stdout
    assert "status" in result.stdout
    assert "install-hook" in result.stdout


def test_cli_subcommands_help():
    # Test scan subcommand help
    result = subprocess.run(
        [sys.executable, "scripts/devflow_cli.py", "scan", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "--migrations" in result.stdout
    assert "--test-logs" in result.stdout

    # Test status subcommand help
    result = subprocess.run(
        [sys.executable, "scripts/devflow_cli.py", "status", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0

    # Test install-hook subcommand help
    result = subprocess.run(
        [sys.executable, "scripts/devflow_cli.py", "install-hook", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
