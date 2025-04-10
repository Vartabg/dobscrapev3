#!/usr/bin/env python3
"""
Dobscrape v4 - DOB Violations Scraper
GUI module for handling the user interface, animations, and flow
"""

import os
import subprocess
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QMovie, QIcon
import pandas as pd

from scraper_async import scrape_violations

class MainWindow(QMainWindow):
    """Main window for the DOB Violations Scraper application"""
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("DOB Violations Scraper")
        self.setFixedSize(600, 500)
        
        # Set up the central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create the circular button
        self.button = QPushButton("Start Scraping")
        self.button.setFixedSize(200, 200)
        self.button.setStyleSheet("""
            QPushButton {
                border-radius: 100px;
                background-color: #2196F3;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0D47A1;
            }
        """)
        self.button.clicked.connect(self.start_scraping)
        
        # Create status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #FF9800; font-size: 16px;")
        
        # Add widgets to layout
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.status_label)
        
        # Prepare animations
        self.flag_movie = QMovie("flag.gif")
        self.flag_movie.setScaledSize(QSize(200, 200))
        
        self.mazel_tov_movie = QMovie("mazel_tov.gif")
        self.mazel_tov_movie.setScaledSize(QSize(400, 300))
        
        # Animation container (initially hidden)
        self.animation_label = QLabel()
        self.animation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.animation_label.hide()
        self.layout.addWidget(self.animation_label)
        
        self.is_scraping = False
        self.violations_data = None

    def start_scraping(self):
        """Start the scraping process with animations"""
        if self.is_scraping:
            return
            
        self.is_scraping = True
        self.button.setEnabled(False)
        self.status_label.setText("Scraping violations...")
        
        # Show flag animation
        self.animation_label.setMovie(self.flag_movie)
        self.animation_label.show()
        self.flag_movie.start()
        
        # Start the scraping in a separate timer to allow the UI to update
        QTimer.singleShot(100, self.perform_scraping)
    
    def perform_scraping(self):
        """Perform the actual scraping operation"""
        try:
            self.violations_data = scrape_violations()
            
            # Check if we got any data
            if self.violations_data is None or self.violations_data.empty:
                self.show_no_results()
            else:
                # Save to CSV
                self.violations_data.to_csv("violations.csv", index=False)
                self.show_success()
        except Exception as e:
            print(f"Error during scraping: {e}")
            self.show_error(str(e))
    
    def show_no_results(self):
        """Show the no results state"""
        self.flag_movie.stop()
        self.animation_label.hide()
        
        # Update button and status
        self.button.setText("Retry")
        self.button.setEnabled(True)
        self.status_label.setText("No violations found matching your criteria.")
        self.is_scraping = False
    
    def show_error(self, error_message):
        """Show error state"""
        self.flag_movie.stop()
        self.animation_label.hide()
        
        # Update button and status
        self.button.setText("Retry")
        self.button.setEnabled(True)
        self.status_label.setText(f"Error: {error_message}")
        self.is_scraping = False
    
    def show_success(self):
        """Show success state with Mazel Tov animation"""
        self.flag_movie.stop()
        
        # Show Mazel Tov animation
        self.animation_label.setMovie(self.mazel_tov_movie)
        self.mazel_tov_movie.start()
        
        # Update button and status
        self.button.setText("View Results")
        self.button.setEnabled(True)
        self.status_label.setText(f"Found {len(self.violations_data)} violations! Saved to violations.csv")
        
        # Connect the button to view results
        self.button.clicked.disconnect()
        self.button.clicked.connect(self.view_results)
        self.is_scraping = False
    
    def view_results(self):
        """Open the CSV file and exit the application"""
        try:
            if sys.platform == 'win32':
                os.startfile("violations.csv")
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', "violations.csv"], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', "violations.csv"], check=True)
        except Exception as e:
            print(f"Error opening CSV: {e}")
        
        # Exit the application after a short delay
        QTimer.singleShot(300, self.close)
