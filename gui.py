# gui.py (Rewritten to match exact approved UI spec)

import sys
import os
import subprocess
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy, QSpacerItem, QGridLayout
)
from PyQt6.QtGui import QMovie, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer

import pandas as pd
from scraper_async import scrape_violations
from excel_generator import generate_excel

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class ScrapeWorker(QThread):
    finished = pyqtSignal(object)

    def __init__(self, start_date):
        super().__init__()
        self.start_date = start_date

    def run(self):
        results = scrape_violations(self.start_date)
        self.finished.emit(results)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("")  # No title bar text
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: white;")
        
        # Load Jewish-style font if available
        font_path = resource_path("assets/FrankRuhlLibre-Regular.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                self.jewish_font = QFontDatabase.applicationFontFamilies(font_id)[0]
            else:
                self.jewish_font = "Arial"
        else:
            self.jewish_font = "Arial"
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Build all screens
        self.home_screen = self.build_home_screen()
        self.date_range_screen = self.build_date_range_screen()
        self.flag_screen = self.build_flag_screen()
        self.results_screen = None  # Will be built dynamically
        
        # Add screens to stack
        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.date_range_screen)
        self.stack.addWidget(self.flag_screen)

    def build_home_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the start button
        start_button = QPushButton("Start")
        start_button.setFixedSize(200, 200)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 100px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        """)
        start_button.clicked.connect(self.show_date_range)
        
        # Center the button
        layout.addStretch()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(start_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def build_date_range_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Define date ranges
        self.date_ranges = {
            "Last 30 Days": datetime.now() - timedelta(days=30),
            "3 Months": datetime.now() - timedelta(days=90),
            "6 Months": datetime.now() - timedelta(days=180),
            "Past Year": datetime.now() - timedelta(days=365),
            "Past 2 Years": datetime.now() - timedelta(days=730),
            "All Since 2020": datetime(2020, 1, 1),
        }
        
        # Create a grid layout for the buttons
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        # Date range buttons in a hex-grid layout
        button_style = """
            QPushButton {
                background-color: #0038b8;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 50px;
                padding: 15px;
                min-width: 150px;
                min-height: 100px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        """
        
        # Add buttons in a grid pattern to mimic circular or hex-grid layout
        options = list(self.date_ranges.keys())
        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
        
        for i, (option, position) in enumerate(zip(options, positions)):
            button = QPushButton(option)
            button.setStyleSheet(button_style)
            button.clicked.connect(lambda _, opt=option: self.start_scrape(self.date_ranges[opt]))
            grid_layout.addWidget(button, position[0], position[1])
        
        # Center the grid
        layout.addStretch()
        centered_layout = QHBoxLayout()
        centered_layout.addStretch()
        centered_layout.addLayout(grid_layout)
        centered_layout.addStretch()
        layout.addLayout(centered_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def build_flag_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Flag animation
        self.flag_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        flag_layout = QHBoxLayout()
        flag_layout.addStretch()
        flag_layout.addWidget(self.flag_label)
        flag_layout.addStretch()
        layout.addLayout(flag_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def build_results_screen(self, success):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        if success:
            # Success screen with Mazel Tov GIF and View Results button
            self.result_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
            
            view_results_button = QPushButton("View Results")
            view_results_button.setFixedSize(150, 150)
            view_results_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 75px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            view_results_button.clicked.connect(self.view_results)
            
            layout.addStretch()
            result_layout = QHBoxLayout()
            result_layout.addStretch()
            result_layout.addWidget(self.result_label)
            result_layout.addStretch()
            layout.addLayout(result_layout)
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(view_results_button)
            button_layout.addStretch()
            layout.addLayout(button_layout)
            layout.addStretch()
        else:
            # No results screen with Oy Vey GIF and message
            self.result_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
            
            # Error message with Jewish-style font
            error_message = QLabel("Sorry, no results found. Try a different time range or fuck off.")
            error_message.setFont(QFont(self.jewish_font, 16, QFont.Weight.Bold))
            error_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_message.setStyleSheet("color: #0038b8; margin: 20px 0;")
            
            # Two circular buttons: Home and Close
            button_style = """
                QPushButton {
                    background-color: #0038b8;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 50px;
                    min-width: 100px;
                    min-height: 100px;
                }
                QPushButton:hover {
                    background-color: #004fd6;
                }
            """
            
            home_button = QPushButton("Home")
            home_button.setFixedSize(100, 100)
            home_button.setStyleSheet(button_style)
            home_button.clicked.connect(self.return_home)
            
            close_button = QPushButton("Close")
            close_button.setFixedSize(100, 100)
            close_button.setStyleSheet(button_style)
            close_button.clicked.connect(self.close)
            
            layout.addStretch()
            
            result_layout = QHBoxLayout()
            result_layout.addStretch()
            result_layout.addWidget(self.result_label)
            result_layout.addStretch()
            layout.addLayout(result_layout)
            
            layout.addWidget(error_message)
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(home_button)
            button_layout.addSpacing(30)  # Space between buttons
            button_layout.addWidget(close_button)
            button_layout.addStretch()
            layout.addLayout(button_layout)
            
            layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def show_date_range(self):
        self.stack.setCurrentWidget(self.date_range_screen)

    def start_scrape(self, start_date):
        self.stack.setCurrentWidget(self.flag_screen)
        
        # Start the flag animation
        flag_path = resource_path("assets/israel_flag.gif")
        self.movie = QMovie(flag_path)
        self.flag_label.setMovie(self.movie)
        self.movie.start()
        
        # Start the scraper thread
        self.scraper = ScrapeWorker(start_date)
        self.scraper.finished.connect(self.scrape_done)
        self.scraper.start()

    def scrape_done(self, result):
        # Stop the flag animation
        self.movie.stop()
        
        # Set up the appropriate results screen based on whether we got results
        has_results = not result.empty
        
        if has_results:
            # Generate the Excel file
            generate_excel(result)
            
            # Build the success results screen
            self.results_screen = self.build_results_screen(True)
            self.stack.addWidget(self.results_screen)
            
            # Show the Mazel Tov GIF
            gif_path = resource_path("assets/mazeltov.gif")
            self.result_movie = QMovie(gif_path)
            self.result_label.setMovie(self.result_movie)
            self.result_movie.start()
            
            # Count how many times we've looped the GIF (exact 3 times)
            self.gif_loop_count = 0
            
            def check_loop():
                self.gif_loop_count += 1
                if self.gif_loop_count >= 3:
                    self.result_movie.stop()
                    self.result_label.clear()  # Hide the GIF
                else:
                    # Check again after the movie duration
                    frame_count = self.result_movie.frameCount()
                    if frame_count > 0:
                        duration = self.result_movie.nextFrameDelay() * frame_count
                        QTimer.singleShot(duration, check_loop)
            
            # Start the loop counter when the first frame finishes
            frame_count = self.result_movie.frameCount()
            if frame_count > 0:
                duration = self.result_movie.nextFrameDelay() * frame_count
                QTimer.singleShot(duration, check_loop)
        else:
            # Build the no results screen
            self.results_screen = self.build_results_screen(False)
            self.stack.addWidget(self.results_screen)
            
            # Show the Oy Vey GIF
            gif_path = resource_path("assets/oyvey.gif")
            self.result_movie = QMovie(gif_path)
            self.result_label.setMovie(self.result_movie)
            self.result_movie.start()
            
            # Count how many times we've looped the GIF (exact 2 times)
            self.gif_loop_count = 0
            
            def check_loop():
                self.gif_loop_count += 1
                if self.gif_loop_count >= 2:
                    self.result_movie.stop()
                else:
                    # Check again after the movie duration
                    frame_count = self.result_movie.frameCount()
                    if frame_count > 0:
                        duration = self.result_movie.nextFrameDelay() * frame_count
                        QTimer.singleShot(duration, check_loop)
            
            # Start the loop counter when the first frame finishes
            frame_count = self.result_movie.frameCount()
            if frame_count > 0:
                duration = self.result_movie.nextFrameDelay() * frame_count
                QTimer.singleShot(duration, check_loop)
        
        # Switch to the result screen
        self.stack.setCurrentWidget(self.results_screen)

    def view_results(self):
        path = os.path.abspath("violations.xlsx")
        try:
            subprocess.Popen(["start", path], shell=True)
        except Exception:
            pass  # Silently fail as per spec (no alerts/popups)
        self.close()  # Exit app after viewing

    def return_home(self):
        # Remove current results screen
        if self.results_screen:
            self.stack.removeWidget(self.results_screen)
            self.results_screen = None
        
        # Return to home screen
        self.stack.setCurrentWidget(self.home_screen)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
