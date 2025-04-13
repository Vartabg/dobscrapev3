# Reconstruct and save the correct full gui.py file with resource_path and complete logic.
# This will be a proper version ready for packaging and testing.

from pathlib import Path  # ✅ This fixes the NameError

final_gui_path = Path("/mnt/data/gui.py")

final_gui_template = '''
import sys
import os
import subprocess
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QMovie, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer

import pandas as pd
from scraper_async import scrape_violations
from excel_generator import generate_excel

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class WorkerThread(QThread):
    finished = pyqtSignal(bool)

    def __init__(self, date_range):
        super().__init__()
        self.date_range = date_range

    def run(self):
        try:
            start_date = self.date_range[0].strftime("%Y-%m-%d")
            print(f"WorkerThread: Starting data fetch for {start_date}")
            df = scrape_violations(start_date=start_date)
            if df is not None and not df.empty:
                generate_excel(df)
                self.finished.emit(True)
            else:
                self.finished.emit(False)
        except Exception as e:
            print(f"Error in thread: {e}")
            self.finished.emit(False)

class Mr4App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("")
        self.setFixedSize(800, 600)

        self.selected_date_range = None
        self.mazel_tov_loop_count = 0

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_screen()
        self.date_screen()
        self.loading_screen()
        self.success_screen()
        self.oyvey_screen()

        self.stack.setCurrentWidget(self.start_widget)

    def start_screen(self):
        self.start_widget = QWidget()
        layout = QVBoxLayout(self.start_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn = QPushButton("Start")
        btn.setFixedSize(200, 200)
        btn.setStyleSheet("background-color: white; border: 3px solid #002B7F; color: #002B7F; border-radius: 100px; font-size: 24pt;")
        btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.date_widget))
        layout.addWidget(btn)
        self.stack.addWidget(self.start_widget)

    def date_screen(self):
        self.date_widget = QWidget()
        layout = QVBoxLayout(self.date_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.date_buttons = []
        self.button_group = QVBoxLayout()
        options = [
            ("Last 30 Days", 30),
            ("Last 3 Months", 90),
            ("Last 6 Months", 180),
            ("Past Year", 365),
            ("Past 2 Years", 730),
            ("All Since 2020", (datetime(2020, 1, 1), datetime.now())),
        ]
        for label, days in options:
            btn = QPushButton(label)
            btn.setFixedSize(300, 50)
            btn.setStyleSheet("border-radius: 25px; font-size: 14pt;")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, b=btn, d=days: self.select_date_range(b, d))
            self.date_buttons.append(btn)
            self.button_group.addWidget(btn)

        layout.addLayout(self.button_group)

        self.fetch_btn = QPushButton("Fetch Data")
        self.fetch_btn.setStyleSheet("background-color: #2ECC71; color: white; border-radius: 25px; font-size: 14pt;")
        self.fetch_btn.setFixedSize(150, 50)
        self.fetch_btn.setVisible(False)
        self.fetch_btn.clicked.connect(self.start_data_fetch)

        self.back_btn = QPushButton("Back")
        self.back_btn.setStyleSheet("background-color: #002B7F; color: white; border-radius: 25px; font-size: 14pt;")
        self.back_btn.setFixedSize(150, 50)
        self.back_btn.setVisible(False)
        self.back_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.start_widget))

        btns = QHBoxLayout()
        btns.addWidget(self.back_btn)
        btns.addWidget(self.fetch_btn)
        layout.addLayout(btns)

        self.stack.addWidget(self.date_widget)

    def select_date_range(self, button, days):
        for btn in self.date_buttons:
            btn.setChecked(False)
        button.setChecked(True)
        if isinstance(days, int):
            self.selected_date_range = (datetime.now() - timedelta(days=days), datetime.now())
        else:
            self.selected_date_range = days
        self.fetch_btn.setVisible(True)
        self.back_btn.setVisible(True)

    def loading_screen(self):
        self.loading_widget = QWidget()
        layout = QVBoxLayout(self.loading_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel()
        self.flag_movie = QMovie(resource_path("assets/israel_flag.gif"))
        self.flag_movie.setScaledSize(QSize(600, 400))
        label.setMovie(self.flag_movie)
        layout.addWidget(label)
        self.stack.addWidget(self.loading_widget)

    def success_screen(self):
        self.success_widget = QWidget()
        layout = QVBoxLayout(self.success_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mazel_label = QLabel()
        self.mazel_tov_movie = QMovie(resource_path("assets/mazel_tov.gif"))
        self.mazel_tov_movie.setScaledSize(QSize(600, 400))
        self.mazel_tov_movie.frameChanged.connect(self._count_mazel_tov_loops)
        self.mazel_label.setMovie(self.mazel_tov_movie)
        layout.addWidget(self.mazel_label)
        self.view_btn = QPushButton("View Results")
        self.view_btn.setFixedSize(200, 200)
        self.view_btn.setStyleSheet("border-radius: 100px; background-color: #2ECC71; color: white; font-size: 18pt;")
        self.view_btn.clicked.connect(self.view_results)
        self.view_btn.setVisible(False)
        self.home_btn = QPushButton("Home")
        self.home_btn.setFixedSize(100, 100)
        self.home_btn.setStyleSheet("border-radius: 50px; background-color: #002B7F; color: white; font-size: 14pt;")
        self.home_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.start_widget))
        self.home_btn.setVisible(False)
        btns = QHBoxLayout()
        btns.addWidget(self.home_btn)
        btns.addWidget(self.view_btn)
        layout.addLayout(btns)
        self.stack.addWidget(self.success_widget)

    def oyvey_screen(self):
        self.oyvey_widget = QWidget()
        layout = QVBoxLayout(self.oyvey_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel("Oy Vey!")
        label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(label)
        sub = QLabel("No results found. Please try another time period or fuck off.")
        sub.setFont(QFont("Arial", 14))
        layout.addWidget(sub)
        gif_label = QLabel()
        self.oyvey_movie = QMovie(resource_path("assets/oyvey.gif"))
        self.oyvey_movie.setScaledSize(QSize(400, 300))
        gif_label.setMovie(self.oyvey_movie)
        layout.addWidget(gif_label)
        btns = QHBoxLayout()
        home = QPushButton("🏠")
        home.setFixedSize(100, 100)
        home.setStyleSheet("border-radius: 50px; background-color: #002B7F; color: white; font-size: 24pt;")
        home.clicked.connect(lambda: self.stack.setCurrentWidget(self.start_widget))
        close = QPushButton("❌")
        close.setFixedSize(100, 100)
        close.setStyleSheet("border-radius: 50px; background-color: #e74c3c; color: white; font-size: 24pt;")
        close.clicked.connect(self.close)
        btns.addWidget(home)
        btns.addWidget(close)
        layout.addLayout(btns)
        self.stack.addWidget(self.oyvey_widget)

    def start_data_fetch(self):
        if not self.selected_date_range:
            return
        self.stack.setCurrentWidget(self.loading_widget)
        self.flag_movie.start()
        self.worker = WorkerThread(self.selected_date_range)
        self.worker.finished.connect(self.handle_scraper_done)
        self.worker.start()

    def handle_scraper_done(self, success):
        self.flag_movie.stop()
        if success:
            self.mazel_tov_loop_count = 0
            self.view_btn.setVisible(False)
            self.home_btn.setVisible(False)
            self.stack.setCurrentWidget(self.success_widget)
            self.mazel_tov_movie.start()
        else:
            self.stack.setCurrentWidget(self.oyvey_widget)
            self.oyvey_movie.start()

    def _count_mazel_tov_loops(self, frame_num):
        if self.mazel_tov_movie.currentFrameNumber() == self.mazel_tov_movie.frameCount() - 1:
            self.mazel_tov_loop_count += 1
            if self.mazel_tov_loop_count >= 3:
                self.mazel_tov_movie.stop()
                self.view_btn.setVisible(True)
                self.home_btn.setVisible(True)

    def view_results(self):
        path = os.path.abspath("violations.xlsx")
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            print(f"Error opening results: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Mr4App()
    win.show()
    sys.exit(app.exec())
'''

# Save the file
final_gui_path.write_text(final_gui_template.strip())

# Return for download
final_gui_path
