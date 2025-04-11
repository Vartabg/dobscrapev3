import sys
import os
import traceback
import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout
from PyQt6.QtGui import QMovie, QCursor
from PyQt6.QtCore import Qt, QTimer
from scraper_async import scrape_violations
from excel_generator import generate_excel_dashboard

class DOBScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOB Violations Scraper")
        self.setFixedSize(400, 620)
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

        self.layout.addSpacing(10)
        self.layout.addWidget(self.start_button)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.state = "start"
        self.output_file = "violations_dashboard.xlsx"
        self.loop_counter = 0
        self.range_buttons = []
        self.advanced_shown = False
        self.advanced_buttons = []
        self.grid_layout = QGridLayout()

    def show_date_options(self):
        self.start_button.hide()
        default_ranges = [
            ("Today", 0),
            ("Last 7 Days", 7),
            ("Last 30 Days", 30),
            ("Last 3 Months", 90),
            ("Last 6 Months", 180),
            ("Last Year", 365),
        ]
        advanced_ranges = [
            ("Last 2 Years", 730),
            ("All Since 2020", None),
            ("2015–2020 Only", "2015-01-01,2020-01-01")
        ]

        row, col = 0, 0
        for label, days in default_ranges:
            btn = self.make_range_button(label, days)
            self.grid_layout.addWidget(btn, row, col)
            col = (col + 1) % 2
            if col == 0:
                row += 1

        self.toggle_button = QPushButton("▸ More Options")
        self.toggle_button.setFixedSize(160, 40)
        self.toggle_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_button.setStyleSheet(self.get_style())
        self.toggle_button.clicked.connect(lambda: self.toggle_advanced(advanced_ranges, row + 1))
        self.grid_layout.addWidget(self.toggle_button, row + 1, 0, 1, 2)
        self.layout.insertLayout(1, self.grid_layout)

    def toggle_advanced(self, options, start_row):
        if self.advanced_shown:
            for btn in self.advanced_buttons:
                btn.hide()
            self.advanced_buttons.clear()
            self.toggle_button.setText("▸ More Options")
        else:
            col = 0
            for label, days in options:
                btn = self.make_range_button(label, days)
                self.grid_layout.addWidget(btn, start_row, col)
                self.advanced_buttons.append(btn)
                col = (col + 1) % 2
                if col == 0:
                    start_row += 1
            self.toggle_button.setText("▾ Hide Options")
        self.advanced_shown = not self.advanced_shown

    def make_range_button(self, label, days):
        btn = QPushButton(label)
        btn.setFixedSize(160, 40)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(self.get_style())
        btn.clicked.connect(lambda _, d=days: self.start_scraping(d))
        self.range_buttons.append(btn)
        return btn

    def get_style(self):
        return (
            "QPushButton { background-color: #e8f0fe; color: #1E90FF; font-size: 14px; border-radius: 12px; } "
            "QPushButton:hover { background-color: #d0e0ff; font-weight: bold; border: 1px solid #1E90FF; }"
        )

    def start_scraping(self, days):
        for btn in self.range_buttons + self.advanced_buttons:
            btn.hide()
        if isinstance(days, str) and "," in days:
            self.start_date = datetime.date(2015, 1, 1)
        else:
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
                print("No data returned.")
                self.label.setText("No data found.")
                self.show_close_button()
                return

            generate_excel_dashboard(df, self.output_file)
            print("Excel dashboard created.")
            self.show_mazel_tov()
        except Exception:
            print("Error during fetch:")
            traceback.print_exc()
            self.label.setText("Error occurred.")
            self.show_close_button()

    def show_close_button(self):
        self.start_button.setText("Close")
        self.start_button.setStyleSheet("border-radius: 60px; background-color: red; color: white; font-size: 16px;")
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