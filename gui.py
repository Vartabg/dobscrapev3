import sys
import os
import traceback
import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout
)
from PyQt6.QtGui import QMovie, QCursor, QFont
from PyQt6.QtCore import Qt, QTimer
from scraper_async import scrape_violations
from excel_generator import generate_excel_dashboard

class DOBScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOB Violations Scraper")
        self.setFixedSize(360, 400)
        self.setWindowFlags(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout()
        self.layout.addStretch()  # Add spacing at the top
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(120, 120)
        self.start_button.setStyleSheet(
            "border-radius: 60px; background-color: #1E90FF; color: white; font-size: 16px;"
        )
        start_layout = QHBoxLayout()
        start_layout.addStretch()
        start_layout.addWidget(self.start_button)
        start_layout.addStretch()
        self.layout.addLayout(start_layout)
        self.layout.addStretch()  # Add spacing at the bottom to center

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setFixedWidth(320)
        self.label.setStyleSheet("font-size: 13px; color: #1E90FF;")
        self.label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))

        self.layout.addSpacing(10)
        self.layout.addWidget(self.label)
        self.layout.addSpacing(10)
        self.setLayout(self.layout)

        self.state = "start"
        self.output_file = "violations_dashboard.xlsx"
        self.loop_counter = 0
        self.range_buttons = []
        self.grid_layout = QGridLayout()
        self.extra_buttons = []

        self.start_button.clicked.connect(self.show_date_options)

    def show_date_options(self):
        self.start_button.hide()
        ranges = [
            ("Past Week", 7),
            ("Past 2 Weeks", 14),
            ("Past Month", 30),
            ("Past 3 Months", 90),
            ("Past 6 Months", 180),
            ("All Since 2020", None),
            ("Past Year", 365),
            ("Past 2 Years", 730),
        ]
        row, col = 0, 0
        for label, days in ranges:
            btn = QPushButton(label)
            btn.setFixedSize(160, 40)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet(
                "QPushButton { background-color: #e8f0fe; color: #1E90FF; font-size: 14px; border-radius: 12px; }"
                "QPushButton:hover { background-color: #d0e0ff; font-weight: bold; border: 1px solid #1E90FF; }"
            )
            btn.clicked.connect(lambda _, d=days: self.start_scraping(d))
            self.grid_layout.addWidget(btn, row, col)
            self.range_buttons.append(btn)
            col = (col + 1) % 2
            if col == 0:
                row += 1

        wrapper = QHBoxLayout()
        wrapper.addStretch()
        wrapper.addLayout(self.grid_layout)
        wrapper.addStretch()
        self.layout.insertLayout(1, wrapper)

    def start_scraping(self, days):
        for btn in self.range_buttons:
            btn.hide()

        today = datetime.date.today()
        self.start_date = today - datetime.timedelta(days=days) if days is not None else datetime.date(2020, 1, 1)

        self.loop_counter = 0
        self.movie = QMovie(os.path.join(os.path.dirname(__file__), "flag.gif"))
        self.label.setMovie(self.movie)
        self.movie.start()
        QTimer.singleShot(200, self.fetch_data)
        self.state = "fetching"

    def fetch_data(self):
        try:
            df = scrape_violations(start_date=self.start_date)
            if df.empty:
                self.show_oyvey_screen()
                return
            generate_excel_dashboard(df, self.output_file)
            self.show_mazel_tov()
        except Exception:
            traceback.print_exc()
            self.label.setText("Something broke. What can I tell ya?")
            self.show_close_button()

    def show_oyvey_screen(self):
        self.label.clear()
        gif_path = os.path.join(os.path.dirname(__file__), "oyvey.gif")
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.label.setMovie(self.movie)
            self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
            self.movie.frameChanged.connect(self.check_oyvey_loops)
            self.movie.start()
            self.oyvey_loops = 0
        else:
            self.label.setText("Sorry, no results found.\nPlease try another time period or fuck off.")

    def check_oyvey_loops(self, frame_number):
        if self.movie and self.movie.currentFrameNumber() == self.movie.frameCount() - 1:
            self.oyvey_loops += 1
            if self.oyvey_loops >= 2:
                self.movie.stop()
                self.label.setText("Sorry, no results found.\nPlease try another time period or fuck off.")
                self.label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                self.show_home_close_buttons()

    def show_home_close_buttons(self):
        layout = QVBoxLayout()  # Changed to QVBoxLayout for better centering
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        layout.addSpacing(20)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        home_btn = QPushButton("Home")
        home_btn.setFixedSize(72, 72)
        home_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        home_btn.setStyleSheet(
            "QPushButton { background-color: #3CB371; color: white; font-size: 12px; border-radius: 36px; }"
            "QPushButton:hover { background-color: #2ea35c; }"
        )
        home_btn.clicked.connect(self.reset_to_home)

        close_btn = QPushButton("Close")
        close_btn.setFixedSize(72, 72)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet(
            "QPushButton { background-color: #87A8C3; color: white; font-size: 12px; border-radius: 36px; }"
            "QPushButton:hover { background-color: #6b94b4; }"
        )
        close_btn.clicked.connect(self.close)

        button_layout.addWidget(home_btn)
        button_layout.addSpacing(20)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        layout.addStretch()

        self.layout.addSpacing(10)
        self.layout.addLayout(layout)
        self.extra_buttons = [home_btn, close_btn]

    def reset_to_home(self):
        for b in self.extra_buttons:
            b.hide()
        self.label.clear()
        self.loop_counter = 0
        self.state = "start"
        self.grid_layout = QGridLayout()
        self.range_buttons.clear()
        self.show_date_options()

    def show_close_button(self):
        self.start_button.setText("Close")
        self.start_button.setStyleSheet(
            "border-radius: 60px; background-color: #87A8C3; color: white; font-size: 16px;"
        )
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.close)
        self.start_button.show()

    def show_mazel_tov(self):
        self.movie.stop()
        self.movie = QMovie(os.path.join(os.path.dirname(__file__), "mazel_tov.gif"))
        self.movie.frameChanged.connect(self.check_gif_loops)
        self.label.setMovie(self.movie)
        self.movie.start()
        self.loop_counter = 0

    def check_gif_loops(self, frame_number):
        if self.movie and self.movie.currentFrameNumber() == self.movie.frameCount() - 1:
            self.loop_counter += 1
            if self.loop_counter >= 2:
                self.movie.stop()
                self.label.clear()

                # Center the View Results button
                view_layout = QVBoxLayout()
                view_button_layout = QHBoxLayout()
                view_button_layout.addStretch()

                self.start_button.setText("View Results")
                self.start_button.setStyleSheet(
                    "border-radius: 60px; background-color: #3CB371; color: white; font-size: 16px;"
                )
                self.start_button.clicked.disconnect()
                self.start_button.clicked.connect(self.view_results)
                self.start_button.show()

                view_button_layout.addWidget(self.start_button)
                view_button_layout.addStretch()

                view_layout.addLayout(view_button_layout)
                view_layout.addStretch()
                self.layout.addLayout(view_layout)

                self.state = "view"

    def view_results(self):
        if os.path.exists(self.output_file):
            os.startfile(self.output_file)
        QTimer.singleShot(300, self.close)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DOBScraperGUI()
    gui.show()
    sys.exit(app.exec())
