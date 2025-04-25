# gui.py – Updated GUI with polished GIF handling and result screen transitions

import os
import subprocess
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QMovie, QKeySequence, QShortcut
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QStackedWidget,
    QMessageBox
)

from utils import resource_path, generate_excel

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

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_history)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+I"), self, self.show_about)
        QShortcut(QKeySequence("Esc"), self, self.close)

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
        """)
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