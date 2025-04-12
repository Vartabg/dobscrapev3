# Dual-Source DOBScraper Legacy Archiver
# Author: ChatGPT, April 12, 2025

$desktopSource = "$env:USERPROFILE\Desktop"
$projectSource = "C:\projects\dobscrape"
$archiveDest = "C:\projects\dobscrape\archive\dobscrape_legacy"

# Create archive folder if it doesn't exist
if (!(Test-Path $archiveDest)) {
    New-Item -Path $archiveDest -ItemType Directory -Force | Out-Null
}

# Define reusable archive function
function Archive-MatchingFiles($sourcePath) {
    Write-Output "`n📂 Scanning: $sourcePath"

    $matches = Get-ChildItem $sourcePath -Recurse -Include *.py,*.spec -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -match "gui|main|test|spec|row" -and
            $_.Name -notmatch "^gui\.py$" -and
            $_.FullName -notmatch "archive"
        }

    foreach ($file in $matches) {
        try {
            $timestamp = Get-Date -Format "yyyy_MM_dd"
            $basename = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
            $ext = [System.IO.Path]::GetExtension($file.Name)
            $archivedName = "${basename}_${timestamp}${ext}"
            $destination = Join-Path $archiveDest $archivedName
            Move-Item -Path $file.FullName -Destination $destination -Force
            Write-Output "✅ Moved $($file.Name) → $archivedName"
        }
        catch {
            Write-Output "❌ Failed to move $($file.FullName): $_"
        }
    }
}

# Run archive on both locations
Archive-MatchingFiles -sourcePath $desktopSource
Archive-MatchingFiles -sourcePath $projectSource

Write-Output "`n✔️  Dual-location cleanup complete. Legacy files archived to:"
Write-Output $archiveDest