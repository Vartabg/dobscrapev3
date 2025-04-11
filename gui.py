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
        self.setFixedSize(360, 460)
        self.setWindowFlags(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(120, 120)
        self.start_button.setStyleSheet(
            "border-radius: 60px; background-color: #1E90FF; color: white; font-size: 16px;"
        )
        self.start_button.clicked.connect(self.show_date_options)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setFixedWidth(320)
        self.label.setFont(QFont("Segoe UI Hebrew", 11))

        self.layout.addSpacing(10)
        start_layout = QHBoxLayout()
        start_layout.addStretch()
        start_layout.addWidget(self.start_button)
        start_layout.addStretch()
        self.layout.addLayout(start_layout)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.state = "start"
        self.output_file = "violations_dashboard.xlsx"
        self.loop_counter = 0
        self.range_buttons = []
        self.grid_layout = QGridLayout()
        self.extra_buttons = []

    def show_date_options(self):
        self.start_button.hide()
        ranges = [
            ("Past Week", 7),
            ("Past 2 Weeks", 14),
            ("Past Month", 30),
            ("Past 3 Months", 90),
            ("Past 6 Months", 180),
            ("All Since 2020", None),
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

        self.layout.insertLayout(1, self.grid_layout)

    def start_scraping(self, days):
        for btn in self.range_buttons:
            btn.hide()

        today = datetime.date.today()
        self.start_date = today - datetime.timedelta(days=days) if days is not None else datetime.date(2020, 1, 1)
        print(f"Using start date: {self.start_date}")

        self.movie = QMovie("flag.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
        QTimer.singleShot(200, self.fetch_data)
        self.state = "fetching"

    def fetch_data(self):
        try:
            print("Starting scrape...")
            df = scrape_violations(start_date=self.start_date)
            print(f"Scrape completed. Rows: {len(df)}")
            if df.empty:
                self.show_oyvey_screen()
                return

            generate_excel_dashboard(df, self.output_file)
            print("Excel dashboard created.")
            self.show_mazel_tov()
        except Exception:
            print("Error during fetch:")
            traceback.print_exc()
            self.label.setText("Something broke. What can I tell ya?")
            self.show_close_button()

    def show_oyvey_screen(self):
        self.label.setText("Looks like nothin' came up for that time range.")
        self.label.setStyleSheet("font-size: 13px; color: #1E90FF; padding: 8px;")
        self.label.setFont(QFont("Segoe UI Hebrew", 11))
        self.movie = QMovie("oyvey.gif")
        self.label.setMovie(self.movie)
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.movie.frameChanged.connect(self.check_oyvey_loops)
        self.movie.start()
        self.oyvey_loops = 0

    def check_oyvey_loops(self, frame_number):
        if self.movie.currentFrameNumber() == self.movie.frameCount() - 1:
            self.oyvey_loops += 1
            if self.oyvey_loops >= 2:
                self.movie.stop()
                self.label.setText("Try another time range, or just close it out.")
                self.label.setStyleSheet("font-size: 13px; color: #1E90FF; padding: 8px;")
                self.label.setFont(QFont("Segoe UI Hebrew", 11))
                self.show_home_close_buttons()

    def show_home_close_buttons(self):
        layout = QHBoxLayout()

        home_btn = QPushButton("Home")
        home_btn.setFixedSize(80, 80)
        home_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        home_btn.setStyleSheet(
            "QPushButton { background-color: #3CB371; color: white; font-size: 13px; border-radius: 40px; }"
            "QPushButton:hover { background-color: #2ea35c; }"
        )
        home_btn.clicked.connect(self.reset_to_home)

        close_btn = QPushButton("Close")
        close_btn.setFixedSize(80, 80)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet(
            "QPushButton { background-color: #87A8C3; color: white; font-size: 13px; border-radius: 40px; }"
            "QPushButton:hover { background-color: #6b94b4; }"
        )
        close_btn.clicked.connect(self.close)

        layout.addStretch()
        layout.addWidget(home_btn)
        layout.addSpacing(20)
        layout.addWidget(close_btn)
        layout.addStretch()

        self.layout.addLayout(layout)
        self.extra_buttons = [home_btn, close_btn]

    def reset_to_home(self):
        for b in self.extra_buttons:
            b.hide()
        self.label.clear()
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
        self.movie = QMovie("mazel_tov.gif")
        self.movie.frameChanged.connect(self.check_gif_loops)
        self.label.setMovie(self.movie)
        self.movie.start()
        self.loop_counter = 0

    def check_gif_loops(self, frame_number):
        if self.movie.currentFrameNumber() == self.movie.frameCount() - 1:
            self.loop_counter += 1
            if self.loop_counter >= 2:
                self.movie.stop()
                self.label.clear()
                self.start_button.setText("View Results")
                self.start_button.setStyleSheet(
                    "border-radius: 60px; background-color: #3CB371; color: white; font-size: 16px;"
                )
                self.start_button.clicked.disconnect()
                self.start_button.clicked.connect(self.view_results)
                self.start_button.show()
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