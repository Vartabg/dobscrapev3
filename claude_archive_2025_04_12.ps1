# DOBScraper Legacy Files Archiving Script
# Date: April 12, 2025

# Define source directories to scan
$sourceDirs = @(
    "C:\Users\garov\Desktop",
    "C:\projects\dobscrape"
)

# Define target directory for archived files
$targetDir = "C:\projects\dobscrape\archive\dobscrape_legacy"

# Create the target directory if it doesn't exist
if (-not (Test-Path -Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    Write-Host "Created target directory: $targetDir"
}

# Get today's date in yyyy_MM_dd format
$timestamp = Get-Date -Format "yyyy_MM_dd"

# Files to exclude (exact matches)
$excludeExactFiles = @(
    "gui.py",
    "scraper_async.py",
    "excel_generator.py"
)

# Keywords to search for in filenames
$includeKeywords = @(
    "gui",
    "main",
    "test",
    "row",
    "spec"
)

# Function to check if a file should be included
function ShouldIncludeFile {
    param (
        [string]$filePath,
        [string]$fileName
    )

    # Check file extension (.py or .spec)
    $extension = [System.IO.Path]::GetExtension($fileName)
    if ($extension -ne ".py" -and $extension -ne ".spec") {
        return $false
    }

    # Check if file is in an 'archive' directory
    if ($filePath -match "\\archive\\") {
        return $false
    }

    # Check if the file is in the exclusion list
    if ($excludeExactFiles -contains $fileName) {
        return $false
    }

    # Check if filename contains any of the include keywords
    foreach ($keyword in $includeKeywords) {
        if ($fileName -match $keyword) {
            return $true
        }
    }

    return $false
}

# Process each source directory
foreach ($sourceDir in $sourceDirs) {
    Write-Host "Scanning directory: $sourceDir"
    
    # Get all files recursively
    $files = Get-ChildItem -Path $sourceDir -File -Recurse -ErrorAction SilentlyContinue
    
    foreach ($file in $files) {
        $fileName = $file.Name
        $filePath = $file.FullName
        
        if (ShouldIncludeFile -filePath $filePath -fileName $fileName) {
            # Generate new filename with timestamp
            $fileNameWithoutExt = [System.IO.Path]::GetFileNameWithoutExtension($fileName)
            $extension = [System.IO.Path]::GetExtension($fileName)
            $newFileName = "${fileNameWithoutExt}_${timestamp}${extension}"
            $targetPath = Join-Path -Path $targetDir -ChildPath $newFileName
            
            # Move the file to the target directory with new name
            try {
                Move-Item -Path $filePath -Destination $targetPath -Force
                Write-Host "Moved $filePath -> $targetPath"
            }
            catch {
                Write-Host "Failed to move file: $filePath. Error: $_"
            }
        }
    }
}

Write-Host "Archive operation completed."
