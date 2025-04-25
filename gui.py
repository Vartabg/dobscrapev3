import os
import sys
import subprocess
import pandas as pd
import scraper_async
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMovie, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QHBoxLayout, QMessageBox
)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def generate_excel(data, output_path="violations.xlsx"):
    """Generate Excel file from DataFrame with error handling"""
    try:
        data.to_excel(output_path, index=False)
        return True
    except Exception as e:
        print(f"Failed to generate Excel: {e}")
        return False

class MainWindow(QMainWindow):
    """Main application window for DOBScraper"""
    __slots__ = (
        'stack', 'results_screen', 'movie', 'result_movie',
        'jewish_font', 'config', 'db', 'logger',
        'locale_manager', 'error_reporter', 'translations',
        'gif_loop_count', 'loading_label', 'result_label'
    )

    def __init__(self):
        super().__init__()
        self.gif_loop_count = 0
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.setup_shortcuts()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(800, 600)  # Per v0.9.3-beta requirements
        self.setWindowTitle("DOB Scraper")
        
        # Initialize to None to handle cleanup later
        self.movie = None
        self.result_movie = None
        self.loading_label = None
        self.result_label = None
        self.results_screen = None

        self.home_screen()

    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_history)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+I"), self, self.show_about)
        QShortcut(QKeySequence("Esc"), self, self.close)

    def home_screen(self):
        """Create and display the home screen with start button"""
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
        """)
        start_button.clicked.connect(self.start_scraping)

        layout.addStretch()
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        home.setLayout(layout)
        self.stack.addWidget(home)
        self.stack.setCurrentWidget(home)

    def start_scraping(self):
        """Start the scraping process and show loading animation"""
        # Clean up previous movies if they exist
        self._cleanup_movies()
        
        loading_screen = QWidget()
        layout = QVBoxLayout()
        self.loading_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.loading_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        loading_screen.setLayout(layout)

        gif_path = resource_path("assets/flag.gif")
        if not os.path.exists(gif_path):
            QMessageBox.critical(self, "Error", f"Missing asset: {gif_path}")
            return
            
        self.movie = QMovie(gif_path)
        self.loading_label.setMovie(self.movie)
        self.movie.start()

        self.stack.addWidget(loading_screen)
        self.stack.setCurrentWidget(loading_screen)

        # Use a longer delay to ensure animation starts properly
        QTimer.singleShot(1000, self.run_real_scraper)

    def run_real_scraper(self):
        """Run the actual scraper backend"""
        try:
            real_data = scraper_async.scrape_violations(start_date="2020-01-01")
            self.scrape_done(real_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Scraping failed: {e}")
            self.show_home()

    def scrape_done(self, result):
        """Handle the completion of scraping and show appropriate results"""
        if self.movie:
            self.movie.stop()

        has_results = not result.empty

        if has_results:
            if not generate_excel(result):
                QMessageBox.warning(self, "Warning", "Could not generate Excel file")
                
            self._show_animation_screen("assets/mazeltov.gif", 3, self.show_success_button)
        else:
            self._show_animation_screen("assets/oyvey.gif", 2, self.show_error_buttons)

    def _show_animation_screen(self, gif_name, loop_count, callback_fn):
        """Generic method to show an animation and call a function when done"""
        # Clean up previous resources
        self._cleanup_movies()
        
        self.results_screen = QWidget()
        layout = QVBoxLayout()
        self.result_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.result_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.results_screen.setLayout(layout)
        self.stack.addWidget(self.results_screen)

        gif_path = resource_path(gif_name)
        if not os.path.exists(gif_path):
            QMessageBox.critical(self, "Error", f"Missing asset: {gif_path}")
            callback_fn()
            return
            
        self.result_movie = QMovie(gif_path)
        self.result_label.setMovie(self.result_movie)
        self.gif_loop_count = 0

        # Connect to the finished signal directly
        def on_frame_changed():
            # Check if we're at the last frame
            if self.result_movie.currentFrameNumber() == self.result_movie.frameCount() - 1:
                self.gif_loop_count += 1
                if self.gif_loop_count >= loop_count:
                    self.result_movie.stop()
                    callback_fn()

        self.result_movie.frameChanged.connect(on_frame_changed)
        self.result_movie.start()
        self.stack.setCurrentWidget(self.results_screen)

    def _cleanup_movies(self):
        """Clean up movie resources to prevent memory leaks"""
        if hasattr(self, 'movie') and self.movie:
            self.movie.stop()
            self.movie.deleteLater()
            self.movie = None
            
        if hasattr(self, 'result_movie') and self.result_movie:
            self.result_movie.stop()
            self.result_movie.deleteLater()
            self.result_movie = None

    def show_success_button(self):
        """Show success screen with button to view results"""
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
        
        if self.results_screen:
            self.stack.removeWidget(self.results_screen)
        self.results_screen = new_screen
        self.stack.addWidget(self.results_screen)
        self.stack.setCurrentWidget(self.results_screen)

    def show_error_buttons(self):
        """Show error screen with home and close buttons"""
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
        """)
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
        """)
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

        if self.results_screen:
            self.stack.removeWidget(self.results_screen)
        self.results_screen = new_screen
        self.stack.addWidget(self.results_screen)
        self.stack.setCurrentWidget(self.results_screen)

    def view_results(self):
        """Open the generated Excel file and close the application"""
        path = os.path.abspath("violations.xlsx")
        if os.path.exists(path):
            try:
                if os.name == 'nt':
                    os.startfile(path)
                else:
                    subprocess.Popen(['xdg-open', path])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open Excel: {e}")
        else:
            QMessageBox.warning(self, "Warning", "Results file not found")
        self.close()

    def show_home(self):
        """Return to the home screen"""
        self._cleanup_movies()
        self.stack.setCurrentIndex(0)

    def show_history(self):
        """Show history screen (placeholder)"""
        QMessageBox.information(self, "History", "History view not implemented yet")

    def show_about(self):
        """Show about screen (placeholder)"""
        QMessageBox.information(self, "About", "DOB Scraper v1.0.0\n\nProject: Mr. 4 in a Row")

    def closeEvent(self, event):
        """Handle application close event and cleanup resources"""
        self._cleanup_movies()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
