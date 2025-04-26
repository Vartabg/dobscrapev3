# gui.py

import os
import sys
import subprocess
import pandas as pd
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QMovie, QKeySequence, QShortcut, QFont, QFontDatabase, QColor, QPalette, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QHBoxLayout, QGridLayout, QGraphicsDropShadowEffect
)

# Import scraper
from scraper_async import scrape_violations
from excel_generator import generate_excel

# Utility
def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller compatibility"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class HebrewStyleButton(QPushButton):
    """Custom button with Jewish styling"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.primary_color = "#0038b8"  # Israeli blue
        self.hover_color = "#1a4fc8"
        self.pressed_color = "#002a8c"
        self.text_color = "white"
        
        # Default state
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.primary_color};
                color: {self.text_color};
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 8px 16px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
                border-left: 4px solid #ffdb58; /* Gold accent on hover */
                border-right: 4px solid #ffdb58;
            }}
            QPushButton:pressed {{
                background-color: {self.pressed_color};
                padding-left: 10px;
                padding-top: 10px;
            }}
        """)
        
        # Add drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(3, 3)
        self.setGraphicsEffect(shadow)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Add Star of David accent (subtle)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw small Star of David in top right corner
        star_size = min(self.width(), self.height()) * 0.15
        margin = 5
        
        # Create Star of David using lines
        painter.setPen(QColor(255, 255, 255, 70))  # Semi-transparent white
        
        # Triangle facing up
        x1 = self.width() - margin - star_size
        y1 = margin + star_size
        x2 = self.width() - margin - star_size/2
        y2 = margin
        x3 = self.width() - margin
        y3 = margin + star_size
        
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        painter.drawLine(int(x2), int(y2), int(x3), int(y3))
        painter.drawLine(int(x3), int(y3), int(x1), int(y1))
        
        # Triangle facing down
        x4 = self.width() - margin - star_size
        y4 = margin
        x5 = self.width() - margin - star_size/2
        y5 = margin + star_size
        x6 = self.width() - margin
        y6 = margin
        
        painter.drawLine(int(x4), int(y4), int(x5), int(y5))
        painter.drawLine(int(x5), int(y5), int(x6), int(y6))
        painter.drawLine(int(x6), int(y6), int(x4), int(y4))

class DOBScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOB Violations Scraper")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: white;")

        self.start_date = "2015-01-01"
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.setup_shortcuts()
        self.output_file_path = os.path.abspath("violations.xlsx")

        # Color scheme
        self.primary_color = "#0038b8"  # Israeli blue
        self.hover_color = "#1a4fc8"
        self.pressed_color = "#002a8c"
        self.text_color = "white"
        
        # Load Hebrew-inspired font
        self.setup_fonts()

        self.start_screen()
        self.stack.setCurrentIndex(0)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Esc"), self, self.close)
    
    def setup_fonts(self):
        """Set up Hebrew-inspired fonts"""
        # Try to load Jewish font
        font_path = resource_path("assets/fonts/jewish.ttf")
        self.hebrew_font_family = "Arial"  # Default fallback
        
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                family = QFontDatabase.applicationFontFamilies(font_id)
                if family:
                    self.hebrew_font_family = family[0]
                    print(f"Loaded Hebrew font: {self.hebrew_font_family}")
        
        # Set font sizes
        self.title_font = QFont(self.hebrew_font_family, 24, QFont.Weight.Bold)
        self.subtitle_font = QFont(self.hebrew_font_family, 16)
        self.button_font = QFont(self.hebrew_font_family, 12, QFont.Weight.Bold)
        self.small_font = QFont(self.hebrew_font_family, 10)

    def create_styled_button(self, text, width=200, height=50, connect_to=None):
        """Create a custom Hebrew-styled button"""
        button = HebrewStyleButton(text)
        button.setFixedSize(width, height)
        button.setFont(self.button_font)
        
        # Connect signal if provided
        if connect_to:
            button.clicked.connect(connect_to)
            
        return button

    # Safe QMovie loader
    def _create_safe_qmovie(self, asset_path, target_label, fallback_text, scaled_size=None):
        """
        Safely creates and assigns a QMovie to a QLabel, checking for file
        existence and movie validity. Sets fallback text on the label if the
        asset is missing or invalid.
        """
        movie = None
        is_valid = False

        # Default label alignment and font for fallback
        target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if os.path.exists(asset_path):
            try:
                movie = QMovie(asset_path)
                if movie.isValid():
                    if scaled_size:
                        movie.setScaledSize(scaled_size)
                    target_label.setMovie(movie)
                    is_valid = True
                else:
                    error_msg = f"{fallback_text}\n(Error: Invalid GIF format)"
                    target_label.setText(error_msg)
                    print(f"Error: QMovie invalid for existing file: '{asset_path}'. Check format/corruption.")
                    movie = None
                    is_valid = False
            except Exception as e:
                error_msg = f"{fallback_text}\n(Error: {e})"
                target_label.setText(error_msg)
                print(f"Error creating QMovie for '{asset_path}': {e}")
                movie = None
                is_valid = False
        else:
            target_label.setText(fallback_text)
            print(f"Warning: Asset not found at '{asset_path}'. Displaying fallback text.")
            movie = None
            is_valid = False

        return movie, is_valid

    def start_screen(self):
        """First screen with Start button"""
        start_screen = QWidget()
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("DOB Violations Scraper")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet("color: #0038b8;")  # Israeli blue
        
        # Subtitle
        subtitle_label = QLabel("Building Violation Reports")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(self.subtitle_font)

        # Start button with Jewish style
        start_button = self.create_styled_button("Start", 200, 60, self.show_category_screen)

        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(subtitle_label)
        layout.addSpacing(40)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        start_screen.setLayout(layout)
        self.stack.addWidget(start_screen)

    def show_category_screen(self):
        """Show the accordion menu"""
        self.category_screen = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Select Category")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet("color: #0038b8;")  # Israeli blue
        
        layout.addWidget(title_label)
        layout.addSpacing(30)

        # Category buttons
        recent_button = self.create_styled_button("Recent Periods", 250, 60, self.show_recent_periods)
        years_button = self.create_styled_button("Past Years", 250, 60, self.show_past_years)
        all_button = self.create_styled_button("All Since 2015", 250, 60, 
                                              lambda: self.begin_scraping("2015-01-01"))

        layout.addWidget(recent_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(years_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(all_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        
        # Back button
        back_button = self.create_styled_button("Back", 120, 40, lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.category_screen.setLayout(layout)
        self.stack.addWidget(self.category_screen)
        self.stack.setCurrentWidget(self.category_screen)

    def show_recent_periods(self):
        """Show Recent Periods selection"""
        self.show_period_buttons([
            ("Today", 0),
            ("1 Week", 7),
            ("2 Weeks", 14),
            ("1 Month", 30),
            ("3 Months", 90),
            ("6 Months", 180),
        ], "Recent Periods")

    def show_past_years(self):
        """Show Past Years selection"""
        self.show_period_buttons([
            ("1 Year", 365),
            ("2 Years", 730),
            ("3 Years", 1095),
            ("4 Years", 1460),
            ("5 Years", 1825),
            ("6 Years", 2190),
            ("7 Years", 2555),
            ("8 Years", 2920),
            ("9 Years", 3285),
        ], "Past Years")

    def show_period_buttons(self, options, title_text):
        """Generate dynamic period buttons in a grid layout"""
        self.period_screen = QWidget()
        main_layout = QVBoxLayout()
        
        # Header
        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet("color: #0038b8;")  # Israeli blue
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)
        
        # Grid layout for buttons - 3 columns
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # Add buttons to grid
        for i, (label, days) in enumerate(options):
            # Create button with Jewish style
            button = self.create_styled_button(label, 180, 50)
            # Use lambda to capture specific days value
            button.clicked.connect(lambda checked, d=days: self.calculate_start_date(d))
            row, col = divmod(i, 3)  # 3 columns
            grid_layout.addWidget(button, row, col)
        
        # Back button
        back_button = self.create_styled_button("Back", 120, 40, self.show_category_screen)
        
        # Add grid to main layout
        main_layout.addLayout(grid_layout)
        main_layout.addSpacing(30)
        main_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.period_screen.setLayout(main_layout)
        self.stack.addWidget(self.period_screen)
        self.stack.setCurrentWidget(self.period_screen)

    def calculate_start_date(self, days_back):
        today = datetime.today()
        new_start = today - timedelta(days=days_back)
        # Enforce minimum date of Jan 1, 2015
        if new_start < datetime(2015, 1, 1):
            new_start = datetime(2015, 1, 1)
        self.begin_scraping(new_start.strftime("%Y-%m-%d"))

    def begin_scraping(self, start_date):
        self.start_date = start_date
        self.show_loading_screen()

    def show_loading_screen(self):
        """Show Israeli flag while scraping"""
        loading_screen = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Processing Request")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet("color: #0038b8;")  # Israeli blue
        
        # Subtitle with date
        subtitle_label = QLabel(f"Searching for violations since {self.start_date}")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(self.subtitle_font)

        self.flag_label = QLabel()
        self.flag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flag_path = resource_path("assets/flag.gif")
        
        # Use safe QMovie loader
        self.flag_movie, is_flag_valid = self._create_safe_qmovie(
            flag_path,
            self.flag_label,
            "Processing..."
        )
        
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(subtitle_label)
        layout.addSpacing(30)
        layout.addWidget(self.flag_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        loading_screen.setLayout(layout)
        self.stack.addWidget(loading_screen)
        self.stack.setCurrentWidget(loading_screen)
        
        # Start the movie if valid
        if is_flag_valid:
            self.flag_movie.start()

        # Start scraping after short delay
        QTimer.singleShot(500, self.scrape_violations)

    def scrape_violations(self):
        try:
            result = scrape_violations(start_date=self.start_date)
            self.handle_scrape_result(result)
        except Exception as e:
            print(f"Error during scraping: {e}")
            self.handle_scrape_result(pd.DataFrame())  # Empty DataFrame for failure

    def handle_scrape_result(self, result):
        if result.empty:
            self.show_failure_screen()
        else:
            try:
                generate_excel(result)
                self.show_success_screen()
            except Exception as e:
                print(f"Error generating Excel: {e}")
                self.show_failure_screen()

    def show_success_screen(self):
        """Show Mazel Tov after success"""
        success_screen = QWidget()
        layout = QVBoxLayout()

        self.success_label = QLabel()
        self.success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gif_path = resource_path("assets/mazeltov.gif")

        # Use safe QMovie loader
        self.success_movie, is_success_valid = self._create_safe_qmovie(
            gif_path,
            self.success_label,
            "Mazel Tov!"
        )

        layout.addStretch()
        layout.addWidget(self.success_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        success_screen.setLayout(layout)
        self.stack.addWidget(success_screen)
        self.stack.setCurrentWidget(success_screen)

        # After 1 playthrough, show final success screen
        if is_success_valid:
            self.success_movie.start()
            self.success_movie.frameChanged.connect(self.check_success_complete)
        else:
            # If GIF is missing or invalid, show final success screen after a delay
            QTimer.singleShot(1000, self.show_final_success_screen)

    def check_success_complete(self):
        if self.success_movie.currentFrameNumber() == self.success_movie.frameCount() - 1:
            self.success_movie.stop()
            self.show_final_success_screen()

    def show_final_success_screen(self):
        """Show final success screen with Hebrew styling"""
        screen = QWidget()
        layout = QVBoxLayout()
        
        # Title using Hebrew font
        title_label = QLabel("Mazel Tov!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet("color: #0038b8;")  # Israeli blue
        
        # Subtitle
        subtitle_label = QLabel("Violation report generated successfully")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(self.subtitle_font)
        
        # File info in clean, minimal style
        file_info = QLabel(f"Location: {self.output_file_path}")
        file_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_info.setFont(QFont("Arial", 12))
        file_info.setWordWrap(True)
        
        # Hebrew styled buttons
        view_button = self.create_styled_button("View Report", 200, 50, self.view_excel)
        home_button = self.create_styled_button("Return Home", 180, 50, self.restart_app)
        exit_button = self.create_styled_button("Exit", 180, 50, self.close)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(home_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(exit_button)
        
        # Main layout with elegant spacing
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(20)
        layout.addWidget(subtitle_label)
        layout.addSpacing(20)
        layout.addWidget(file_info)
        layout.addSpacing(40)
        layout.addWidget(view_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        screen.setLayout(layout)
        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)

    def show_failure_screen(self):
        """Show Oy Vey after failure"""
        fail_screen = QWidget()
        layout = QVBoxLayout()

        self.fail_label = QLabel()
        self.fail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gif_path = resource_path("assets/oyvey.gif")

        # Use safe QMovie loader
        self.fail_movie, is_fail_valid = self._create_safe_qmovie(
            gif_path,
            self.fail_label,
            "Oy Vey!"
        )

        layout.addStretch()
        layout.addWidget(self.fail_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        fail_screen.setLayout(layout)
        self.stack.addWidget(fail_screen)
        self.stack.setCurrentWidget(fail_screen)

        # After 1 playthrough, show final failure screen
        if is_fail_valid:
            self.fail_movie.start()
            self.fail_movie.frameChanged.connect(self.check_failure_complete)
        else:
            # If GIF is missing or invalid, show final failure screen after a delay
            QTimer.singleShot(1000, self.show_final_failure_screen)

    def check_failure_complete(self):
        if self.fail_movie.currentFrameNumber() == self.fail_movie.frameCount() - 1:
            self.fail_movie.stop()
            self.show_final_failure_screen()

    def show_final_failure_screen(self):
        """Show final failure screen with Hebrew styling"""
        screen = QWidget()
        layout = QVBoxLayout()
        
        # Title using Hebrew font
        title_label = QLabel("Oy Vey!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet("color: #0038b8;")  # Israeli blue
        
        # Subtitle
        subtitle_label = QLabel("No building violations were found for the selected dates")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(self.subtitle_font)
        subtitle_label.setWordWrap(True)
        
        # Hebrew styled buttons
        home_button = self.create_styled_button("Try Again", 180, 50, self.restart_app)
        exit_button = self.create_styled_button("Exit", 180, 50, self.close)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(home_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(exit_button)
        
        # Main layout with elegant spacing
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(20)
        layout.addWidget(subtitle_label)
        layout.addSpacing(40)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        screen.setLayout(layout)
        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)

    def restart_app(self):
        self.stack.setCurrentIndex(0)

    def view_excel(self):
        """Open the generated Excel file"""
        if os.path.exists(self.output_file_path):
            try:
                if sys.platform == "win32":
                    os.startfile(self.output_file_path)
                elif sys.platform == "darwin":  # macOS
                    subprocess.Popen(["open", self.output_file_path])
                else:  # Linux
                    subprocess.Popen(["xdg-open", self.output_file_path])
                print(f"Opening Excel file at: {self.output_file_path}")
            except Exception as e:
                print(f"Failed to open Excel file: {e}")
        else:
            print(f"Excel file not found at: {self.output_file_path}")

# Main Execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DOBScraperGUI()
    window.show()
    sys.exit(app.exec())