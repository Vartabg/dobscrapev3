# Script to annotate files in the DOBScraper legacy archive

$sourceFolder = "C:\projects\dobscrape\archive\dobscrape_legacy"
$backupFolder = "C:\projects\dobscrape\archive\dobscrape_legacy_backup"

# Ensure the backup folder exists
if (-not (Test-Path -Path $backupFolder)) {
    New-Item -ItemType Directory -Path $backupFolder | Out-Null
}

# Define file filters
$filePatterns = @('gui', 'main', 'test', 'row', 'spec')
$skipPatterns = @('pytest', 'pandas', 'arrow', 'pyarrow', 'tester')
$annotationComment = "# Copilot: Summarize what this file does and why it may have been replaced or archived.`n"

# Loop through all .py and .spec files in the source folder
Get-ChildItem -Path $sourceFolder -Recurse -Include *.py, *.spec | ForEach-Object {
    $fileName = $_.Name
    $filePath = $_.FullName

    # Check if the file name contains any of the required patterns
    if ($filePatterns -notcontains ($filePatterns | Where-Object { $fileName -like "*$_*" })) {
        return
    }

    # Skip files that contain any of the skip patterns
    if ($skipPatterns -contains ($skipPatterns | Where-Object { $fileName -like "*$_*" })) {
        return
    }

    # Read the first line of the file
    $firstLine = Get-Content -Path $filePath -TotalCount 1

    # Check if the file is already annotated
    if ($firstLine -eq $annotationComment.TrimEnd()) {
        Write-Host "⏭️ Skipped (already annotated): $fileName"
        return
    }

    # Backup the file before modifying it
    $backupPath = Join-Path -Path $backupFolder -ChildPath $fileName
    Copy-Item -Path $filePath -Destination $backupPath -Force
    Write-Host "📦 Backed up: $fileName → dobscrape_legacy_backup/"

    # Preserve timestamp
    $originalTimestamp = Get-Item -Path $filePath | Select-Object -ExpandProperty LastWriteTime

    # Insert the annotation comment at the top of the file
    $fileContents = Get-Content -Path $filePath
    $annotatedContents = @($annotationComment) + $fileContents
    $annotatedContents | Set-Content -Path $filePath

    # Restore timestamp
    (Get-Item -Path $filePath).LastWriteTime = $originalTimestamp

    # Log the update
    Write-Host "✅ Updated: $fileName"
}

Write-Host "✅ Annotation complete for all DOBScraper legacy files."