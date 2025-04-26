#!/usr/bin/env python3
"""
Mr. 4 in a Row (DOBScraper)
----------------------------
Main entry point for the DOB Violations Scraper application.

This program scrapes NYC Department of Buildings violations data
for Brooklyn and Queens, displaying an animated Israeli flag during
the process and a "Mazel Tov" celebration upon completion.

Author: Garo Vartabedian
Version: 1.0.0 (2025-04-12)
"""

import os
import sys
from gui import DOBScraperGUI
from PyQt6.QtWidgets import QApplication

def check_directories():
    """Ensure the required directories exist"""
    if not os.path.exists("assets"):
        os.makedirs("assets")
        print("Created assets directory")

def main():
    """Main function to start the application"""
    # Check for required directories
    check_directories()
    
    # Start the Qt application
    app = QApplication(sys.argv)
    window = DOBScraperGUI()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
