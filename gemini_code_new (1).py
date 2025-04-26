# gui.py (Gemini Version - Includes Safe GIF Loading)

import os
import sys
# Removed pandas import as results are checked by emptiness, not content here
# import pandas as pd
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, QTimer, QSize, QUrl # Ensure QUrl is imported if needed by QMovie path
from PyQt6.QtGui import QMovie, QKeySequence, QShortcut, QFont, QFontDatabase, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QHBoxLayout, QSpacerItem, QSizePolicy
)

# --- Attempt to import external dependencies ---
# These are needed for the actual functionality but GUI can run visually without them
try:
    from scraper_async import scrape_violations
    SCRAPER_AVAILABLE = True
except ImportError:
    print("Warning: scraper_async.py not found. Scraping will be simulated.")
    SCRAPER_AVAILABLE = False
    # Mock function for visual testing
    def scrape_violations(start_date):
        print(f"MOCK SCRAPE: Simulating scrape from {start_date}")
        import random
        # Simulate finding results ~70% of the time
        return None if random.random() < 0.3 else {"data": ["mock result"]} # Use a simple non-empty dict/list

try:
    from excel_generator import generate_excel
    EXCEL_GEN_AVAILABLE = True
except ImportError:
    print("Warning: excel_generator.py not found. Excel generation will be simulated.")
    EXCEL_GEN_AVAILABLE = False
    # Mock function for visual testing
    def generate_excel(data):
        print("MOCK EXCEL: Simulating Excel generation.")
        return True # Simulate success

# Utility function (Essential for PyInstaller)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".") # Use script's directory if not bundled

    return os.path.join(base_path, relative_path)

# --- Constants ---
# Paths using resource_path for PyInstaller compatibility
FONT_PATH = resource_path("assets/fonts/jewish.ttf")
FLAG_GIF_PATH = resource_path("assets/flag.gif")
MAZEL_TOV_GIF_PATH = resource_path("assets/mazeltov.gif") # Ensure filename matches project spec
OY_VEY_GIF_PATH = resource_path("assets/oyvey.gif")       # Ensure filename matches project spec

# Styling
ISRAELI_BLUE = "#0038b8"
WHITE_TEXT = "white"
DEFAULT_BG = "white"

# Sizes
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
START_BUTTON_SIZE = QSize(150, 150)
PERIOD_BUTTON_SIZE = QSize(120, 120)
FINAL_BUTTON_SIZE = QSize(150, 50)

# Fonts
LARGE_TITLE_SIZE = 24 # Adjusted from 36 for better fit? Test with 36 first.
SUBTITLE_SIZE = 16
BUTTON_FONT_SIZE = 14

class DOBScraperGUI(QMainWindow):
    """
    Main GUI window for the Mr. 4 in a Row (DOB Scraper) application.
    Handles user interaction, screen transitions, and triggers scraping.
    Gemini Version: Implements safe GIF loading with fallbacks.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mr. 4 in a Row")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(f"background-color: {DEFAULT_BG};")

        self.start_date = "2015-01-01" # Default, updated by selection
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.title_font_family = "Arial" # Default fallback font
        self.setup_font() # Load custom font if available
        self.setup_shortcuts()

        # --- Screen Creation & Setup ---
        # Create all screens upfront for smooth transitions
        self._create_start_screen()
        self._create_category_screen()
        self._create_period_screen_layout() # Create base layout, buttons added dynamically
        self._create_loading_screen()
        self._create_gif_screens() # Includes Gemini's safe loading
        self._create_final_result_screens()
        # --- End Screen Setup ---

        # Add screens to stack widget AFTER they are created
        self.start_screen_index = self.stack.addWidget(self.start_screen_widget)
        self.category_screen_index = self.stack.addWidget(self.category_screen_widget)
        self.period_screen_index = self.stack.addWidget(self.period_screen_widget)
        self.loading_screen_index = self.stack.addWidget(self.loading_screen_widget)
        self.success_gif_screen_index = self.stack.addWidget(self.success_gif_widget)
        self.failure_gif_screen_index = self.stack.addWidget(self.failure_gif_widget)
        self.final_success_screen_index = self.stack.addWidget(self.final_success_widget)
        self.final_failure_screen_index = self.stack.addWidget(self.final_failure_widget)

        # Set initial screen
        self.stack.setCurrentIndex(self.start_screen_index)

    # =========================================
    # Initialization and Helper Methods
    # =========================================

    def setup_font(self):
        """Loads the custom Jewish font if available, sets fallback."""
        if os.path.exists(FONT_PATH):
            font_id = QFontDatabase.addApplicationFont(FONT_PATH)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    self.title_font_family = font_families[0]
                    print(f"Successfully loaded font: {self.title_font_family}")
                    return # Success
                else:
                    print(f"Warning: Font file loaded but no families found in {FONT_PATH}. Falling back to Arial.")
            else:
                print(f"Warning: Could not load font at {FONT_PATH}. Falling back to Arial.")
        else:
             print(f"Warning: Font file not found at {FONT_PATH}. Falling back to Arial.")
        # Fallback already set by default
        self.title_font_family = "Arial"

    def _get_font(self, point_size, bold=False):
        """Helper to get a QFont object with the loaded font or fallback."""
        font = QFont(self.title_font_family, point_size)
        font.setBold(bold)
        return font

    def setup_shortcuts(self):
        """Setup keyboard shortcuts (Ctrl+Q, Esc to close)."""
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close_app)
        QShortcut(QKeySequence("Esc"), self, self.close_app)

    def _create_styled_button(self, text, size, on_click_method, is_circle=False):
        """Creates a styled button according to project specifications."""
        button = QPushButton(text)
        button.setFixedSize(size)

        border_radius = size.height() // 2 if is_circle else 10

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ISRAELI_BLUE};
                color: {WHITE_TEXT};
                border-radius: {border_radius}px;
                padding: 5px 10px;
                font-size: {BUTTON_FONT_SIZE}px;
                font-family: Arial; /* Consistent font for buttons */
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #004fd6; /* Lighter blue on hover */
            }}
            QPushButton:pressed {{
                background-color: #002a8c; /* Darker blue when pressed */
            }}
        """)
        button.clicked.connect(on_click_method)
        return button

    # --- Gemini Enhancement: Safe QMovie Loader ---
    def _create_safe_qmovie(self, asset_path, target_label, fallback_text, scaled_size=None):
        """
        Safely creates and assigns a QMovie to a QLabel, checking for file
        existence and movie validity. Sets fallback text on the label if the
        asset is missing or invalid.

        Args:
            asset_path (str): The resolved absolute path to the GIF asset.
            target_label (QLabel): The QLabel widget to display the movie or fallback text.
            fallback_text (str): Text to display in the label if the asset is not found or invalid.
            scaled_size (QSize, optional): Desired QSize for the QMovie scaling. Defaults to None.

        Returns:
            tuple: (QMovie | None, bool): Created QMovie object (or None) and validity flag.
        """
        movie = None
        is_valid = False

        # Default label alignment and font for fallback
        target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        target_label.setFont(self._get_font(SUBTITLE_SIZE)) # Use standard subtitle font for fallback

        if os.path.exists(asset_path):
            try:
                movie = QMovie(asset_path)
                if movie.isValid():
                    if scaled_size and isinstance(scaled_size, QSize):
                        movie.setScaledSize(scaled_size)
                    target_label.setMovie(movie)
                    is_valid = True
                else:
                    error_msg = f"{fallback_text}\n(Error: Invalid GIF format)"
                    target_label.setText(error_msg)
                    print(f"Error: QMovie invalid for existing file: '{asset_path}'. Check format/corruption.")
                    movie = None
                    is_valid = False
            except Exception as e:
                error_msg = f"{fallback_text}\n(Error: {e})"
                target_label.setText(error_msg)
                print(f"Error creating QMovie for '{asset_path}': {e}")
                movie = None
                is_valid = False
        else:
            target_label.setText(fallback_text)
            print(f"Warning: Asset not found at '{asset_path}'. Displaying fallback text.")
            movie = None
            is_valid = False

        return movie, is_valid

    # =========================================
    # Screen Creation Methods (Called from __init__)
    # =========================================

    def _create_start_screen(self):
        """Creates the initial screen with the large Start button."""
        self.start_screen_widget = QWidget()
        layout = QVBoxLayout(self.start_screen_widget)

        start_button = self._create_styled_button(
            "Start", START_BUTTON_SIZE, self.show_category_screen, is_circle=True
        )
        # Override font for the big start button if custom font loaded
        start_font = self._get_font(18, bold=True) if self.title_font_family != "Arial" else QFont("Arial", 18, QFont.Weight.Bold)
        start_button.setFont(start_font)


        layout.addStretch()
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def _create_category_screen(self):
        """Creates the screen with category selection buttons."""
        self.category_screen_widget = QWidget()
        layout = QVBoxLayout(self.category_screen_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center buttons vertically

        categories = [
            ("Recent Periods", self.show_recent_periods),
            ("Past Years", self.show_past_years),
            ("All Since 2015", lambda: self.begin_scraping("2015-01-01"))
        ]

        layout.addStretch(1)
        for label, func in categories:
            # Use styled button, but allow flexible width for text
            button = self._create_styled_button(label, QSize(250, 60), func, is_circle=False)
            layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addSpacing(20)
        layout.addStretch(1)

    def _create_period_screen_layout(self):
        """Creates the base layout for the period selection screen."""
        self.period_screen_widget = QWidget()
        # Main vertical layout to allow stretching
        main_layout = QVBoxLayout(self.period_screen_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Store the layout where buttons will be added/removed
        self.period_button_container = QVBoxLayout()
        self.period_button_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.period_button_container.setSpacing(15)

        main_layout.addStretch(1)
        main_layout.addLayout(self.period_button_container) # Add the button container
        main_layout.addStretch(1)

    def _create_loading_screen(self):
        """Creates the screen displaying the loading indicator (flag GIF)."""
        self.loading_screen_widget = QWidget()
        layout = QVBoxLayout(self.loading_screen_widget)

        self.flag_label = QLabel() # Create label for GIF/fallback

        # Use safe loader for the flag GIF
        self.flag_movie, self._flag_movie_valid = self._create_safe_qmovie(
             FLAG_GIF_PATH,
             self.flag_label,
             "Loading...\n(Flag GIF Missing)" # Fallback text
             # Optional: Add QSize(width, height) here if scaling needed
        )

        layout.addStretch()
        layout.addWidget(self.flag_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def _create_gif_screens(self):
        """Creates the intermediate success (Mazel Tov) and failure (Oy Vey) GIF screens."""
        # --- Success GIF Screen ---
        self.success_gif_widget = QWidget()
        layout_success = QVBoxLayout(self.success_gif_widget)
        layout_success.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.success_gif_label = QLabel() # Label for GIF/fallback

        # Use safe loader
        self.success_movie, self._success_movie_valid = self._create_safe_qmovie(
            MAZEL_TOV_GIF_PATH,
            self.success_gif_label,
            "Success!\n(Mazel Tov GIF Missing)"
            # Optional: Add QSize(width, height) for scaling
        )
        # Connect signal only if the movie is valid
        if self._success_movie_valid:
             self.success_movie.frameChanged.connect(self._check_success_frame)

        layout_success.addWidget(self.success_gif_label)


        # --- Failure GIF Screen ---
        self.failure_gif_widget = QWidget()
        layout_failure = QVBoxLayout(self.failure_gif_widget)
        layout_failure.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.failure_gif_label = QLabel() # Label for GIF/fallback

        # Use safe loader
        self.failure_movie, self._failure_movie_valid = self._create_safe_qmovie(
            OY_VEY_GIF_PATH,
            self.failure_gif_label,
            "No Results Found\n(Oy Vey GIF Missing)"
             # Optional: Add QSize(width, height) for scaling
        )
        # Connect signal only if valid
        if self._failure_movie_valid:
            self.failure_movie.frameChanged.connect(self._check_failure_frame)

        layout_failure.addWidget(self.failure_gif_label)


    def _create_final_result_screens(self):
        """Creates the final static success and failure result screens."""
        # --- Final Success Screen ---
        self.final_success_widget = QWidget()
        final_success_layout = QVBoxLayout(self.final_success_widget)

        title_success = QLabel("Mazel Tov!")
        title_success.setFont(self._get_font(LARGE_TITLE_SIZE, bold=True))
        title_success.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_success.setStyleSheet("color: black;")

        subtext_success = QLabel("Your violation report has been successfully generated.")
        subtext_success.setFont(self._get_font(SUBTITLE_SIZE))
        subtext_success.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtext_success.setWordWrap(True)
        subtext_success.setStyleSheet("color: black;")

        buttons_layout_success = QHBoxLayout()
        buttons_layout_success.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons_layout_success.setSpacing(20)

        home_button_success = self._create_styled_button("🏠 Return Home", FINAL_BUTTON_SIZE, self.go_home)
        exit_button_success = self._create_styled_button("❌ Exit App", FINAL_BUTTON_SIZE, self.close_app)

        buttons_layout_success.addWidget(home_button_success)
        buttons_layout_success.addWidget(exit_button_success)

        final_success_layout.addStretch(1)
        final_success_layout.addWidget(title_success)
        final_success_layout.addSpacing(15)
        final_success_layout.addWidget(subtext_success)
        final_success_layout.addSpacing(30)
        final_success_layout.addLayout(buttons_layout_success)
        final_success_layout.addStretch(1)

        # --- Final Failure Screen ---
        self.final_failure_widget = QWidget()
        final_failure_layout = QVBoxLayout(self.final_failure_widget)

        title_failure = QLabel("Oy Vey!")
        title_failure.setFont(self._get_font(LARGE_TITLE_SIZE, bold=True))
        title_failure.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_failure.setStyleSheet("color: black;")

        subtext_failure = QLabel("No building violations were found for the selected dates.")
        subtext_failure.setFont(self._get_font(SUBTITLE_SIZE))
        subtext_failure.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtext_failure.setWordWrap(True)
        subtext_failure.setStyleSheet("color: black;")

        buttons_layout_failure = QHBoxLayout()
        buttons_layout_failure.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons_layout_failure.setSpacing(20)

        home_button_failure = self._create_styled_button("🏠 Return Home", FINAL_BUTTON_SIZE, self.go_home)
        exit_button_failure = self._create_styled_button("❌ Exit App", FINAL_BUTTON_SIZE, self.close_app)

        buttons_layout_failure.addWidget(home_button_failure)
        buttons_layout_failure.addWidget(exit_button_failure)

        final_failure_layout.addStretch(1)
        final_failure_layout.addWidget(title_failure)
        final_failure_layout.addSpacing(15)
        final_failure_layout.addWidget(subtext_failure)
        final_failure_layout.addSpacing(30)
        final_failure_layout.addLayout(buttons_layout_failure)
        final_failure_layout.addStretch(1)

    # =========================================
    # Screen Navigation and Logic Methods
    # =========================================

    def show_category_screen(self):
        """Switches view to the category selection screen."""
        self.stack.setCurrentIndex(self.category_screen_index)

    def show_recent_periods(self):
        """Configures and shows the period selection screen for recent dates."""
        options = [
            ("Today", 0), ("1 Week", 7), ("2 Weeks", 14),
            ("1 Month", 30), ("3 Months", 90), ("6 Months", 180),
        ]
        self.populate_and_show_period_buttons(options)

    def show_past_years(self):
        """Configures and shows the period selection screen for past years."""
        options = [
            ("1 Year", 365), ("2 Years", 730), ("3 Years", 1095),
            ("4 Years", 1460), ("5 Years", 1825), ("6 Years", 2190),
            ("7 Years", 2555), ("8 Years", 2920), ("9 Years", 3285),
        ]
        self.populate_and_show_period_buttons(options)

    def populate_and_show_period_buttons(self, options):
        """Clears previous period buttons, adds new ones, and shows the screen."""
        # Clear existing buttons from the container layout
        while self.period_button_container.count():
            item = self.period_button_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater() # Ensure proper cleanup

        # Add new buttons based on options
        for label, days in options:
            button = self._create_styled_button(
                label, PERIOD_BUTTON_SIZE,
                # Use lambda correctly to capture the value of 'days' at creation time
                lambda checked, d=days: self.calculate_start_date(d),
                is_circle=True
            )
            self.period_button_container.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stack.setCurrentIndex(self.period_screen_index)

    def calculate_start_date(self, days_back):
        """Calculates the start date based on days back and triggers scraping."""
        today = datetime.today()
        # Handle 'Today' explicitly
        new_start = today if days_back == 0 else today - timedelta(days=days_back)

        # Enforce minimum date of Jan 1, 2015
        min_date = datetime(2015, 1, 1)
        if new_start < min_date:
            new_start = min_date

        self.begin_scraping(new_start.strftime("%Y-%m-%d")) # Use YYYY-MM-DD

    def begin_scraping(self, start_date):
        """Stores start date and transitions to the loading screen."""
        self.start_date = start_date
        print(f"Starting scrape from: {self.start_date}")
        self.show_loading_screen()

    def show_loading_screen(self):
        """Switches view to the loading screen and starts the flag GIF."""
        self.stack.setCurrentIndex(self.loading_screen_index)
        # Start the flag animation only if the movie is valid
        if self.flag_movie and self._flag_movie_valid:
            self.flag_movie.start()
        # Start scraping after short delay to allow UI to update
        QTimer.singleShot(500, self.scrape_violations)

    def scrape_violations(self):
        """Initiates the violation scraping process."""
        print("Scraping violations...")
        if not SCRAPER_AVAILABLE:
            # Use mock function if real one isn't imported
            result_data = scrape_violations(self.start_date)
            # Simulate delay for mock scrape
            QTimer.singleShot(2000, lambda: self.handle_scrape_result(result_data))
            return

        # --- Actual Scraper Call (Needs proper threading for non-blocking GUI) ---
        # This is a placeholder. A real implementation should use QThread
        # to run scrape_violations in the background.
        try:
            # Assuming scrape_violations is blocking for now or handles its own async
            result_data = scrape_violations(start_date=self.start_date)
            print(f"Scraping complete. Found results: {'Yes' if result_data else 'No'}") # Simplified check
            self.handle_scrape_result(result_data)
        except Exception as e:
            print(f"Error during scraping: {e}")
            self.handle_scrape_result(None) # Treat errors as failure

    def handle_scrape_result(self, result_data):
        """Processes scrape result, generates Excel, shows success/failure screen."""
        # Stop loading animation
        if hasattr(self, 'flag_movie') and self.flag_movie and self._flag_movie_valid:
            self.flag_movie.stop()

        # Check if result_data indicates success (not None, not empty dict/list etc.)
        # Adjust this check based on what scrape_violations actually returns
        if result_data and (isinstance(result_data, (dict, list)) and result_data): # Example check
            print("Violations found, generating Excel...")
            excel_success = False
            if EXCEL_GEN_AVAILABLE:
                try:
                    excel_success = generate_excel(result_data)
                    if excel_success:
                        print("Excel generated successfully.")
                    else:
                        print("Failed to generate Excel.")
                except Exception as e:
                    print(f"Error generating Excel: {e}")
                    excel_success = False # Ensure failure path
            else:
                 excel_success = generate_excel(result_data) # Call mock

            # Show success GIF screen only if Excel generation succeeded
            if excel_success:
                self.show_success_screen()
            else:
                 # Handle Excel generation failure - show failure screen?
                print("Treating Excel generation failure as overall failure.")
                self.show_failure_screen()
        else:
            print("No violations found or error occurred during scrape.")
            self.show_failure_screen() # Show Oy Vey GIF screen


    # =========================================
    # Success/Failure Flow Methods
    # =========================================

    def show_success_screen(self):
        """Displays the Mazel Tov GIF screen."""
        print("Showing Success GIF Screen")
        self.stack.setCurrentIndex(self.success_gif_screen_index)
        if self.success_movie and self._success_movie_valid:
            self.success_movie.start()
            self._success_frame_count = self.success_movie.frameCount()
            self._success_played_once = False
        else:
            # If GIF missing/invalid, skip directly to final screen after delay
            QTimer.singleShot(1000, self.show_final_success_screen)

    def _check_success_frame(self, frame_number):
        """Internal: Checks if the success GIF has played its last frame ONCE."""
        if not self._success_movie_valid or self._success_played_once: return
        if self._success_frame_count > 0 and frame_number == self._success_frame_count - 1:
            self._success_played_once = True
            QTimer.singleShot(100, self.check_success_complete) # Delay before transition

    def check_success_complete(self):
        """Called after Mazel Tov GIF finishes. Transitions to final success screen."""
        print("Success GIF complete, showing final success screen.")
        if self.success_movie: self.success_movie.stop()
        self.show_final_success_screen()

    def show_final_success_screen(self):
        """Displays the final static 'Mazel Tov' result screen."""
        print("Showing Final Success Screen")
        self.stack.setCurrentIndex(self.final_success_screen_index)

    def show_failure_screen(self):
        """Displays the Oy Vey GIF screen."""
        print("Showing Failure GIF Screen")
        self.stack.setCurrentIndex(self.failure_gif_screen_index)
        if self.failure_movie and self._failure_movie_valid:
            self.failure_movie.start()
            self._failure_frame_count = self.failure_movie.frameCount()
            self._failure_played_once = False
        else:
            # If GIF missing/invalid, skip directly to final screen after delay
             QTimer.singleShot(1000, self.show_final_failure_screen)

    def _check_failure_frame(self, frame_number):
        """Internal: Checks if the failure GIF has played its last frame ONCE."""
        if not self._failure_movie_valid or self._failure_played_once: return
        if self._failure_frame_count > 0 and frame_number == self._failure_frame_count - 1:
            self._failure_played_once = True
            QTimer.singleShot(100, self.check_failure_complete) # Delay before transition

    def check_failure_complete(self):
        """Called after Oy Vey GIF finishes. Transitions to final failure screen."""
        print("Failure GIF complete, showing final failure screen.")
        if self.failure_movie: self.failure_movie.stop()
        self.show_final_failure_screen()

    def show_final_failure_screen(self):
        """Displays the final static 'Oy Vey' result screen."""
        print("Showing Final Failure Screen")
        self.stack.setCurrentIndex(self.final_failure_screen_index)

    # =========================================
    # Action Methods (Button Clicks etc.)
    # =========================================

    def go_home(self):
        """Returns the user to the initial start screen."""
        print("Returning to home screen.")
        # Stop any potentially running movies
        if hasattr(self, 'flag_movie') and self.flag_movie: self.flag_movie.stop()
        if hasattr(self, 'success_movie') and self.success_movie: self.success_movie.stop()
        if hasattr(self, 'failure_movie') and self.failure_movie: self.failure_movie.stop()
        self.stack.setCurrentIndex(self.start_screen_index)

    def close_app(self):
        """Closes the application cleanly."""
        print("Exiting application.")
        QApplication.instance().quit()

# =========================================
# Main Execution Block
# =========================================
if __name__ == "__main__":
    # Ensure the 'assets' directory exists for the application to find resources
    if not os.path.exists("assets"):
        print("Warning: 'assets' directory not found. Creating it.")
        try:
            os.makedirs("assets")
            # Also create fonts subdir if base assets dir creation succeeds
            os.makedirs(os.path.join("assets", "fonts"), exist_ok=True)
        except OSError as e:
             print(f"Error: Could not create 'assets' directory: {e}. Application might not find resources.")

    app = QApplication(sys.argv)
    window = DOBScraperGUI()
    window.show()
    sys.exit(app.exec())