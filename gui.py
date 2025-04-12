
import sys
import asyncio
import os
import datetime
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMovie, QFont
import scraper_async
import excel_generator

class DOBViolationsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOB Violations Scraper")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)
        self.init_ui()

    def init_ui(self):
        self.clear_layout()
        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(200, 200)
        self.start_button.setStyleSheet("border-radius: 100px; background-color: white; font-size: 24px;")
        self.start_button.clicked.connect(self.show_date_options)
        self.layout.addWidget(self.start_button)

    def show_date_options(self):
        self.clear_layout()
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
            btn.setStyleSheet("border-radius: 25px; font-size: 18px;")
            btn.clicked.connect(lambda _, d=days: self.start_scraping(d))
            self.layout.addWidget(btn)

    def start_scraping(self, days):
        self.clear_layout()
        self.flag_label = QLabel()
        self.flag_movie = QMovie("assets/israel_flag.gif")
        self.flag_label.setMovie(self.flag_movie)
        self.layout.addWidget(self.flag_label)
        self.flag_movie.start()
        start_date = None
        if days:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        asyncio.ensure_future(self.run_scraper(start_date))

    async def run_scraper(self, start_date):
        violations = await scraper_async.fetch_violations(start_date)
        if not violations:
            self.show_no_results()
        else:
            excel_generator.generate_excel(violations)
            self.show_mazel_tov()

    def show_mazel_tov(self):
        self.clear_layout()
        self.mazel_label = QLabel()
        self.mazel_movie = QMovie("assets/mazel_tov.gif")
        self.mazel_movie.setScaledSize(self.size())
        self.mazel_label.setMovie(self.mazel_movie)
        self.layout.addWidget(self.mazel_label)
        self.mazel_movie.start()
        QTimer.singleShot(self.mazel_movie.duration() * 3, self.show_view_results)

    def show_view_results(self):
        self.clear_layout()
        view_button = QPushButton("View Results")
        view_button.setFixedSize(200, 200)
        view_button.setStyleSheet("border-radius: 100px; background-color: green; color: white; font-size: 24px;")
        view_button.clicked.connect(self.open_results)
        self.layout.addWidget(view_button)

    def open_results(self):
        filepath = os.path.abspath("violations.xlsx")
        webbrowser.open(filepath)
        self.close()

    def show_no_results(self):
        self.clear_layout()
        label = QLabel("sorry, no results found. please try a different time period or fuck off.")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Times New Roman", 16))
        self.layout.addWidget(label)

        oyvey = QLabel()
        movie = QMovie("assets/oyvey.gif")
        movie.setScaledSize(self.size())
        oyvey.setMovie(movie)
        self.layout.addWidget(oyvey)
        movie.start()
        QTimer.singleShot(movie.duration() * 2, self.show_home_and_close_buttons)

    def show_home_and_close_buttons(self):
        self.clear_layout()
        layout = QHBoxLayout()
        home_btn = QPushButton("🏠")
        close_btn = QPushButton("❌")
        for btn in (home_btn, close_btn):
            btn.setFixedSize(100, 100)
            btn.setStyleSheet("border-radius: 50px; font-size: 32px;")
        home_btn.clicked.connect(self.init_ui)
        close_btn.clicked.connect(self.close)
        layout.addWidget(home_btn)
        layout.addWidget(close_btn)
        self.layout.addLayout(layout)

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DOBViolationsApp()
    window.show()
    sys.exit(app.exec())
