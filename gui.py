# FINAL PATCHED VERSION — Start button visibility fix applied
import sys
import asyncio
import os
import datetime
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QMainWindow, QFrame, QSpacerItem, QSizePolicy, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QMovie, QFont, QColor
import scraper_async
import excel_generator

# Israeli flag colors
ISRAEL_BLUE = "#002B7F"  # Deep blue from Israeli flag
ISRAEL_WHITE = "#FFFFFF"  # Pure white
ISRAEL_GREEN = "#2ECC71"  # Green that harmonizes with flag

class DOBViolationsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOB Violations Scraper")
        self.setFixedSize(800, 600)
        self.setStyleSheet(f"background-color: {ISRAEL_WHITE};")
        
        # Create central widget - CRITICAL for QMainWindow
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet(f"background-color: {ISRAEL_WHITE};")
        self.setCentralWidget(self.central_widget)
        
        # Create main layout for central widget
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for cleaner look
        
        # Initialize UI
        self.init_ui()

    def init_ui(self):
        """Initialize the starting UI with the circular start button"""
        self.clear_layout()
        
        # Create start button
        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(200, 200)
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                border-radius: 100px; 
                background-color: {ISRAEL_WHITE}; 
                color: {ISRAEL_BLUE};
                font-size: 24pt;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #F8F8F8;  /* Very subtle hover effect */
            }}
        """)
        self.start_button.clicked.connect(self.show_date_options)
        
        # Create container with vertical centering
        container = QWidget()
        container.setStyleSheet(f"background-color: {ISRAEL_WHITE};")
        container_layout = QVBoxLayout(container)
        
        # Add spacers for vertical centering
        container_layout.addStretch()
        container_layout.addWidget(self.start_button, 0, Qt.AlignmentFlag.AlignCenter)
        container_layout.addStretch()
        
        self.main_layout.addWidget(container)
        
        # Add fade-in effect for start button
        self.fade_in_widget(self.start_button)

    def show_date_options(self):
        """Show date range selection buttons"""
        self.clear_layout()
        
        # Create container for date range buttons
        date_container = QWidget()
        date_container.setStyleSheet(f"background-color: {ISRAEL_WHITE};")
        date_layout = QVBoxLayout(date_container)
        date_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_layout.setSpacing(15)  # 15px spacing between buttons
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create date range buttons
        self.date_options = {
            "Last 30 Days": 30,
            "Last 3 Months": 90,
            "Last 6 Months": 180,
            "Past Year": 365,
            "Past 2 Years": 730,
            "All Since 2020": None
        }
        
        # Add spacer for vertical centering
        date_layout.addStretch()
        
        # Create buttons with staggered fade-in
        buttons = []
        for label, days in self.date_options.items():
            btn = QPushButton(label)
            btn.setFixedSize(300, 50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border-radius: 25px; 
                    background-color: {ISRAEL_WHITE};
                    color: black;
                    font-size: 18pt;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: #F8F8F8;  /* Very subtle hover effect */
                }}
            """)
            btn.clicked.connect(lambda checked=False, d=days: self.start_scraping(d))
            date_layout.addWidget(btn)
            
            # Make button initially transparent
            opacity_effect = QGraphicsOpacityEffect()
            opacity_effect.setOpacity(0)
            btn.setGraphicsEffect(opacity_effect)
            buttons.append(btn)
        
        # Add spacer for vertical centering
        date_layout.addStretch()
        
        # Add to main layout
        self.main_layout.addWidget(date_container)
        
        # Fade in buttons with sequence
        for i, btn in enumerate(buttons):
            QTimer.singleShot(100 * i, lambda b=btn: self.fade_in_widget(b))

    def start_scraping(self, days):
        """Start the scraping process with animation"""
        self.clear_layout()
        
        # Create container for flag animation with proper centering
        flag_container = QWidget()
        flag_container.setStyleSheet(f"background-color: {ISRAEL_WHITE};")
        flag_layout = QVBoxLayout(flag_container)
        flag_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flag_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add spacer for vertical centering
        flag_layout.addStretch()
        
        # Add flag animation
        self.flag_label = QLabel()
        self.flag_movie = QMovie("assets/israel_flag.gif")
        
        # Set appropriate size for the movie (max width 600px)
        self.flag_movie.setScaledSize(QSize(600, 400))
        
        self.flag_label.setMovie(self.flag_movie)
        self.flag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flag_layout.addWidget(self.flag_label)
        
        # Add spacer for vertical centering
        flag_layout.addStretch()
        
        self.main_layout.addWidget(flag_container)
        
        # Add fade-in effect
        self.fade_in_widget(self.flag_label)
        
        # Start animation after fade-in
        QTimer.singleShot(300, lambda: self.flag_movie.start())
        
        # Calculate start date for filtering
        start_date = None
        if days:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Run scraper asynchronously
        QTimer.singleShot(500, lambda: self._run_scraper_async(start_date))

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
        except Exception as e:
            print(f"Error during API call: {e}")
            # Show fallback for any errors
            self.show_no_results()
        finally:
            loop.close()

    def show_mazel_tov(self):
        """Show Mazel Tov animation after successful scraping"""
        self.clear_layout()
        
        # Create container for mazel tov animation
        mazel_container = QWidget()
        mazel_container.setStyleSheet(f"background-color: {ISRAEL_WHITE};")
        mazel_layout = QVBoxLayout(mazel_container)
        mazel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mazel_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add spacer for vertical centering
        mazel_layout.addStretch()
        
        # Add mazel tov animation
        self.mazel_label = QLabel()
        self.mazel_movie = QMovie("assets/mazel_tov.gif")
        
        # Set appropriate size for the movie (600x400)
        self.mazel_movie.setScaledSize(QSize(600, 400))
        
        self.mazel_label.setMovie(self.mazel_movie)
        self.mazel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mazel_layout.addWidget(self.mazel_label)
        
        # Add spacer for vertical centering
        mazel_layout.addStretch()
        
        self.main_layout.addWidget(mazel_container)
        
        # Add fade-in effect
        self.fade_in_widget(self.mazel_label)
        
        # Start animation after fade-in
        QTimer.singleShot(300, lambda: self.mazel_movie.start())
        
        # Show view results button after a fixed duration (approximately 3 loops)
        # Using fixed time instead of movie.duration() which is not available
        QTimer.singleShot(9000, self.show_view_results)  # 3 seconds per loop * 3 loops

    def show_view_results(self):
        """Show the View Results button after animation finishes"""
        self.clear_layout()
        
        # Create container for view results button with vertical centering
        results_container = QWidget()
        results_container.setStyleSheet(f"background-color: {ISRAEL_WHITE};")
        results_layout = QVBoxLayout(results_container)
        results_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add spacer for vertical centering
        results_layout.addStretch()
        
        # Add view results button using the green color that matches Israeli flag
        view_button = QPushButton("View Results")
        view_button.setFixedSize(200, 200)
        view_button.setStyleSheet(f"""
            QPushButton {{
                border-radius: 100px; 
                background-color: {ISRAEL_GREEN}; 
                color: white; 
                font-size: 24pt;
                border: none;
            }}
        """)
        view_button.clicked.connect(self.open_results)
        results_layout.addWidget(view_button)
        
        # Add spacer for vertical centering
        results_layout.addStretch()
        
        self.main_layout.addWidget(results_container)
        
        # Add fade-in effect
        self.fade_in_widget(view_button)

    def open_results(self):
        """Open the Excel results file and close the application"""
        filepath = os.path.abspath("violations.xlsx")
        webbrowser.open(filepath)
        
        # Add slight delay before closing to ensure Excel opens
        QTimer.singleShot(1000, self.close)

    def show_no_results(self):
        """Show the no results message and animation"""
        self.clear_layout()
        
        # Create container for no results content
        no_results_container = QWidget()
        no_results_container.setStyleSheet(f"background-color: {ISRAEL_WHITE};")
        no_results_layout = QVBoxLayout(no_results_container)
        no_results_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_results_layout.setContentsMargins(50, 0, 50, 0)  # Add horizontal padding
        
        # Add spacer for vertical centering
        no_results_layout.addStretch()
        
        # Add oy vey animation
        oyvey_label = QLabel()
        oyvey_movie = QMovie("assets/oyvey.gif")
        oyvey_movie.setScaledSize(QSize(400, 300))
        oyvey_label.setMovie(oyvey_movie)
        oyvey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_results_layout.addWidget(oyvey_label)
        
        # Add no results message with Jewish-flavored tone
        message_label = QLabel("sorry, no results found. please try a different time period or fuck off.")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFont(QFont("Times New Roman", 16))
        message_label.setStyleSheet("margin: 20px 0;")  # Add vertical margin
        no_results_layout.addWidget(message_label)
        
        # Add spacer for vertical centering
        no_results_layout.addStretch()
        
        self.main_layout.addWidget(no_results_container)
        
        # Add fade-in effect
        self.fade_in_widget(oyvey_label)
        self.fade_in_widget(message_label)
        
        # Start animation after fade-in
        QTimer.singleShot(300, lambda: oyvey_movie.start())
        
        # Show home and close buttons after fixed duration (approximately 2 loops)
        # Using fixed time instead of movie.duration() which is not available
        QTimer.singleShot(6000, self.show_home_and_close_buttons)  # 3 seconds per loop * 2 loops

    def show_home_and_close_buttons(self):
        """Show home and close buttons after no results animation"""
        self.clear_layout()
        
        # Create container for buttons
        buttons_container = QWidget()
        buttons_container.setStyleSheet(f"background-color: {ISRAEL_WHITE};")
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons_layout.setContentsMargins(50, 0, 50, 0)  # Add horizontal padding
        
        # Add spacer for vertical centering
        buttons_layout.addStretch()
        
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
        button_row.setSpacing(30)  # 30px space between buttons
        
        # Add home button (blue of Israeli flag)
        home_btn = QPushButton("🏠")
        home_btn.setFixedSize(100, 100)
        home_btn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 50px; 
                font-size: 32px;
                background-color: {ISRAEL_BLUE};
                color: white;
                border: none;
            }}
        """)
        home_btn.clicked.connect(self.init_ui)
        button_row.addWidget(home_btn)
        
        # Add close button (red for contrast but harmonizing)
        close_btn = QPushButton("❌")
        close_btn.setFixedSize(100, 100)
        close_btn.setStyleSheet("""
            QPushButton {
                border-radius: 50px; 
                font-size: 32px;
                background-color: #e74c3c;
                color: white;
                border: none;
            }
        """)
        close_btn.clicked.connect(self.close)
        button_row.addWidget(close_btn)
        
        buttons_layout.addLayout(button_row)
        
        # Add spacer for vertical centering
        buttons_layout.addStretch()
        
        self.main_layout.addWidget(buttons_container)
        
        # Add fade-in effects
        self.fade_in_widget(message_label)
        
        # Staggered fade-in for buttons
        QTimer.singleShot(200, lambda: self.fade_in_widget(home_btn))
        QTimer.singleShot(400, lambda: self.fade_in_widget(close_btn))

    def fade_in_widget(self, widget, duration=300):
        """Create a fade-in animation for a widget"""
        # Create opacity effect
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0)
        
        # Create animation
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()

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
