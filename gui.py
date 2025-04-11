import sys
import os
import traceback
import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt, QTimer
from scraper_async import scrape_violations
from excel_generator import generate_excel_dashboard

class DOBScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOB Violations Scraper")
        self.setFixedSize(400, 460)
        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dropdown = QComboBox()
        self.dropdown.addItems([
            "Last 30 Days",
            "Last 3 Months",
            "Last 6 Months",
            "All Since 2020"
        ])
        self.dropdown.setCurrentIndex(3)
        self.dropdown.setStyleSheet("font-size: 14px; padding: 6px; background-color: #e8f0fe; border: none; border-radius: 12px; color: #1E90FF; font-weight: bold;")

        self.button = QPushButton("Start")
        self.button.setFixedSize(120, 120)
        self.button.setStyleSheet(
            "border-radius: 60px; background-color: #1E90FF; color: white; font-size: 16px;"
        )
        self.button.clicked.connect(self.start_scraping)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dropdown.setFixedWidth(200)
self.layout.addSpacing(20)
self.layout.addWidget(self.dropdown)
self.layout.addSpacing(10)
self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.state = "start"
        self.output_file = "violations_dashboard.xlsx"
        self.loop_counter = 0

    def get_start_date(self):
        today = datetime.date.today()
        selection = self.dropdown.currentText()
        if "30" in selection:
            return today - datetime.timedelta(days=30)
        elif "3 Months" in selection:
            return today - datetime.timedelta(days=90)
        elif "6 Months" in selection:
            return today - datetime.timedelta(days=180)
        return datetime.date(2020, 1, 1)

    def start_scraping(self):
        if self.state == "start":
            self.start_date = self.get_start_date()
            print(f"Selected start date: {self.start_date}")
            self.button.hide()
            self.dropdown.hide()
            self.movie = QMovie("flag.gif")
            self.label.setMovie(self.movie)
            self.movie.start()
            QTimer.singleShot(200, self.fetch_data)
            self.state = "fetching"
        elif self.state == "view":
            self.view_results()

    def fetch_data(self):
        try:
            print("Starting scrape...")
            df = scrape_violations(start_date=self.start_date)
            print(f"Scrape completed. Rows: {len(df)}")
            if df.empty:
                print("No data returned.")
                self.label.setText("No data found.")
                self.button.setText("Close")
                self.button.setStyleSheet("border-radius: 60px; background-color: red; color: white; font-size: 16px;")
                self.button.show()
                self.button.clicked.disconnect()
                self.button.clicked.connect(self.close)
                self.state = "error"
                return

            generate_excel_dashboard(df, self.output_file)
            print("Excel dashboard created.")
            self.show_mazel_tov()
        except Exception as e:
            print("An error occurred during scraping:")
            traceback.print_exc()
            self.label.setText("Error occurred")
            self.button.setText("Close")
            self.button.setStyleSheet("border-radius: 60px; background-color: red; color: white; font-size: 16px;")
            self.button.show()
            self.button.clicked.disconnect()
            self.button.clicked.connect(self.close)
            self.state = "error"

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
            print(f"Loop {self.loop_counter} completed.")
            if self.loop_counter >= 2:
                self.movie.stop()
                self.label.clear()
                self.button.setText("View Results")
                self.button.setStyleSheet(
                    "border-radius: 60px; background-color: #3CB371; color: white; font-size: 16px;"
                )
                self.button.show()
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