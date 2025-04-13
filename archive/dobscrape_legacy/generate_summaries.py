"""
Copilot:
This script scans all .py and .spec files in the legacy folder and generates markdown summaries.

For each file, generate a .md file with the following fields:
- File Name
- Purpose or intended functionality
- AI Author (ChatGPT, Claude, Gemini, or Unknown)
- Known issues or why it was replaced
- What replaced it (if known)
- Timestamp archived (use filename if possible)

Summaries should be saved to: archive/dobscrape_legacy/summaries/
"""

import os
from datetime import datetime

source_dir = "archive/dobscrape_legacy"
output_dir = os.path.join(source_dir, "summaries")
os.makedirs(output_dir, exist_ok=True)

def extract_date_from_filename(filename):
    # Example: gui_testable_2025_04_12.py → 2025-04-12
    parts = filename.split("_")
    for i in range(len(parts)):
        if parts[i].isdigit() and len(parts[i]) == 4 and i+2 < len(parts):
            return f"{parts[i]}-{parts[i+1]}-{parts[i+2][:2]}"
    return "Unknown"

for file in os.listdir(source_dir):
    if file.endswith((".py", ".spec")) and "summary" not in file:
        filepath = os.path.join(source_dir, file)
        base_name = os.path.splitext(file)[0]
        summary_path = os.path.join(output_dir, f"{base_name}.md")

        archive_date = extract_date_from_filename(file)

        with open(summary_path, "w") as f:
            f.write(f"# Summary for `{file}`\n\n")
            f.write(f"**File Name:** {file}\n\n")
            f.write(f"**Purpose:** _Copilot: Describe what this file was doing._\n\n")
            f.write(f"**AI Author:** _Copilot: Likely author? (Claude, ChatGPT, etc.)_\n\n")
            f.write(f"**Reason for Archival:** _Copilot: Why was this replaced or deprecated?_\n\n")
            f.write(f"**Replacement File:** _Copilot: What is the newer file that replaced this?_ \n\n")
            f.write(f"**Archived On:** {archive_date}\n")
