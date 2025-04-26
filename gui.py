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
    QStackedWidget, QHBoxLayout
)

# Import scraper
from scraper_async import scrape_violations

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

        self.start_screen()
        self.stack.setCurrentIndex(0)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Esc"), self, self.close)

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

        start_button = QPushButton("Start")
        start_button.setFixedSize(150, 150)
        start_button.setFont(custom_font)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                font-weight: bold;
                border-radius: 75px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        """)
        start_button.clicked.connect(self.show_category_screen)

        layout.addStretch()
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        start_screen.setLayout(layout)
        self.stack.addWidget(start_screen)

    def show_category_screen(self):
        """Show the accordion menu"""
        self.category_screen = QWidget()
        layout = QVBoxLayout()

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
                    font-family: Arial;
                }
                QPushButton:hover {
                    background-color: #004fd6;
                }
            """)
            button.clicked.connect(func)
            layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addSpacing(20)

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
        ])

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
        ])

    def show_period_buttons(self, options):
        """Generate dynamic period buttons"""
        self.period_screen = QWidget()
        layout = QVBoxLayout()

        for label, days in options:
            button = QPushButton(label)
            button.setFixedSize(120, 120)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #0038b8;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 60px;
                    font-family: Arial;
                }
                QPushButton:hover {
                    background-color: #004fd6;
                }
            """)
            button.clicked.connect(lambda checked, d=days: self.calculate_start_date(d))
            layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addSpacing(15)

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

        self.flag_label = QLabel()
        self.flag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flag_path = resource_path("assets/flag.gif")
        if os.path.exists(flag_path):
            self.flag_movie = QMovie(flag_path)
            self.flag_label.setMovie(self.flag_movie)
            self.flag_movie.start()
        else:
            self.flag_label.setText("Loading...")

        layout.addStretch()
        layout.addWidget(self.flag_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        loading_screen.setLayout(layout)
        self.stack.addWidget(loading_screen)
        self.stack.setCurrentWidget(loading_screen)

        # Start scraping after short delay
        QTimer.singleShot(500, self.scrape_violations)

    def scrape_violations(self):
        result = scrape_violations(start_date=self.start_date)
        self.handle_scrape_result(result)

    def handle_scrape_result(self, result):
        if result.empty:
            self.show_failure_screen()
        else:
            from excel_generator import generate_excel
            generate_excel(result)
            self.show_success_screen()

    def show_success_screen(self):
        """Show Mazel Tov after success"""
        success_screen = QWidget()
        layout = QVBoxLayout()

        self.success_label = QLabel()
        self.success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gif_path = resource_path("assets/mazeltov.gif")

        if os.path.exists(gif_path):
            self.success_movie = QMovie(gif_path)
            self.success_label.setMovie(self.success_movie)
            self.success_movie.start()
        else:
            self.success_label.setText("Success!")

        layout.addStretch()
        layout.addWidget(self.success_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        success_screen.setLayout(layout)
        self.stack.addWidget(success_screen)
        self.stack.setCurrentWidget(success_screen)

        # After 3 loops, show "View Results"
        self.success_movie.frameChanged.connect(self.check_success_loops)
        self.success_loops = 0

    def check_success_loops(self):
        if self.success_movie.currentFrameNumber() == self.success_movie.frameCount() - 1:
            self.success_loops += 1
            if self.success_loops >= 3:
                self.success_movie.stop()
                self.show_view_results_button()

    def show_view_results_button(self):
        screen = QWidget()
        layout = QVBoxLayout()

        view_button = QPushButton("View Results")
        view_button.setFixedSize(150, 150)
        view_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 75px;
                font-family: Arial;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        view_button.clicked.connect(self.view_excel)

        layout.addStretch()
        layout.addWidget(view_button, alignment=Qt.AlignmentFlag.AlignCenter)
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

        if os.path.exists(gif_path):
            self.fail_movie = QMovie(gif_path)
            self.fail_label.setMovie(self.fail_movie)
            self.fail_movie.start()
        else:
            self.fail_label.setText("No Results Found.")

        layout.addStretch()
        layout.addWidget(self.fail_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        fail_screen.setLayout(layout)
        self.stack.addWidget(fail_screen)
        self.stack.setCurrentWidget(fail_screen)

        # After 2 loops, show Home/Close
        self.fail_movie.frameChanged.connect(self.check_failure_loops)
        self.fail_loops = 0

    def check_failure_loops(self):
        if self.fail_movie.currentFrameNumber() == self.fail_movie.frameCount() - 1:
            self.fail_loops += 1
            if self.fail_loops >= 2:
                self.fail_movie.stop()
                self.show_error_buttons()

    def show_error_buttons(self):
        screen = QWidget()
        layout = QVBoxLayout()

        home_button = QPushButton("Home")
        home_button.setFixedSize(100, 100)
        home_button.clicked.connect(self.restart_app)

        close_button = QPushButton("Close")
        close_button.setFixedSize(100, 100)
        close_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(home_button)
        button_layout.addWidget(close_button)

        layout.addStretch()
        layout.addLayout(button_layout)
        layout.addStretch()

        screen.setLayout(layout)
        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)

    def restart_app(self):
        self.stack.setCurrentIndex(0)

    def view_excel(self):
        path = os.path.abspath("violations.xlsx")
        if os.path.exists(path):
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                else:
                    subprocess.Popen(["xdg-open", path])
            except Exception as e:
                print(f"Failed to open Excel: {e}")
        self.close()

# Main Execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DOBScraperGUI()
    window.show()
    sys.exit(app.exec())
