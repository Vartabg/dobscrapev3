# Step 1: Inject Copilot instruction
$guiPath = "gui.py"
$copilotComment = "# Copilot: Please rewrite this file so it does not write to disk at runtime and ensures UTF-8 is used for all text operations. Eliminate usage of Path().write_text(). Integrate the GUI logic directly into the application."

# Add the comment if not already present
if (-not (Select-String -Path $guiPath -Pattern "Copilot: Please rewrite")) {
    $existing = Get-Content $guiPath
    Set-Content -Path $guiPath -Value "$copilotComment`n$existing"
    Write-Host "✅ Injected Copilot directive."
}

# Step 2: Open VSCode for Copilot to act
code $guiPath
Read-Host -Prompt "🛠️ Please let Copilot rewrite the file. Press Enter to continue once done"

# Step 3: Commit & Push
git add $guiPath
git commit -m "🧠 Copilot: Rewrote gui.py to inline GUI and fix UTF-8 encoding"
git push
Write-Host "✅ Pushed changes to GitHub."

# Step 4: Rebuild with PyInstaller
pyinstaller --clean DOBScraper.spec

# Step 5: Launch .exe
$exePath = ".\dist\DOBScraper.exe"
if (Test-Path $exePath) {
    Start-Process $exePath
    Write-Host "🚀 Launched DOBScraper.exe"
} else {
    Write-Host "❌ Executable not found."
}