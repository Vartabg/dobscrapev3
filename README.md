# Dobscrape v4

## Overview
Dobscrape v4 is a Python desktop application for scraping and identifying active DOB (Department of Buildings) building violations in Brooklyn and Queens using NYC Open Data.

## Key Features
- Scrapes **only active violations** from Brooklyn and Queens
- Filters violations issued **on or after January 1, 2024**
- No keyword filtering (all active violations qualify)
- Outputs to a clean `violations.csv`
- GUI includes a **circular button**, **animated Israeli flag**, and a **"Mazel Tov" overlay**
- Final GUI button lets user **view results**, then **auto-exits**

## Installation

1. Ensure Python 3.12 is installed on your system
2. Clone this repository
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```
2. Click the "Start Scraping" button to begin
3. Wait for the scraping process to complete
4. When finished, click "View Results" to open the generated CSV file

## Key Changes in v4

- **Fixed keyword filtering issue** - Removed all keyword filtering code as specified in the requirements
- **Improved error handling** - Better error detection and feedback in the UI
- **Clearer user messaging** - Updated status messages to be more accurate
- **Optimized API queries** - Structured queries to minimize API calls

## File Structure

```
📦 dobscrapev4/
├── main.py               # Launches the GUI
├── gui.py                # GUI with flag animation and overlay
├── scraper_async.py      # Async scraper, filters by date, borough, active status
├── flag.gif              # Animated Israeli flag shown during scraping
├── mazel_tov.gif         # Animated Mazel Tov shown after scraping
├── requirements.txt      # Dependencies: aiohttp, pandas, PyQt6
└── violations.csv        # Output CSV with all filtered DOB records
```

## Next Steps

- Consider adding `enrich_owners.py` module to look up owner information
- Build `.exe` with PyInstaller:
  ```bash
  pyinstaller --onefile main.py
  ```
