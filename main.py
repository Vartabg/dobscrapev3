#!/usr/bin/env python3
"""
Dobscrape v4 - DOB Violations Scraper
Main entry point that launches the GUI
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui import MainWindow

def main():
    """Launch the DOB Violations Scraper GUI application"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
