import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtCore import Qt, QTimer
from scraper_async import DOBScraperAsync
from filters import filter_data

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
        self.button.setStyleSheet("border-radius: 60px; background-color: #1E90FF; color: white; font-size: 16px;")
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
            scraper = DOBScraperAsync()
            df = scraper.run_scraper()
            df = filter_data(df)
            df.to_csv(self.output_file, index=False)
            self.show_mazel_tov()
        except Exception as e:
            self.label.setText(f"Error: {str(e)}")
            self.label.setStyleSheet("color: red; font-weight: bold;")

    def show_mazel_tov(self):
        self.movie.stop()
        self.label.setPixmap(QPixmap("mazel_tov.png").scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        self.button.setText("View Results")
        self.button.show()
        self.state = "view"

    def view_results(self):
        if os.path.exists(self.output_file):
            os.startfile(self.output_file)
        QTimer.singleShot(500, self.close)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DOBScraperGUI()
    gui.show()
    sys.exit(app.exec())
