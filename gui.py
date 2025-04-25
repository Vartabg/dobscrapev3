import os
import sys
import subprocess
import pandas as pd
import scraper_async
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QMovie, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QGraphicsOpacityEffect, QHBoxLayout
)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def generate_excel(data, output_path="violations.xlsx"):
    try:
        data.to_excel(output_path, index=False)
        return True
    except Exception as e:
        print(f"Failed to generate Excel: {e}")
        return False

class MainWindow(QMainWindow):
    __slots__ = (
        'stack', 'results_screen', 'movie', 'result_movie',
        'jewish_font', 'config', 'db', 'logger',
        'locale_manager', 'error_reporter', 'translations'
    )

    def __init__(self):
        super().__init__()
        self.gif_loop_count = 0
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.setup_shortcuts()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        self.home_screen()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_history)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+I"), self, self.show_about)
        QShortcut(QKeySequence("Esc"), self, self.close)

    def home_screen(self):
        home = QWidget()
        layout = QVBoxLayout()

        start_button = QPushButton("Start")
        start_button.setFixedSize(200, 200)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border-radius: 100px;
                font-family: 'Arial';
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        ""
        )
        start_button.clicked.connect(self.start_scraping)

        layout.addStretch()
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        home.setLayout(layout)
        self.stack.addWidget(home)
        self.stack.setCurrentWidget(home)

    def start_scraping(self):
        loading_screen = QWidget()
        layout = QVBoxLayout()
        self.loading_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.loading_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        loading_screen.setLayout(layout)

        gif_path = resource_path("assets/flag.gif")
        self.movie = QMovie(gif_path)
        self.loading_label.setMovie(self.movie)
        self.movie.start()

        self.stack.addWidget(loading_screen)
        self.stack.setCurrentWidget(loading_screen)

        QTimer.singleShot(1000, self.run_real_scraper)

    def run_real_scraper(self):
        real_data = scraper_async.scrape_violations(start_date="2020-01-01")
        self.scrape_done(real_data)

    def scrape_done(self, result):
        if hasattr(self, 'movie') and self.movie:
            self.movie.stop()

        has_results = not result.empty

        if has_results:
            generate_excel(result)

            self.results_screen = QWidget()
            layout = QVBoxLayout()
            self.result_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addStretch()
            layout.addWidget(self.result_label, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addStretch()
            self.results_screen.setLayout(layout)
            self.stack.addWidget(self.results_screen)

            gif_path = resource_path("assets/mazeltov.gif")
            self.result_movie = QMovie(gif_path)
            self.result_label.setMovie(self.result_movie)
            self.gif_loop_count = 0

            def check_loop():
                if self.result_movie.currentFrameNumber() == self.result_movie.frameCount() - 1:
                    self.gif_loop_count += 1
                    if self.gif_loop_count >= 3:
                        self.result_movie.stop()
                        self.result_label.clear()
                        self.show_success_button()
                    else:
                        frame_count = self.result_movie.frameCount()
                        if frame_count > 0:
                            duration = self.result_movie.nextFrameDelay() * frame_count
                            QTimer.singleShot(duration, check_loop)

            self.result_movie.frameChanged.connect(lambda: check_loop())
            self.result_movie.start()
            self.stack.setCurrentWidget(self.results_screen)
        else:
            self.handle_no_results()

    def show_success_button(self):
        new_screen = QWidget()
        layout = QVBoxLayout()

        view_results_button = QPushButton("View Results")
        view_results_button.setFixedSize(150, 150)
        view_results_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 75px;
                font-family: 'Arial';
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ""
        )
        view_results_button.clicked.connect(self.view_results)
        layout.addStretch()
        layout.addWidget(view_results_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        new_screen.setLayout(layout)
        self.stack.removeWidget(self.results_screen)
        self.results_screen = new_screen
        self.stack.addWidget(self.results_screen)
        self.stack.setCurrentWidget(self.results_screen)

    def handle_no_results(self):
        self.results_screen = QWidget()
        layout = QVBoxLayout()
        self.result_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.result_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.results_screen.setLayout(layout)
        self.stack.addWidget(self.results_screen)

        gif_path = resource_path("assets/oyvey.gif")
        self.result_movie = QMovie(gif_path)
        self.result_label.setMovie(self.result_movie)
        self.gif_loop_count = 0

        def check_loop():
            if self.result_movie.currentFrameNumber() == self.result_movie.frameCount() - 1:
                self.gif_loop_count += 1
                if self.gif_loop_count >= 2:
                    self.result_movie.stop()
                    self.show_error_buttons()
                else:
                    frame_count = self.result_movie.frameCount()
                    if frame_count > 0:
                        duration = self.result_movie.nextFrameDelay() * frame_count
                        QTimer.singleShot(duration, check_loop)

        self.result_movie.frameChanged.connect(lambda: check_loop())
        self.result_movie.start()
        self.stack.setCurrentWidget(self.results_screen)

    def show_error_buttons(self):
        new_screen = QWidget()
        layout = QVBoxLayout()

        home_button = QPushButton("Home")
        home_button.setFixedSize(100, 100)
        home_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 50px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        ""
        )
        home_button.clicked.connect(self.show_home)

        close_button = QPushButton("Close")
        close_button.setFixedSize(100, 100)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 50px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        ""
        )
        close_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(home_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(close_button)
        button_layout.addStretch()

        layout.addStretch()
        layout.addLayout(button_layout)
        layout.addStretch()

        new_screen.setLayout(layout)

        self.stack.removeWidget(self.results_screen)
        self.results_screen = new_screen
        self.stack.addWidget(self.results_screen)
        self.stack.setCurrentWidget(self.results_screen)

    def view_results(self):
        path = os.path.abspath("violations.xlsx")
        if os.path.exists(path):
            try:
                if os.name == 'nt':
                    os.startfile(path)
                else:
                    subprocess.Popen(['xdg-open', path], shell=True)
            except Exception as e:
                print(f"Failed to open Excel: {e}")
        self.close()

    def show_home(self):
        self.stack.setCurrentIndex(0)

    def show_history(self):
        print("History view not implemented yet")

    def show_about(self):
        print("About screen not implemented yet")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
