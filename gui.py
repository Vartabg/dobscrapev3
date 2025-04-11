import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt, QTimer
from scraper_async import scrape_violations

class DOBScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOB Violations Scraper")
        self.setFixedSize(400, 400)
        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.button = QPushButton("Start")
        self.button.setFixedSize(120, 120)
        self.button.setStyleSheet(
            "border-radius: 60px; background-color: #1E90FF; color: white; font-size: 16px;"
        )
        self.button.clicked.connect(self.start_scraping)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.state = "start"
        self.output_file = "violations.csv"

    def start_scraping(self):
        if self.state == "start":
            self.button.hide()
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
            df = scrape_violations()
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
            df.to_csv(self.output_file, index=False)
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
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.movie.setLoopCount(3)
        self.label.setMovie(self.movie)
        self.movie.start()

        total_duration = self.movie.loopCount() * self.movie.nextFrameDelay() * self.movie.frameCount()
        QTimer.singleShot(total_duration, self.show_view_button)

    def show_view_button(self):
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