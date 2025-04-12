# --- START OF FILE gui.py ---

import sys
import os
import subprocess # Needed for macOS/Linux open fallback
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                            QHBoxLayout, QWidget, QLabel, QGridLayout, QFrame,
                            QStackedWidget, QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QMovie, QFont, QColor, QPalette, QIcon
from PyQt6.QtCore import pyqtSignal, QThread
import pandas as pd # Import pandas for checking DataFrame
import traceback # For printing full errors

# === Integration: Reconnect backend components ===
try:
    from scraper_async import scrape_violations
    from excel_generator import generate_excel
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Backend modules not found ({e}). Running in GUI-only test mode.")
    BACKEND_AVAILABLE = False
    def scrape_violations(start_date):
        print("Warning: Using dummy scrape_violations.")
        # Simulate finding nothing to easily test Oy Vey flow
        return pd.DataFrame()
    def generate_excel(df, output_path="violations.xlsx"):
        print(f"Warning: Using dummy generate_excel. Would save to {output_path}.")
        pass
# =================================================

# --- Constants based on UX Design Brief ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
UX_BLUE = "#002B7F"
UX_GREEN = "#2ECC71"
UX_RED = "#e74c3c"
UX_WHITE = "#ffffff"
UX_BLACK = "#000000"
UX_HOVER_GRAY = "#F8F8F8"
FONT_FAMILY = "Arial, Segoe UI" # Use Arial or Segoe UI

DEFAULT_EXCEL_PATH = "violations.xlsx"

# --- Stylesheets based on UX Design Brief ---
MAIN_WINDOW_STYLE = f"background-color: {UX_WHITE};"

START_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {UX_WHITE};
        border: 3px solid {UX_BLUE};
        color: {UX_BLUE};
        border-radius: 100px; /* half of width/height */
        font-size: 24pt;
        font-family: {FONT_FAMILY};
        font-weight: bold;
        min-width: 200px;
        max-width: 200px;
        min-height: 200px;
        max-height: 200px;
    }}
    QPushButton:hover {{
        background-color: {UX_HOVER_GRAY}; /* Subtle hover */
    }}
    QPushButton:pressed {{
        background-color: #E0E0E0; /* Slightly darker press */
    }}
"""

DATE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {UX_WHITE};
        border: 1px solid {UX_BLACK}; /* Subtle border */
        color: {UX_BLACK};
        border-radius: 25px;
        font-size: 14pt; /* Readable size */
        font-family: {FONT_FAMILY};
        min-width: 300px;
        max-width: 300px;
        min-height: 50px;
        max-height: 50px;
        margin: 5px 0; /* Vertical margin */
    }}
    QPushButton:hover {{
        background-color: {UX_HOVER_GRAY};
    }}
    QPushButton:pressed {{
        background-color: #E0E0E0;
    }}
    QPushButton:checked {{
        background-color: {UX_BLUE};
        color: {UX_WHITE};
        border: 1px solid {UX_BLUE};
    }}
"""

FETCH_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {UX_GREEN};
        border: none;
        color: {UX_WHITE};
        border-radius: 25px;
        font-size: 14pt;
        font-family: {FONT_FAMILY};
        font-weight: bold;
        min-width: 150px; /* Smaller than date buttons */
        max-width: 150px;
        min-height: 50px;
        max-height: 50px;
    }}
    QPushButton:hover {{
        background-color: #27ae60; /* Darker Green */
    }}
    QPushButton:pressed {{
        background-color: #1e8449; /* Even Darker Green */
    }}
"""

BACK_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {UX_BLUE};
        border: none;
        color: {UX_WHITE};
        border-radius: 25px;
        font-size: 14pt;
        font-family: {FONT_FAMILY};
        font-weight: bold;
        min-width: 150px;
        max-width: 150px;
        min-height: 50px;
        max-height: 50px;
    }}
    QPushButton:hover {{
        background-color: #0039A8; /* Slightly Lighter Blue */
    }}
    QPushButton:pressed {{
        background-color: #001F5C; /* Darker Blue */
    }}
"""

VIEW_RESULTS_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {UX_GREEN};
        border: none;
        color: {UX_WHITE};
        border-radius: 100px; /* Circle */
        font-size: 18pt; /* Adjust as needed */
        font-family: {FONT_FAMILY};
        font-weight: bold;
        min-width: 200px;
        max-width: 200px;
        min-height: 200px;
        max-height: 200px;
        padding: 10px; /* Add padding if text is long */
    }}
     QPushButton:hover {{
        background-color: #27ae60;
    }}
    QPushButton:pressed {{
        background-color: #1e8449;
    }}
"""

HOME_SUCCESS_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {UX_BLUE};
        border: none;
        color: {UX_WHITE};
        border-radius: 50px; /* Circle */
        font-size: 14pt;
        font-family: {FONT_FAMILY};
        font-weight: bold;
        min-width: 100px;
        max-width: 100px;
        min-height: 100px;
        max-height: 100px;
    }}
     QPushButton:hover {{
        background-color: #0039A8;
    }}
    QPushButton:pressed {{
        background-color: #001F5C;
    }}
"""

OYVEY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {UX_BLUE}; /* Changed to blue as per brief visuals */
        border: none;
        color: {UX_WHITE};
        border-radius: 50px; /* Circle */
        font-size: 28pt; /* Larger for Emoji */
        font-family: {FONT_FAMILY};
        min-width: 100px;
        max-width: 100px;
        min-height: 100px;
        max-height: 100px;
        padding: 0px; /* No padding for emoji */
    }}
     QPushButton:hover {{
        background-color: #0039A8; /* Lighter Blue */
    }}
    QPushButton:pressed {{
        background-color: #001F5C; /* Darker Blue */
    }}
"""


class WorkerThread(QThread):
    """Worker thread for running data fetching and generation asynchronously"""
    finished = pyqtSignal(bool)  # Signal emits True if results were found and processed, False otherwise

    def __init__(self, date_range):
        super().__init__()
        if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
             raise ValueError("WorkerThread requires a date_range tuple (start_date, end_date)")
        self.date_range = date_range

    def run(self):
        if not BACKEND_AVAILABLE:
            print("Backend not available. Simulating data fetch...")
            self.sleep(3)
            results_found = False # Simulate no results for testing
            self.finished.emit(results_found)
            return

        try:
            start_date_dt = self.date_range[0]
            start_date_str = start_date_dt.strftime("%Y-%m-%d")
            print(f"WorkerThread: Starting data fetch for dates >= {start_date_str}")

            violations_df = scrape_violations(start_date=start_date_str)

            if violations_df is not None and not violations_df.empty:
                print(f"WorkerThread: Found {len(violations_df)} violations.")
                generate_excel(violations_df, output_path=DEFAULT_EXCEL_PATH)
                print(f"WorkerThread: Excel file generated at {DEFAULT_EXCEL_PATH}")
                self.finished.emit(True)
            else:
                print("WorkerThread: No violations found for the selected date range.")
                self.finished.emit(False)

        except Exception as e:
            print(f"WorkerThread: Error during backend processing - {e}")
            traceback.print_exc()
            self.finished.emit(False)


class Mr4InARowApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Window Setup based on Brief ---
        self.setWindowTitle("") # No window title
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT) # Fixed size
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        # Determine base path for assets and excel file
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.base_path, "assets")
        self.excel_path = os.path.join(self.base_path, DEFAULT_EXCEL_PATH)

        self.selected_date_range = None

        # --- Central Stacked Widget for Screens ---
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # --- Screen Objects (initialize attributes) ---
        self.start_screen_widget = None
        self.date_screen_widget = None
        self.loading_screen_widget = None
        self.success_screen_widget = None
        self.oyvey_screen_widget = None
        self.flag_movie = None
        self.mazel_tov_movie = None
        self.oyvey_movie = None

        # --- Create Screens ---
        self._create_start_screen()
        self._create_date_screen()
        self._create_loading_screen()
        self._create_success_screen()
        self._create_oyvey_screen()

        # --- Add Screens to Stacked Widget ---
        if self.start_screen_widget: self.stacked_widget.addWidget(self.start_screen_widget)
        if self.date_screen_widget: self.stacked_widget.addWidget(self.date_screen_widget)
        if self.loading_screen_widget: self.stacked_widget.addWidget(self.loading_screen_widget)
        if self.success_screen_widget: self.stacked_widget.addWidget(self.success_screen_widget)
        if self.oyvey_screen_widget: self.stacked_widget.addWidget(self.oyvey_screen_widget)

        # --- Show Initial Screen ---
        if self.start_screen_widget:
             self.show_screen(self.start_screen_widget)
        else:
             print("Error: Start screen widget not created.")


    # --- Screen Creation Methods ---

    def _create_start_screen(self):
        self.start_screen_widget = QWidget()
        layout = QVBoxLayout(self.start_screen_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        start_button = QPushButton("Start")
        start_button.setStyleSheet(START_BUTTON_STYLE)
        start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        start_button.clicked.connect(lambda: self.show_screen(self.date_screen_widget))

        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def _create_date_screen(self):
        self.date_screen_widget = QWidget()
        main_layout = QVBoxLayout(self.date_screen_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(10)

        self.date_buttons_group = []
        date_options_layout = QVBoxLayout()
        date_options_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_options_layout.setSpacing(5)

        date_ranges = [
            ("Last 30 Days", self.get_date_range(30)),
            ("Last 3 Months", self.get_date_range(90)),
            ("Last 6 Months", self.get_date_range(180)),
            ("Past Year", self.get_date_range(365)),
            ("Past 2 Years", self.get_date_range(730)),
            ("All Since 2020", (datetime(2020, 1, 1), datetime.now()))
        ]

        for label, date_range in date_ranges:
            button = QPushButton(label)
            button.setStyleSheet(DATE_BUTTON_STYLE)
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked, b=button, dr=date_range: self._on_date_button_selected(b, dr))
            date_options_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
            self.date_buttons_group.append(button)

        main_layout.addLayout(date_options_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.action_buttons_layout = QHBoxLayout()
        self.action_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.action_buttons_layout.setSpacing(30)

        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet(BACK_BUTTON_STYLE)
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.clicked.connect(self._go_back_to_start)
        self.back_button.hide()

        self.fetch_button = QPushButton("Fetch Data")
        self.fetch_button.setStyleSheet(FETCH_BUTTON_STYLE)
        self.fetch_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fetch_button.clicked.connect(self.start_data_fetch)
        self.fetch_button.hide()

        self.action_buttons_layout.addWidget(self.back_button)
        self.action_buttons_layout.addWidget(self.fetch_button)

        main_layout.addLayout(self.action_buttons_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

    def _create_loading_screen(self):
        self.loading_screen_widget = QWidget()
        layout = QVBoxLayout(self.loading_screen_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.loading_gif_label = QLabel()
        self.loading_gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flag_path = os.path.join(self.assets_dir, "flag.gif")

        if os.path.exists(flag_path):
            self.flag_movie = QMovie(flag_path)
            self.flag_movie.setScaledSize(QSize(600, 400))
            self.loading_gif_label.setMovie(self.flag_movie)
        else:
            print(f"Warning: Loading GIF not found at {flag_path}")
            self.loading_gif_label.setText("🇮🇱")
            self.loading_gif_label.setFont(QFont(FONT_FAMILY, 100))
            self.flag_movie = None

        fetching_label = QLabel("Fetching...")
        fetching_label.setFont(QFont(FONT_FAMILY, 16))
        fetching_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fetching_label.setStyleSheet(f"color: {UX_BLACK}; margin-top: 20px;")

        layout.addWidget(self.loading_gif_label)
        layout.addWidget(fetching_label)

    def _create_success_screen(self):
        self.success_screen_widget = QWidget()
        layout = QVBoxLayout(self.success_screen_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        self.success_gif_label = QLabel()
        self.success_gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mazel_tov_path = os.path.join(self.assets_dir, "mazel_tov.gif")

        if os.path.exists(mazel_tov_path):
            self.mazel_tov_movie = QMovie(mazel_tov_path)
            self.success_gif_label.setMovie(self.mazel_tov_movie)
            try: self.mazel_tov_movie.finished.disconnect(self._show_success_buttons)
            except TypeError: pass
            self.mazel_tov_movie.finished.connect(self._show_success_buttons)
        else:
            print(f"Warning: Success GIF not found at {mazel_tov_path}")
            self.success_gif_label.setText("🎉 Mazel Tov! 🎉")
            self.success_gif_label.setFont(QFont(FONT_FAMILY, 24))
            self.mazel_tov_movie = None
            QTimer.singleShot(200, self._show_success_buttons)

        layout.addWidget(self.success_gif_label)

        self.success_buttons_layout = QHBoxLayout()
        self.success_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.success_buttons_layout.setSpacing(40)

        self.home_success_button = QPushButton("Home")
        self.home_success_button.setStyleSheet(HOME_SUCCESS_BUTTON_STYLE)
        self.home_success_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.home_success_button.clicked.connect(self._go_back_to_start)
        self.home_success_button.hide()

        self.view_results_button = QPushButton("View\nResults")
        self.view_results_button.setStyleSheet(VIEW_RESULTS_BUTTON_STYLE)
        self.view_results_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_results_button.clicked.connect(self.view_results)
        self.view_results_button.hide()

        self.success_buttons_layout.addWidget(self.home_success_button)
        self.success_buttons_layout.addWidget(self.view_results_button)

        layout.addLayout(self.success_buttons_layout)

    def _create_oyvey_screen(self):
        self.oyvey_screen_widget = QWidget()
        layout = QVBoxLayout(self.oyvey_screen_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        oyvey_label = QLabel("Oy Vey!")
        oyvey_label.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        oyvey_label.setStyleSheet(f"color: {UX_RED};")
        oyvey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        explanation_text = "No results found. Please try another time period or fuck off."
        explanation_label = QLabel(explanation_text)
        explanation_label.setFont(QFont(FONT_FAMILY, 14))
        explanation_label.setStyleSheet(f"color: {UX_BLACK};")
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        explanation_label.setWordWrap(True)

        self.oyvey_gif_label = QLabel()
        self.oyvey_gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        oyvey_path = os.path.join(self.assets_dir, "oyvey.gif")

        if os.path.exists(oyvey_path):
            self.oyvey_movie = QMovie(oyvey_path)
            self.oyvey_movie.setScaledSize(QSize(400, 300))
            self.oyvey_gif_label.setMovie(self.oyvey_movie)
        else:
            print(f"Warning: Oy Vey GIF not found at {oyvey_path}")
            self.oyvey_gif_label.setText("😕")
            self.oyvey_gif_label.setFont(QFont(FONT_FAMILY, 100))
            self.oyvey_movie = None

        layout.addWidget(oyvey_label)
        layout.addWidget(explanation_label)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        layout.addWidget(self.oyvey_gif_label)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        oyvey_buttons_layout = QHBoxLayout()
        oyvey_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        oyvey_buttons_layout.setSpacing(40)

        home_oyvey_button = QPushButton("🏠")
        home_oyvey_button.setStyleSheet(OYVEY_BUTTON_STYLE)
        home_oyvey_button.setCursor(Qt.CursorShape.PointingHandCursor)
        home_oyvey_button.setToolTip("Go Home")
        home_oyvey_button.clicked.connect(self._go_back_to_start)

        close_oyvey_button = QPushButton("❌")
        close_oyvey_button.setStyleSheet(OYVEY_BUTTON_STYLE)
        close_oyvey_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_oyvey_button.setToolTip("Close Application")
        close_oyvey_button.clicked.connect(self.close)

        oyvey_buttons_layout.addWidget(home_oyvey_button)
        oyvey_buttons_layout.addWidget(close_oyvey_button)

        layout.addLayout(oyvey_buttons_layout)

    # --- Action and Navigation Methods ---

    def show_screen(self, screen_widget):
        """Switches to the specified screen widget and handles animations."""
        if not screen_widget:
            print("Error: Attempted to show a non-existent screen.")
            return

        current_widget = self.stacked_widget.currentWidget()

        if current_widget == screen_widget:
            return

        if current_widget:
            if current_widget == self.loading_screen_widget and self.flag_movie:
                self.flag_movie.stop()
            elif current_widget == self.success_screen_widget and self.mazel_tov_movie:
                 self.mazel_tov_movie.stop()
            elif current_widget == self.oyvey_screen_widget and self.oyvey_movie:
                 self.oyvey_movie.stop()

            self.fade_out_animation = QPropertyAnimation(current_widget, b"windowOpacity")
            self.fade_out_animation.setDuration(150)
            self.fade_out_animation.setStartValue(current_widget.windowOpacity())
            self.fade_out_animation.setEndValue(0.0)
            self.fade_out_animation.finished.connect(lambda: self._finish_transition(screen_widget))
            self.fade_out_animation.start()
        else:
            self._finish_transition(screen_widget)


    def _finish_transition(self, screen_widget):
        """Completes the screen switch, potentially fading in."""
        current_widget = self.stacked_widget.currentWidget()
        if current_widget:
             current_widget.setWindowOpacity(1.0) # Reset opacity just in case

        screen_widget.setWindowOpacity(0.0)
        self.stacked_widget.setCurrentWidget(screen_widget)

        if screen_widget == self.loading_screen_widget and self.flag_movie:
            self.flag_movie.start()
        elif screen_widget == self.success_screen_widget:
             if self.mazel_tov_movie:
                 # *** USE setLoops() INSTEAD OF setLoopCount() ***
                 self.mazel_tov_movie.setLoopCount(3) 
                 # ***********************************************
                 self.home_success_button.hide()
                 self.view_results_button.hide()
                 self.mazel_tov_movie.start()
             # Buttons shown via timer or finished signal
        elif screen_widget == self.oyvey_screen_widget and self.oyvey_movie:
             self.oyvey_movie.start()
        elif screen_widget == self.date_screen_widget:
            self._reset_date_screen()

        self.fade_in_animation = QPropertyAnimation(screen_widget, b"windowOpacity")
        self.fade_in_animation.setDuration(150)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.start()


    def _reset_date_screen(self):
        """Resets date button selection and hides action buttons."""
        self.selected_date_range = None
        if hasattr(self, 'date_buttons_group'):
            for button in self.date_buttons_group:
                button.setChecked(False)
        if hasattr(self, 'fetch_button'): self.fetch_button.hide()
        if hasattr(self, 'back_button'): self.back_button.hide()

    def _go_back_to_start(self):
        """Handles going back to the start screen."""
        if self.start_screen_widget:
             self.show_screen(self.start_screen_widget)

    def _on_date_button_selected(self, clicked_button, date_range):
        """Handles logic when a date range button is clicked."""
        for button in self.date_buttons_group:
            if button != clicked_button and button.isChecked():
                button.setChecked(False)

        if clicked_button.isChecked():
            self.selected_date_range = date_range
            print(f"Date range selected: {date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}")
            self.fetch_button.show()
            self.back_button.show()
        else:
            self.selected_date_range = None
            print("Date range deselected.")
            self.fetch_button.hide()
            self.back_button.hide()

    def _show_success_buttons(self):
        """Called when the Mazel Tov animation finishes or if no GIF."""
        if self.stacked_widget.currentWidget() == self.success_screen_widget:
            print("Showing success buttons.")
            self.home_success_button.show()
            self.view_results_button.show()
        else:
            print("Success screen no longer active. Buttons not shown.")


    def start_data_fetch(self):
        """Starts the background worker thread."""
        if self.selected_date_range is None:
            print("Error: No date range selected.")
            return
        if self.loading_screen_widget:
             self.show_screen(self.loading_screen_widget)
        else:
             print("Error: Loading screen not available.")
             return

        self.worker = WorkerThread(self.selected_date_range)
        self.worker.finished.connect(self.handle_fetch_completed)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def handle_fetch_completed(self, results_found):
        """Handles the result from the worker thread."""
        if results_found:
            print("Fetch completed: Results found.")
            if self.success_screen_widget:
                self.show_screen(self.success_screen_widget)
            else:
                print("Error: Success screen not available.")
        else:
            print("Fetch completed: No results found or error occurred.")
            if self.oyvey_screen_widget:
                self.show_screen(self.oyvey_screen_widget)
            else:
                print("Error: Oy Vey screen not available.")


    def view_results(self):
        """Opens the generated Excel file."""
        print(f"Attempting to open results file: {self.excel_path}")
        if os.path.exists(self.excel_path):
            try:
                if sys.platform == "win32":
                    os.startfile(self.excel_path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", self.excel_path], check=True)
                else:
                    subprocess.run(["xdg-open", self.excel_path], check=True)
                print(f"Successfully launched application for: {self.excel_path}")
            except FileNotFoundError:
                 print(f"Error: Could not find system command (open/xdg-open) to open the file.")
            except subprocess.CalledProcessError as e:
                 print(f"Error opening file with system command: {e}")
            except Exception as e:
                print(f"Error opening file {self.excel_path}: {e}")
                traceback.print_exc()
        else:
            print(f"Error: Could not find results file at {self.excel_path}")


    # --- Utility Methods ---
    def get_date_range(self, days):
        """Generate a date range tuple (start_date, end_date)"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return (start_date, end_date)


def main():
    app = QApplication(sys.argv)
    window = Mr4InARowApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
# --- END OF FILE gui.py ---