# gui.py

import os
import sys
import subprocess
import pandas as pd
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMovie, QKeySequence, QShortcut, QFont, QFontDatabase
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QHBoxLayout, QGridLayout
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

class DOBScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mr. 4 in a Row")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: white;")

        self.start_date = "2015-01-01"
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.setup_shortcuts()
        self.output_file_path = os.path.abspath("violations.xlsx")

        self.start_screen()
        self.stack.setCurrentIndex(0)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Esc"), self, self.close)

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

        # Jewish font if available
        font_path = resource_path("assets/fonts/jewish.ttf")
        custom_font = QFont("Arial", 18)
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                family = QFontDatabase.applicationFontFamilies(font_id)
                if family:
                    custom_font = QFont(family[0], 18)

        # Title
        title_label = QLabel("Mr. 4 in a Row")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont(custom_font.family(), 24, QFont.Weight.Bold))
        
        # Subtitle
        subtitle_label = QLabel("Building Violations Scraper")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont(custom_font.family(), 16))

        start_button = QPushButton("Start")
        start_button.setFixedSize(150, 150)
        start_button.setFont(custom_font)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                font-weight: bold;
                border-radius: 75px;
                border: 1px solid #0038b8;
            }
            QPushButton:hover {
                background-color: #004fd6;
                border: 2px solid #66a3ff;
            }
        """)
        start_button.clicked.connect(self.show_category_screen)

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
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        
        layout.addWidget(title_label)
        layout.addSpacing(30)

        categories = [
            ("Recent Periods", self.show_recent_periods),
            ("Past Years", self.show_past_years),
            ("All Since 2015", lambda: self.begin_scraping("2015-01-01"))
        ]

        for label, func in categories:
            button = QPushButton(label)
            button.setFixedSize(250, 60)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #0038b8;
                    color: white;
                    font-size: 16px;
                    border-radius: 10px;
                    border: 1px solid #0038b8;
                }
                QPushButton:hover {
                    background-color: #004fd6;
                    border: 2px solid #66a3ff;
                }
            """)
            button.clicked.connect(func)
            layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addSpacing(20)
        
        # Back button
        back_button = QPushButton("Back")
        back_button.setFixedSize(100, 40)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                border-radius: 10px;
                border: 1px solid #0038b8;
            }
            QPushButton:hover {
                background-color: #004fd6;
                border: 2px solid #66a3ff;
            }
        """)
        back_button.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        
        layout.addSpacing(20)
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
        layout = QVBoxLayout()
        
        # Header
        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title_label)
        layout.addSpacing(20)
        
        # Grid layout for buttons - 3 columns
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # Add buttons to grid
        for i, (label, days) in enumerate(options):
            button = QPushButton(label)
            button.setFixedSize(120, 120)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #0038b8;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 60px;
                    border: 1px solid #0038b8;
                }
                QPushButton:hover {
                    background-color: #004fd6;
                    border: 2px solid #66a3ff;
                }
            """)
            button.clicked.connect(lambda checked, d=days: self.calculate_start_date(d))
            row, col = divmod(i, 3)  # 3 columns
            grid_layout.addWidget(button, row, col)
        
        # Back button
        back_button = QPushButton("Back")
        back_button.setFixedSize(100, 40)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                border-radius: 10px;
                border: 1px solid #0038b8;
            }
            QPushButton:hover {
                background-color: #004fd6;
                border: 2px solid #66a3ff;
            }
        """)
        back_button.clicked.connect(self.show_category_screen)
        
        # Add grid to main layout
        layout.addLayout(grid_layout)
        layout.addSpacing(20)
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.period_screen.setLayout(layout)
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
        title_label = QLabel("Scraping Building Violations")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        
        # Subtitle with date
        subtitle_label = QLabel(f"Finding violations since {self.start_date}")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 16))

        self.flag_label = QLabel()
        self.flag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flag_path = resource_path("assets/flag.gif")
        
        # Use safe QMovie loader
        self.flag_movie, is_flag_valid = self._create_safe_qmovie(
            flag_path,
            self.flag_label,
            "Loading...\n(Flag GIF Missing)"
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
            "Mazel Tov!\n(Success GIF Missing)"
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
        """Show final success screen with Return Home, View Results and Exit App buttons"""
        screen = QWidget()
        layout = QVBoxLayout()
        
        # Jewish font if available
        font_path = resource_path("assets/fonts/jewish.ttf")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        subtitle_font = QFont("Arial", 16)
        
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                family = QFontDatabase.applicationFontFamilies(font_id)
                if family:
                    title_font = QFont(family[0], 24, QFont.Weight.Bold)
                    subtitle_font = QFont(family[0], 16)
        
        # Title label
        title_label = QLabel("Mazel Tov!")
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle label
        subtitle_label = QLabel("Your violation report has been successfully generated.")
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add file location info
        file_info = QLabel(f"Excel file saved to: {self.output_file_path}")
        file_info.setFont(QFont("Arial", 12))
        file_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_info.setWordWrap(True)
        
        # Button style with fixed hover effect (no box-shadow)
        button_style = """
            QPushButton {
                background-color: #0038b8;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                border: 1px solid #0038b8;
            }
            QPushButton:hover {
                background-color: #004fd6;
                border: 2px solid #66a3ff;
            }
        """
        
        # View Results button
        view_button = QPushButton("🔍 View Excel Results")
        view_button.setFixedSize(200, 50)
        view_button.setStyleSheet(button_style)
        view_button.clicked.connect(self.view_excel)
        
        # Home and Exit buttons
        home_button = QPushButton("🏠 Return Home")
        home_button.setFixedSize(150, 50)
        home_button.setStyleSheet(button_style)
        home_button.clicked.connect(self.restart_app)
        
        exit_button = QPushButton("❌ Exit App")
        exit_button.setFixedSize(150, 50)
        exit_button.setStyleSheet(button_style)
        exit_button.clicked.connect(self.close)
        
        # Button layout for Home/Exit
        button_layout = QHBoxLayout()
        button_layout.addWidget(home_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(exit_button)
        
        # Main layout
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(20)
        layout.addWidget(subtitle_label)
        layout.addSpacing(10)
        layout.addWidget(file_info)
        layout.addSpacing(30)
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
            "Oy Vey!\n(Failure GIF Missing)"
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
        """Show final failure screen with Return Home and Exit App buttons"""
        screen = QWidget()
        layout = QVBoxLayout()
        
        # Jewish font if available
        font_path = resource_path("assets/fonts/jewish.ttf")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        subtitle_font = QFont("Arial", 16)
        
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                family = QFontDatabase.applicationFontFamilies(font_id)
                if family:
                    title_font = QFont(family[0], 24, QFont.Weight.Bold)
                    subtitle_font = QFont(family[0], 16)
        
        # Title label
        title_label = QLabel("Oy Vey!")
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle label
        subtitle_label = QLabel("No building violations were found for the selected dates.")
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Button style with fixed hover effect (no box-shadow)
        button_style = """
            QPushButton {
                background-color: #0038b8;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                border: 1px solid #0038b8;
            }
            QPushButton:hover {
                background-color: #004fd6;
                border: 2px solid #66a3ff;
            }
        """
        
        # Buttons
        home_button = QPushButton("🏠 Return Home")
        home_button.setFixedSize(150, 50)
        home_button.setStyleSheet(button_style)
        home_button.clicked.connect(self.restart_app)
        
        exit_button = QPushButton("❌ Exit App")
        exit_button.setFixedSize(150, 50)
        exit_button.setStyleSheet(button_style)
        exit_button.clicked.connect(self.close)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(home_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(exit_button)
        
        # Main layout
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