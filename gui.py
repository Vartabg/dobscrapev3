import sys
import asyncio
import os
import datetime
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QMainWindow, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QMovie, QFont
import scraper_async
import excel_generator

class DOBViolationsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOB Violations Scraper")
        self.setFixedSize(800, 600)
        
        # Create central widget - CRITICAL for QMainWindow
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout for central widget
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Initialize UI
        self.init_ui()

    def init_ui(self):
        """Initialize the starting UI with the circular start button"""
        self.clear_layout()
        
        # Create start button
        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(200, 200)
        self.start_button.setStyleSheet("""
            QPushButton {
                border-radius: 100px; 
                background-color: white; 
                font-size: 24px;
                border: 2px solid #3498db;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.start_button.clicked.connect(self.show_date_options)
        
        # Add to layout with proper alignment
        button_container = QFrame()
        button_layout = QVBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(self.start_button)
        
        self.main_layout.addWidget(button_container)

    def show_date_options(self):
        """Show date range selection buttons"""
        self.clear_layout()
        
        # Create container for buttons
        date_frame = QFrame()
        date_layout = QVBoxLayout(date_frame)
        date_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_layout.setSpacing(15)  # Add space between buttons
        
        # Create date range buttons
        self.date_options = {
            "Last 30 Days": 30,
            "Last 3 Months": 90,
            "Last 6 Months": 180,
            "Past Year": 365,
            "Past 2 Years": 730,
            "All Since 2020": None
        }
        
        for label, days in self.date_options.items():
            btn = QPushButton(label)
            btn.setFixedSize(300, 50)
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 25px; 
                    font-size: 18px;
                    background-color: white;
                    border: 2px solid #3498db;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
            # Important: Use lambda with default argument to capture current value
            btn.clicked.connect(lambda checked=False, d=days: self.start_scraping(d))
            date_layout.addWidget(btn)
        
        self.main_layout.addWidget(date_frame)

    def start_scraping(self, days):
        """Start the scraping process with animation"""
        self.clear_layout()
        
        # Create container for flag animation
        flag_container = QFrame()
        flag_layout = QVBoxLayout(flag_container)
        flag_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add flag animation
        self.flag_label = QLabel()
        self.flag_movie = QMovie("assets/israel_flag.gif")
        self.flag_label.setMovie(self.flag_movie)
        self.flag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flag_layout.addWidget(self.flag_label)
        
        self.main_layout.addWidget(flag_container)
        self.flag_movie.start()
        
        # Calculate start date for filtering
        start_date = None
        if days:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Run scraper asynchronously
        QTimer.singleShot(100, lambda: self._run_scraper_async(start_date))

    def _run_scraper_async(self, start_date):
        """Helper to run the async scraper from a non-async context"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            violations = loop.run_until_complete(scraper_async.fetch_violations(start_date))
            if not violations:
                self.show_no_results()
            else:
                excel_generator.generate_excel(violations)
                self.show_mazel_tov()
        finally:
            loop.close()

    def show_mazel_tov(self):
        """Show Mazel Tov animation after successful scraping"""
        self.clear_layout()
        
        # Create container for mazel tov animation
        mazel_container = QFrame()
        mazel_layout = QVBoxLayout(mazel_container)
        mazel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add mazel tov animation
        self.mazel_label = QLabel()
        self.mazel_movie = QMovie("assets/mazel_tov.gif")
        
        # Set appropriate size for the movie
        self.mazel_movie.setScaledSize(QSize(600, 400))
        
        self.mazel_label.setMovie(self.mazel_movie)
        self.mazel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mazel_layout.addWidget(self.mazel_label)
        
        self.main_layout.addWidget(mazel_container)
        self.mazel_movie.start()
        
        # Show view results button after animation plays 3 times
        # Calculate approximate duration for 3 loops
        single_duration = self.mazel_movie.duration()
        if single_duration <= 0:  # If duration cannot be determined
            single_duration = 3000  # Default to 3 seconds
            
        QTimer.singleShot(single_duration * 3, self.show_view_results)

    def show_view_results(self):
        """Show the View Results button after animation finishes"""
        self.clear_layout()
        
        # Create container for view results button
        results_container = QFrame()
        results_layout = QVBoxLayout(results_container)
        results_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add view results button
        view_button = QPushButton("View Results")
        view_button.setFixedSize(200, 200)
        view_button.setStyleSheet("""
            QPushButton {
                border-radius: 100px; 
                background-color: green; 
                color: white; 
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        view_button.clicked.connect(self.open_results)
        results_layout.addWidget(view_button)
        
        self.main_layout.addWidget(results_container)

    def open_results(self):
        """Open the Excel results file and close the application"""
        filepath = os.path.abspath("violations.xlsx")
        webbrowser.open(filepath)
        self.close()

    def show_no_results(self):
        """Show the no results message and animation"""
        self.clear_layout()
        
        # Create container for no results content
        no_results_container = QFrame()
        no_results_layout = QVBoxLayout(no_results_container)
        no_results_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add oy vey animation
        oyvey_label = QLabel()
        oyvey_movie = QMovie("assets/oyvey.gif")
        oyvey_movie.setScaledSize(QSize(400, 300))
        oyvey_label.setMovie(oyvey_movie)
        oyvey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_results_layout.addWidget(oyvey_label)
        
        # Add no results message
        message_label = QLabel("sorry, no results found. please try a different time period or fuck off.")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFont(QFont("Times New Roman", 16))
        message_label.setStyleSheet("margin: 20px;")
        no_results_layout.addWidget(message_label)
        
        self.main_layout.addWidget(no_results_container)
        
        # Start animation
        oyvey_movie.start()
        
        # Show home and close buttons after animation plays twice
        single_duration = oyvey_movie.duration()
        if single_duration <= 0:  # If duration cannot be determined
            single_duration = 3000  # Default to 3 seconds
            
        QTimer.singleShot(single_duration * 2, self.show_home_and_close_buttons)

    def show_home_and_close_buttons(self):
        """Show home and close buttons after no results animation"""
        self.clear_layout()
        
        # Create container for buttons
        buttons_container = QFrame()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add message (keeping the previous message)
        message_label = QLabel("sorry, no results found. please try a different time period or fuck off.")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFont(QFont("Times New Roman", 16))
        message_label.setStyleSheet("margin-bottom: 30px;")
        buttons_layout.addWidget(message_label)
        
        # Create horizontal layout for buttons
        button_row = QHBoxLayout()
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_row.setSpacing(30)  # Add space between buttons
        
        # Add home button
        home_btn = QPushButton("🏠")
        home_btn.setFixedSize(100, 100)
        home_btn.setStyleSheet("""
            QPushButton {
                border-radius: 50px; 
                font-size: 32px;
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        home_btn.clicked.connect(self.init_ui)
        button_row.addWidget(home_btn)
        
        # Add close button
        close_btn = QPushButton("❌")
        close_btn.setFixedSize(100, 100)
        close_btn.setStyleSheet("""
            QPushButton {
                border-radius: 50px; 
                font-size: 32px;
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_btn.clicked.connect(self.close)
        button_row.addWidget(close_btn)
        
        buttons_layout.addLayout(button_row)
        self.main_layout.addWidget(buttons_container)

    def clear_layout(self):
        """Clear all widgets from the main layout"""
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                # If the item is a layout, clear it recursively
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DOBViolationsApp()
    window.show()
    sys.exit(app.exec())
