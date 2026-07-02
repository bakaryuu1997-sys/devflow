# Creates a "DevFlow Guard" shortcut on your Desktop that launches run.bat.
# Usage (from the project folder):  powershell -ExecutionPolicy Bypass -File scripts\create_shortcut.ps1

$root = Split-Path -Parent $PSScriptRoot
$target = Join-Path $root "run.bat"
if (-not (Test-Path $target)) {
    Write-Error "run.bat not found next to the project root ($target)."
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
$linkPath = Join-Path $desktop "DevFlow Guard.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($linkPath)
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = $root
$shortcut.Description = "Launch DevFlow Guard locally (no login)"
# A globe-style icon from the Windows shell icon library.
$shortcut.IconLocation = "$env:SystemRoot\System32\SHELL32.dll,13"
$shortcut.Save()

Write-Host "Created shortcut: $linkPath"
Write-Host "Double-click it to start DevFlow Guard, then open http://127.0.0.1:8000"
