import os
import sys
import subprocess
import datetime
import pandas as pd
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QSize
from PyQt6.QtGui import QMovie, QKeySequence, QShortcut, QFont, QFontDatabase, QPixmap, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QMessageBox, QGraphicsOpacityEffect, QHBoxLayout,
    QScrollArea, QGridLayout
)

# Import scraper module (will be implemented by Copilot/Gemini)
try:
    from scraper_async import scrape_violations
except ImportError:
    # Mock implementation for standalone testing
    def scrape_violations(start_date="2015-01-01"):
        print(f"Mock scraping violations since {start_date}")
        # Return empty DataFrame for testing
        return pd.DataFrame()

def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller compatibility"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DOBScraperGUI(QMainWindow):
    """Main GUI class for Mr. 4 in a Row application"""
    
    def __init__(self):
        super().__init__()
        
        # Setup window properties
        self.setWindowTitle("Mr. 4 in a Row")
        self.setFixedSize(800, 600)
        
        # Create stacked widget for screen flow
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Setup fonts
        self.setup_fonts()
        
        # Create screens
        self.create_start_screen()
        self.create_date_selection_screen()
        
        # Initialize variables
        self.selected_start_date = None
        
        # Setup shortcuts
        self.setup_shortcuts()
        
        # Show start screen
        self.stack.setCurrentIndex(0)
    
    def setup_fonts(self):
        """Load Jewish font if available, otherwise use Arial"""
        self.jewish_font = QFont("Arial", 12)
        try:
            # Attempt to load Jewish font
            font_path = resource_path("assets/fonts/jewish.ttf")
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                    self.jewish_font = QFont(font_family, 12)
                    print(f"Successfully loaded Jewish font: {font_family}")
        except Exception as e:
            print(f"Error loading font: {e}")
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Esc"), self, self.close)
    
    def create_start_screen(self):
        """Create the initial start screen with a single button"""
        start_screen = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create title label
        title_label = QLabel("Mr. 4 in a Row")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont(self.jewish_font.family(), 24, QFont.Weight.Bold))
        
        # Create subtitle label
        subtitle_label = QLabel("Building Violations Scraper")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont(self.jewish_font.family(), 16))
        
        # Create start button
        start_button = QPushButton("Start")
        start_button.setFixedSize(150, 150)
        start_button.setFont(QFont(self.jewish_font.family(), 18, QFont.Weight.Bold))
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                border-radius: 75px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        """)
        start_button.clicked.connect(self.show_date_selection)
        
        # Assemble layout
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(subtitle_label)
        layout.addSpacing(40)
        layout.addWidget(start_button, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        start_screen.setLayout(layout)
        self.stack.addWidget(start_screen)
    
    def create_date_selection_screen(self):
        """Create the date selection screen with accordion menu"""
        date_screen = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create title
        title_label = QLabel("Select Date Range")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont(self.jewish_font.family(), 24, QFont.Weight.Bold))
        
        # Create accordion sections
        
        # Recent Periods Section
        recent_label = QLabel("Recent Periods")
        recent_label.setFont(QFont(self.jewish_font.family(), 16, QFont.Weight.Bold))
        
        recent_grid = QGridLayout()
        recent_grid.setSpacing(10)
        
        # Create date range buttons for recent periods
        date_ranges = [
            ("Last 30 Days", self.get_date_days_ago(30)),
            ("Last 90 Days", self.get_date_days_ago(90)),
            ("Last 6 Months", self.get_date_days_ago(180)),
            ("Last Year", self.get_date_days_ago(365))
        ]
        
        for i, (label, date) in enumerate(date_ranges):
            btn = self.create_date_button(label, date)
            recent_grid.addWidget(btn, i // 2, i % 2)
        
        # Past Years Section
        years_label = QLabel("Past Years")
        years_label.setFont(QFont(self.jewish_font.family(), 16, QFont.Weight.Bold))
        
        years_grid = QGridLayout()
        years_grid.setSpacing(10)
        
        # Create date range buttons for past years
        current_year = datetime.datetime.now().year
        for i, year in enumerate(range(current_year, 2014, -1)):
            date = f"{year}-01-01"
            btn = self.create_date_button(f"{year}", date)
            years_grid.addWidget(btn, i // 2, i % 2)
        
        # All Since 2015 Section
        all_label = QLabel("All Time")
        all_label.setFont(QFont(self.jewish_font.family(), 16, QFont.Weight.Bold))
        
        all_btn = self.create_date_button("All Since 2015", "2015-01-01")
        
        # Assemble layout
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)
        
        # Add recent periods section
        main_layout.addWidget(recent_label)
        main_layout.addSpacing(5)
        main_layout.addLayout(recent_grid)
        main_layout.addSpacing(20)
        
        # Add past years section
        main_layout.addWidget(years_label)
        main_layout.addSpacing(5)
        main_layout.addLayout(years_grid)
        main_layout.addSpacing(20)
        
        # Add all since 2015 section
        main_layout.addWidget(all_label)
        main_layout.addSpacing(5)
        main_layout.addWidget(all_btn, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Add back button
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(100, 40)
        back_btn.setFont(self.jewish_font)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        """)
        back_btn.clicked.connect(self.show_start_screen)
        
        main_layout.addStretch()
        main_layout.addWidget(back_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Add scroll area for better viewing on small screens
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_content.setLayout(main_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        
        # Set up date screen layout
        date_layout = QVBoxLayout()
        date_layout.addWidget(scroll_area)
        date_screen.setLayout(date_layout)
        
        self.stack.addWidget(date_screen)
    
    def create_date_button(self, label_text, date_value):
        """Create a styled date button"""
        btn = QPushButton(label_text)
        btn.setFixedSize(120, 120)
        btn.setFont(self.jewish_font)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                border-radius: 60px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        """)
        # Use lambda to capture button-specific date value
        btn.clicked.connect(lambda checked, d=date_value: self.start_scraping(d))
        return btn
    
    def get_date_days_ago(self, days):
        """Calculate date X days ago in YYYY-MM-DD format"""
        today = datetime.datetime.now()
        past_date = today - datetime.timedelta(days=days)
        return past_date.strftime("%Y-%m-%d")
    
    def show_start_screen(self):
        """Show the initial start screen"""
        self.stack.setCurrentIndex(0)
    
    def show_date_selection(self):
        """Show the date selection screen"""
        self.stack.setCurrentIndex(1)
    
    def start_scraping(self, start_date):
        """Begin the scraping process with the selected start date"""
        self.selected_start_date = start_date
        
        # Create and show the loading screen with flag GIF
        self.create_scraping_screen()
        self.stack.setCurrentWidget(self.scraping_screen)
        
        # Start flag animation
        if hasattr(self, 'movie') and self.movie:
            self.movie.start()
        
        # Mock the scraping process with a timer for testing
        # In a real implementation, this would call the scraper asynchronously
        QTimer.singleShot(3000, self.process_scrape_results)
    
    def create_scraping_screen(self):
        """Create the loading screen with flag animation"""
        self.scraping_screen = QWidget()
        layout = QVBoxLayout()
        
        # Create title label
        title_label = QLabel("Scraping Building Violations")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont(self.jewish_font.family(), 24, QFont.Weight.Bold))
        
        # Create subtitle with date range
        subtitle_label = QLabel(f"Finding violations since {self.selected_start_date}")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont(self.jewish_font.family(), 16))
        
        # Create flag animation
        flag_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        gif_path = resource_path("assets/flag.gif")
        
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            flag_label.setMovie(self.movie)
        else:
            # Fallback if GIF is missing
            flag_label.setText("Loading...")
            flag_label.setFont(QFont(self.jewish_font.family(), 20, QFont.Weight.Bold))
        
        # Assemble layout
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(subtitle_label)
        layout.addSpacing(40)
        layout.addWidget(flag_label)
        layout.addStretch()
        
        self.scraping_screen.setLayout(layout)
        self.stack.addWidget(self.scraping_screen)
    
    def process_scrape_results(self):
        """Process the results from the scraper"""
        # In a real implementation, this would get results from the scraper
        # For testing, we'll simulate both success and failure paths
        
        # Mock scraping call
        try:
            # Call the actual scraper with the selected date
            results = scrape_violations(start_date=self.selected_start_date)
            
            # Check if we got any results
            has_results = not results.empty if hasattr(results, 'empty') else False
            
            # Stop the flag animation
            if hasattr(self, 'movie') and self.movie:
                self.movie.stop()
            
            # Show appropriate result screen
            if has_results:
                # Generate Excel file with results
                self.try_generate_excel(results)
                # Show success screen
                self.show_success_screen()
            else:
                # Show failure screen
                self.show_failure_screen()
                
        except Exception as e:
            print(f"Error during scraping: {e}")
            # Stop the flag animation
            if hasattr(self, 'movie') and self.movie:
                self.movie.stop()
            # Show failure screen
            self.show_failure_screen()
    
    def try_generate_excel(self, data):
        """Try to generate Excel file with the scraped data"""
        try:
            # Try to import the excel generator
            from excel_generator import generate_excel
            generate_excel(data, output_path="violations.xlsx")
            return True
        except ImportError:
            # Mock implementation for testing
            print("Excel generator not found, using mock implementation")
            try:
                if hasattr(data, 'to_excel'):
                    data.to_excel("violations.xlsx", index=False)
                else:
                    # Create dummy file for testing
                    with open("violations.xlsx", 'w') as f:
                        f.write("Mock Excel data")
                return True
            except Exception as e:
                print(f"Failed to generate Excel: {e}")
                return False
    
    def show_success_screen(self):
        """Show the success screen with Mazel Tov GIF"""
        self.success_screen = QWidget()
        layout = QVBoxLayout()
        
        # Create GIF label
        gif_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        gif_path = resource_path("assets/mazeltov.gif")
        
        if os.path.exists(gif_path):
            self.success_movie = QMovie(gif_path)
            gif_label.setMovie(self.success_movie)
            
            # Connect to frameChanged to detect when animation completes
            self.success_movie.frameChanged.connect(self.check_success_complete)
            self.success_movie.start()
        else:
            # Fallback if GIF is missing
            gif_label.setText("Mazel Tov!")
            gif_label.setFont(QFont(self.jewish_font.family(), 24, QFont.Weight.Bold))
            # Show final screen immediately
            QTimer.singleShot(1000, self.show_final_success_screen)
        
        # Assemble layout
        layout.addStretch()
        layout.addWidget(gif_label)
        layout.addStretch()
        
        self.success_screen.setLayout(layout)
        self.stack.addWidget(self.success_screen)
        self.stack.setCurrentWidget(self.success_screen)
    
    def check_success_complete(self):
        """Check if the Mazel Tov GIF has completed playing"""
        current_frame = self.success_movie.currentFrameNumber()
        total_frames = self.success_movie.frameCount()
        
        # If we're at the last frame
        if current_frame == total_frames - 1:
            self.success_movie.stop()
            self.show_final_success_screen()
    
    def show_final_success_screen(self):
        """Show the final success screen with buttons after GIF completes"""
        # Create a new widget for the final success screen
        final_screen = QWidget()
        layout = QVBoxLayout()
        
        # Add title label "Mazel Tov!"
        title_label = QLabel("Mazel Tov!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont(self.jewish_font.family(), 24, QFont.Weight.Bold))
        
        # Add subtitle "Your violation report has been successfully generated."
        subtitle_label = QLabel("Your violation report has been successfully generated.")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont(self.jewish_font.family(), 16))
        
        # Create buttons: Return Home and Exit App
        buttons_layout = QHBoxLayout()
        
        home_button = QPushButton("🏠 Return Home")
        home_button.setFixedSize(150, 50)
        home_button.setFont(self.jewish_font)
        home_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        """)
        home_button.clicked.connect(self.show_start_screen)
        
        exit_button = QPushButton("❌ Exit App")
        exit_button.setFixedSize(150, 50)
        exit_button.setFont(self.jewish_font)
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        """)
        exit_button.clicked.connect(self.close)
        
        # Add buttons to the horizontal layout with spacing
        buttons_layout.addStretch()
        buttons_layout.addWidget(home_button)
        buttons_layout.addSpacing(20)
        buttons_layout.addWidget(exit_button)
        buttons_layout.addStretch()
        
        # Assemble the final layout with proper spacing
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(subtitle_label)
        layout.addSpacing(30)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        final_screen.setLayout(layout)
        
        # Replace the previous results screen
        if self.success_screen:
            self.stack.removeWidget(self.success_screen)
        
        # Add and show the final success screen
        self.success_screen = final_screen
        self.stack.addWidget(self.success_screen)
        self.stack.setCurrentWidget(self.success_screen)
        
        # Apply fade-in animation
        self.apply_fade_in_effect(final_screen)
    
    def show_failure_screen(self):
        """Show the failure screen with Oy Vey GIF"""
        self.failure_screen = QWidget()
        layout = QVBoxLayout()
        
        # Create GIF label
        gif_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        gif_path = resource_path("assets/oyvey.gif")
        
        if os.path.exists(gif_path):
            self.failure_movie = QMovie(gif_path)
            gif_label.setMovie(self.failure_movie)
            
            # Connect to frameChanged to detect when animation completes
            self.failure_movie.frameChanged.connect(self.check_failure_complete)
            self.failure_movie.start()
        else:
            # Fallback if GIF is missing
            gif_label.setText("Oy Vey!")
            gif_label.setFont(QFont(self.jewish_font.family(), 24, QFont.Weight.Bold))
            # Show final screen immediately
            QTimer.singleShot(1000, self.show_final_failure_screen)
        
        # Assemble layout
        layout.addStretch()
        layout.addWidget(gif_label)
        layout.addStretch()
        
        self.failure_screen.setLayout(layout)
        self.stack.addWidget(self.failure_screen)
        self.stack.setCurrentWidget(self.failure_screen)
    
    def check_failure_complete(self):
        """Check if the Oy Vey GIF has completed playing"""
        current_frame = self.failure_movie.currentFrameNumber()
        total_frames = self.failure_movie.frameCount()
        
        # If we're at the last frame
        if current_frame == total_frames - 1:
            self.failure_movie.stop()
            self.show_final_failure_screen()
    
    def show_final_failure_screen(self):
        """Show the final failure screen with buttons after GIF completes"""
        # Create a new widget for the final failure screen
        final_screen = QWidget()
        layout = QVBoxLayout()
        
        # Add title label "Oy Vey!"
        title_label = QLabel("Oy Vey!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont(self.jewish_font.family(), 24, QFont.Weight.Bold))
        
        # Add subtitle "No building violations were found for the selected dates."
        subtitle_label = QLabel("No building violations were found for the selected dates.")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont(self.jewish_font.family(), 16))
        
        # Create buttons: Return Home and Exit App
        buttons_layout = QHBoxLayout()
        
        home_button = QPushButton("🏠 Return Home")
        home_button.setFixedSize(150, 50)
        home_button.setFont(self.jewish_font)
        home_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        """)
        home_button.clicked.connect(self.show_start_screen)
        
        exit_button = QPushButton("❌ Exit App")
        exit_button.setFixedSize(150, 50)
        exit_button.setFont(self.jewish_font)
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        """)
        exit_button.clicked.connect(self.close)
        
        # Add buttons to the horizontal layout with spacing
        buttons_layout.addStretch()
        buttons_layout.addWidget(home_button)
        buttons_layout.addSpacing(20)
        buttons_layout.addWidget(exit_button)
        buttons_layout.addStretch()
        
        # Assemble the final layout with proper spacing
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(subtitle_label)
        layout.addSpacing(30)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        final_screen.setLayout(layout)
        
        # Replace the previous results screen
        if self.failure_screen:
            self.stack.removeWidget(self.failure_screen)
        
        # Add and show the final failure screen
        self.failure_screen = final_screen
        self.stack.addWidget(self.failure_screen)
        self.stack.setCurrentWidget(self.failure_screen)
        
        # Apply fade-in animation
        self.apply_fade_in_effect(final_screen)
    
    def apply_fade_in_effect(self, widget, duration=400):
        """Apply a fade-in effect to the given widget.
        
        Args:
            widget: The QWidget to animate
            duration: Animation duration in milliseconds (default: 400ms)
        """
        # Create opacity effect
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
        
        # Create animation
        self.fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.fade_animation.setDuration(duration)  # 400ms (0.4 seconds)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(Qt.CurveShape.OutCubic)  # Smooth easing
        
        # Start animation
        self.fade_animation.start()


# Main entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DOBScraperGUI()
    window.show()
    sys.exit(app.exec())
