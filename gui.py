# gui.py (Rewritten and clean for PyInstaller packaging)

import sys
import os
import subprocess
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QMovie, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer

import pandas as pd
from scraper_async import scrape_violations
from excel_generator import generate_excel

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class ScrapeWorker(QThread):
    finished = pyqtSignal(object)

    def __init__(self, start_date):
        super().__init__()
        self.start_date = start_date

    def run(self):
        results = scrape_violations(self.start_date)
        self.finished.emit(results)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mr. 4 in a Row")
        self.setFixedSize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_screen = self.build_home_screen()
        self.flag_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.gif_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.result_button = self.build_result_button()

        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.flag_label)
        self.stack.addWidget(self.gif_label)
        self.stack.addWidget(self.result_button)

    def build_home_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        button = QPushButton("Start")
        button.setFixedSize(120, 120)
        button.setStyleSheet("border-radius: 60px; font-size: 18px;")
        button.clicked.connect(self.start_scrape)
        layout.addSpacerItem(QSpacerItem(20, 200, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacerItem(QSpacerItem(20, 200, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        widget.setLayout(layout)
        return widget

    def build_result_button(self):
        widget = QWidget()
        layout = QVBoxLayout()
        button = QPushButton("View Results")
        button.setFixedSize(150, 150)
        button.setStyleSheet("border-radius: 75px; font-size: 18px; background-color: #4CAF50;")
        button.clicked.connect(self.view_results)
        layout.addSpacerItem(QSpacerItem(20, 150, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacerItem(QSpacerItem(20, 150, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        widget.setLayout(layout)
        return widget

    def start_scrape(self):
        self.stack.setCurrentWidget(self.flag_label)
        self.movie = QMovie(resource_path("assets/israel_flag.gif"))
        self.flag_label.setMovie(self.movie)
        self.movie.start()

        self.scraper = ScrapeWorker(datetime(2020, 1, 1))
        self.scraper.finished.connect(self.scrape_done)
        self.scraper.start()

    def scrape_done(self, result):
        if result.empty:
            gif_path = resource_path("assets/oyvey.gif")
        else:
            gif_path = resource_path("assets/mazeltov.gif")
            generate_excel(result)

        self.movie.stop()
        self.movie = QMovie(gif_path)
        self.gif_label.setMovie(self.movie)
        self.movie.start()

        QTimer.singleShot(9000, self.show_result_button)  # Loop 3x if ~3s each
        self.stack.setCurrentWidget(self.gif_label)

    def show_result_button(self):
        self.movie.stop()
        self.stack.setCurrentWidget(self.result_button)

    def view_results(self):
        path = os.path.abspath("violations.xlsx")
        subprocess.Popen(["start", path], shell=True)
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
