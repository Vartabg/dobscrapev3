import sys
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QWidget, QLabel, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QMovie, QFont, QColor, QPalette, QIcon
from PyQt6.QtCore import pyqtSignal, QThread

# Placeholder imports for when you reconnect these components
# from scraper_async import fetch_violations
# from excel_generator import generate_excel

# Constants for styling
ISRAEL_BLUE = "#0038b8"
ISRAEL_WHITE = "#ffffff"
GREEN_ACCENT = "#2ecc71"
BUTTON_STYLE = """
    QPushButton {
        background-color: #0038b8;
        color: white;
        border-radius: 20px;
        font-size: 16px;
        padding: 10px 20px;
        min-width: 120px;
        min-height: 40px;
    }
    QPushButton:hover {
        background-color: #0046e5;
    }
    QPushButton:pressed {
        background-color: #002c8a;
    }
"""
CIRCULAR_BUTTON_STYLE = """
    QPushButton {
        background-color: #0038b8;
        color: white;
        border-radius: 25px;
        font-size: 16px;
        min-width: 50px;
        min-height: 50px;
    }
    QPushButton:hover {
        background-color: #0046e5;
    }
    QPushButton:pressed {
        background-color: #002c8a;
    }
"""
DATE_BUTTON_STYLE = """
    QPushButton {
        background-color: #ffffff;
        color: #0038b8;
        border: 2px solid #0038b8;
        border-radius: 15px;
        font-size: 14px;
        padding: 8px 15px;
        min-width: 150px;
        margin: 5px;
    }
    QPushButton:hover {
        background-color: #e6f0ff;
    }
    QPushButton:pressed {
        background-color: #c4d9ff;
    }
    QPushButton:checked {
        background-color: #0038b8;
        color: white;
    }
"""

class WorkerThread(QThread):
    """Worker thread for running data fetching operations asynchronously"""
    finished = pyqtSignal(bool)  # Signal emits True if results were found, False otherwise
    
    def __init__(self, date_range):
        super().__init__()
        self.date_range = date_range
        
    def run(self):
        # This is a placeholder for the actual fetch_violations and generate_excel functions
        # When you reconnect the components, replace this with actual calls
        
        # Simulate processing time (3 seconds)
        self.sleep(3)
        
        # For demonstration, we'll assume results were found
        # When connecting real logic, replace this with actual result detection
        results_found = True  # Set to False to test the "Oy Vey" screen
        
        # Emit signal with the result status
        self.finished.emit(results_found)


class Mr4InARowApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up the main window
        self.setWindowTitle("Mr. 4 in a Row")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(f"background-color: {ISRAEL_WHITE};")
        
        # Set up central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Initialize the start screen
        self.init_start_screen()
        
        # Initialize other screens but don't show them yet
        self.date_range_widget = None
        self.loading_widget = None
        self.results_widget = None
        self.oyvey_widget = None
        
    def init_start_screen(self):
        """Initialize the start screen with a centered start button"""
        self.start_widget = QWidget()
        start_layout = QVBoxLayout(self.start_widget)
        start_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add title
        title_label = QLabel("Mr. 4 in a Row")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ISRAEL_BLUE};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        start_layout.addWidget(title_label)
        
        # Add some spacing
        start_layout.addSpacing(20)
        
        # Add start button
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet(BUTTON_STYLE)
        self.start_button.setFixedSize(150, 50)
        self.start_button.clicked.connect(self.show_date_range_screen)
        start_layout.addWidget(self.start_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Add to main layout
        self.main_layout.addWidget(self.start_widget)
        
    def init_date_range_screen(self):
        """Initialize the date range selection screen with 6 options"""
        self.date_range_widget = QWidget()
        date_layout = QVBoxLayout(self.date_range_widget)
        date_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add title
        title_label = QLabel("Select Date Range")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ISRAEL_BLUE};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_layout.addWidget(title_label)
        
        # Add date range options
        date_options_layout = QGridLayout()
        date_options_layout.setSpacing(10)
        
        # Create 6 date range options
        self.date_buttons = []
        date_ranges = [
            ("Last 24 Hours", self.get_date_range(1)),
            ("Last 3 Days", self.get_date_range(3)),
            ("Last Week", self.get_date_range(7)),
            ("Last Month", self.get_date_range(30)),
            ("Last 3 Months", self.get_date_range(90)),
            ("Last Year", self.get_date_range(365))
        ]
        
        # Add buttons in a 3x2 grid
        for i, (label, date_range) in enumerate(date_ranges):
            button = QPushButton(label)
            button.setStyleSheet(DATE_BUTTON_STYLE)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, b=button, d=date_range: self.select_date_range(b, d))
            row, col = divmod(i, 2)
            date_options_layout.addWidget(button, row, col)
            self.date_buttons.append(button)
            
        date_layout.addLayout(date_options_layout)
        
        # Add button container
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Back button
        back_button = QPushButton("Back")
        back_button.setStyleSheet(BUTTON_STYLE)
        back_button.clicked.connect(self.show_start_screen)
        button_layout.addWidget(back_button)
        
        # Space between buttons
        button_layout.addSpacing(20)
        
        # Fetch button
        self.fetch_button = QPushButton("Fetch Data")
        self.fetch_button.setStyleSheet(BUTTON_STYLE)
        self.fetch_button.setEnabled(False)  # Disabled until a date range is selected
        self.fetch_button.clicked.connect(self.start_data_fetch)
        button_layout.addWidget(self.fetch_button)
        
        date_layout.addLayout(button_layout)
        
        # Add to main layout but hide initially
        self.main_layout.addWidget(self.date_range_widget)
        self.date_range_widget.hide()
        
    def init_loading_screen(self):
        """Initialize the loading screen with the Israeli flag animation"""
        self.loading_widget = QWidget()
        loading_layout = QVBoxLayout(self.loading_widget)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add loading label
        loading_label = QLabel("Fetching Data...")
        loading_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        loading_label.setStyleSheet(f"color: {ISRAEL_BLUE};")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_layout.addWidget(loading_label)
        
        # Add flag animation
        flag_label = QLabel()
        flag_path = os.path.join("assets", "israel_flag.gif")
        
        if os.path.exists(flag_path):
            self.flag_movie = QMovie(flag_path)
            self.flag_movie.setScaledSize(QSize(300, 200))
            flag_label.setMovie(self.flag_movie)
            flag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            loading_layout.addWidget(flag_label)
        else:
            # Fallback if GIF is not found
            fallback_label = QLabel("🇮🇱 Fetching data... 🇮🇱")
            fallback_label.setFont(QFont("Arial", 16))
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            loading_layout.addWidget(fallback_label)
        
        # Add to main layout but hide initially
        self.main_layout.addWidget(self.loading_widget)
        self.loading_widget.hide()
        
    def init_results_screen(self):
        """Initialize the success screen with Mazel Tov animation"""
        self.results_widget = QWidget()
        results_layout = QVBoxLayout(self.results_widget)
        results_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add success label
        success_label = QLabel("Success!")
        success_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        success_label.setStyleSheet(f"color: {GREEN_ACCENT};")
        success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_layout.addWidget(success_label)
        
        # Add Mazel Tov animation
        mazel_tov_label = QLabel()
        mazel_tov_path = os.path.join("assets", "mazel_tov.gif")
        
        if os.path.exists(mazel_tov_path):
            self.mazel_tov_movie = QMovie(mazel_tov_path)
            self.mazel_tov_movie.setScaledSize(QSize(300, 200))
            mazel_tov_label.setMovie(self.mazel_tov_movie)
            mazel_tov_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            results_layout.addWidget(mazel_tov_label)
        else:
            # Fallback if GIF is not found
            fallback_label = QLabel("🎉 Mazel Tov! 🎉")
            fallback_label.setFont(QFont("Arial", 18))
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            results_layout.addWidget(fallback_label)
            
        # Add the "View Results" button (initially hidden)
        self.view_results_button = QPushButton("View Results")
        self.view_results_button.setStyleSheet(BUTTON_STYLE)
        self.view_results_button.clicked.connect(self.view_results)
        self.view_results_button.hide()  # Hidden until animation completes
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Back to start button
        home_button = QPushButton("Home")
        home_button.setStyleSheet(CIRCULAR_BUTTON_STYLE)
        home_button.clicked.connect(self.show_start_screen)
        button_layout.addWidget(home_button)
        
        # Add view results button to layout
        button_layout.addWidget(self.view_results_button)
        
        results_layout.addLayout(button_layout)
        
        # Add to main layout but hide initially
        self.main_layout.addWidget(self.results_widget)
        self.results_widget.hide()
        
    def init_oyvey_screen(self):
        """Initialize the 'Oy Vey' screen for when no results are found"""
        self.oyvey_widget = QWidget()
        oyvey_layout = QVBoxLayout(self.oyvey_widget)
        oyvey_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add Oy Vey label
        oyvey_label = QLabel("Oy Vey!")
        oyvey_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        oyvey_label.setStyleSheet("color: #e74c3c;")  # Red color for the error
        oyvey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        oyvey_layout.addWidget(oyvey_label)
        
        # Add explanation
        explanation_label = QLabel("No results found for the selected date range.")
        explanation_label.setFont(QFont("Arial", 16))
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        oyvey_layout.addWidget(explanation_label)
        
        # Add Oy Vey animation or image if available
        oyvey_image_label = QLabel()
        oyvey_path = os.path.join("assets", "oyvey.gif")
        
        if os.path.exists(oyvey_path):
            self.oyvey_movie = QMovie(oyvey_path)
            self.oyvey_movie.setScaledSize(QSize(250, 200))
            oyvey_image_label.setMovie(self.oyvey_movie)
            oyvey_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            oyvey_layout.addWidget(oyvey_image_label)
        else:
            # Fallback if image is not found
            fallback_label = QLabel("😕")
            fallback_label.setFont(QFont("Arial", 72))
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            oyvey_layout.addWidget(fallback_label)
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(30)
        
        # Home button (circular)
        home_button = QPushButton("🏠")
        home_button.setStyleSheet(CIRCULAR_BUTTON_STYLE)
        home_button.setFixedSize(60, 60)
        home_button.clicked.connect(self.show_start_screen)
        button_layout.addWidget(home_button)
        
        # Close button (circular)
        close_button = QPushButton("❌")
        close_button.setStyleSheet(CIRCULAR_BUTTON_STYLE)
        close_button.setFixedSize(60, 60)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        oyvey_layout.addLayout(button_layout)
        
        # Add to main layout but hide initially
        self.main_layout.addWidget(self.oyvey_widget)
        self.oyvey_widget.hide()
    
    # Utility Methods
    def get_date_range(self, days):
        """Generate a date range tuple (start_date, end_date) for the given number of days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return (start_date, end_date)
    
    def select_date_range(self, button, date_range):
        """Handle date range selection"""
        # Uncheck all other buttons
        for btn in self.date_buttons:
            if btn != button:
                btn.setChecked(False)
        
        # Store the selected date range
        self.selected_date_range = date_range
        
        # Enable the fetch button
        self.fetch_button.setEnabled(button.isChecked())
    
    # Screen Navigation Methods
    def show_start_screen(self):
        """Show the start screen, hide all others"""
        # Hide all screens
        if self.date_range_widget:
            self.date_range_widget.hide()
        if self.loading_widget:
            self.loading_widget.hide()
            if hasattr(self, 'flag_movie') and self.flag_movie:
                self.flag_movie.stop()
        if self.results_widget:
            self.results_widget.hide()
            if hasattr(self, 'mazel_tov_movie') and self.mazel_tov_movie:
                self.mazel_tov_movie.stop()
        if self.oyvey_widget:
            self.oyvey_widget.hide()
            if hasattr(self, 'oyvey_movie') and self.oyvey_movie:
                self.oyvey_movie.stop()
        
        # Show start screen
        self.start_widget.show()
    
    def show_date_range_screen(self):
        """Show the date range selection screen"""
        # Initialize if not already
        if not self.date_range_widget:
            self.init_date_range_screen()
        
        # Hide all screens
        self.start_widget.hide()
        if self.loading_widget:
            self.loading_widget.hide()
        if self.results_widget:
            self.results_widget.hide()
        if self.oyvey_widget:
            self.oyvey_widget.hide()
        
        # Show date range screen
        self.date_range_widget.show()
    
    def show_loading_screen(self):
        """Show the loading screen with the Israeli flag animation"""
        # Initialize if not already
        if not self.loading_widget:
            self.init_loading_screen()
        
        # Hide all screens
        self.start_widget.hide()
        self.date_range_widget.hide()
        if self.results_widget:
            self.results_widget.hide()
        if self.oyvey_widget:
            self.oyvey_widget.hide()
        
        # Show loading screen
        self.loading_widget.show()
        
        # Start flag animation
        if hasattr(self, 'flag_movie') and self.flag_movie:
            self.flag_movie.start()
    
    def show_results_screen(self):
        """Show the results screen with the Mazel Tov animation"""
        # Initialize if not already
        if not self.results_widget:
            self.init_results_screen()
        
        # Hide all screens
        self.start_widget.hide()
        self.date_range_widget.hide()
        self.loading_widget.hide()
        if self.oyvey_widget:
            self.oyvey_widget.hide()
        
        # Hide the view results button initially (will show after animation)
        self.view_results_button.hide()
        
        # Show results screen
        self.results_widget.show()
        
        # Start Mazel Tov animation
        if hasattr(self, 'mazel_tov_movie') and self.mazel_tov_movie:
            # Set animation to play 3 loops
            self.mazel_tov_movie.setLoopCount(3)
            self.mazel_tov_movie.start()
            
            # Connect the finished signal to show the View Results button
            self.mazel_tov_movie.finished.connect(self.show_view_results_button)
    
    def show_oyvey_screen(self):
        """Show the 'Oy Vey' screen when no results are found"""
        # Initialize if not already
        if not self.oyvey_widget:
            self.init_oyvey_screen()
        
        # Hide all screens
        self.start_widget.hide()
        self.date_range_widget.hide()
        self.loading_widget.hide()
        if self.results_widget:
            self.results_widget.hide()
        
        # Show oy vey screen
        self.oyvey_widget.show()
        
        # Start animation if available
        if hasattr(self, 'oyvey_movie') and self.oyvey_movie:
            self.oyvey_movie.start()
    
    # Action Methods
    def start_data_fetch(self):
        """Start the data fetching process"""
        # Show loading screen
        self.show_loading_screen()
        
        # Start the worker thread to fetch data
        self.worker = WorkerThread(self.selected_date_range)
        self.worker.finished.connect(self.handle_fetch_completed)
        self.worker.start()
    
    def handle_fetch_completed(self, results_found):
        """Handle the completion of data fetching"""
        if results_found:
            # Show the success screen with Mazel Tov animation
            self.show_results_screen()
        else:
            # Show the Oy Vey screen
            self.show_oyvey_screen()
    
    def show_view_results_button(self):
        """Show the View Results button after the Mazel Tov animation completes"""
        self.view_results_button.show()
    
    def view_results(self):
        """Handle the View Results button click"""
        # This is a placeholder - when you reconnect the excel_generator component,
        # you'll want to open the Excel file here
        print("View Results clicked - would open Excel file")
        
        # For now, we'll just go back to the start screen
        QTimer.singleShot(500, self.show_start_screen)


def main():
    app = QApplication(sys.argv)
    window = Mr4InARowApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
