# PowerShell Cleanup Script for DOBScraper Project
# Author: ChatGPT (AI Assistant to Garo Vartabedian)
# Date: April 12, 2025

# Set your project root directory (change this if your folder is not on Desktop)
$root = "$env:USERPROFILE\Desktop\dobscrape"
$archive = Join-Path $root "archive\dobscrape_legacy"

# Create archive folder if it doesn't exist
if (!(Test-Path $archive)) {
    New-Item -Path $archive -ItemType Directory -Force | Out-Null
}

# Define files to archive by loose match
$patterns = @(
    "gui_debug.py", "gui_kinter.py", "gui_testable.py", "gui_minimal.py", "main.py", "qt_test.py",
    "Mr4InARow.spec", "gui_embed_assets.spec", "gui.spec", "test_assets.py"
)

foreach ($pattern in $patterns) {
    $file = Join-Path $root $pattern
    if (Test-Path $file) {
        Write-Output "📦 Archiving $pattern..."
        $timestamp = Get-Date -Format "yyyy_MM_dd"
        $basename = [System.IO.Path]::GetFileNameWithoutExtension($file)
        $ext = [System.IO.Path]::GetExtension($file)
        $archivedName = "${basename}_${timestamp}${ext}"
        $destination = Join-Path $archive $archivedName
        Move-Item -Path $file -Destination $destination -Force
    }
}

Write-Output ""
Write-Output "✅ Cleanup complete! All legacy files moved to:"
Write-Output $archive