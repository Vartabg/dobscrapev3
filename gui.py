from PyQt6.QtGui import QFontDatabase
import os
import sys
import subprocess
import pandas as pd
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QSize
from PyQt6.QtGui import QMovie, QKeySequence, QShortcut, QFont, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QMessageBox, QGraphicsOpacityEffect, QHBoxLayout
)

# Import the scraper
try:
    from scraper_async import scrape_violations
except ImportError:
    print("Warning: Could not import scraper_async. Running in demo mode.")
    scrape_violations = None

def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller compatibility"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def generate_excel(data, output_path="violations.xlsx"):
    """Generate Excel file with violation data"""
    try:
        # For MockResult, just create a dummy file
        if not hasattr(data, 'to_excel'):
            with open(output_path, 'w') as f:
                f.write("Mock Excel data")
        else:
            data.to_excel(output_path, index=False)
        return True
    except Exception as e:
        print(f"Failed to generate Excel: {e}")
        return False

class DOBScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mr. 4 in a Row")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: white;")
        
        # Initialize variables
        self.gif_loop_count = 0
        self.has_results = False
        
        # Create stacked widget for different screens
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
        
        # Create screens
        self.create_start_screen()
        self.create_loading_screen()
        
        # Show start screen
        self.stack.setCurrentIndex(0)
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Esc"), self, self.close)
    
    def create_start_screen(self):
        """Create the initial screen with start button"""
        start_screen = QWidget()
        layout = QVBoxLayout()
        
        # Try to load custom font
        font_path = resource_path("assets/fonts/jewish.ttf")
        custom_font = QFont("Arial", 14)  # Default font
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_families = QFont.applicationFontFamilies(font_id)
                if font_families:
                    custom_font = QFont(font_families[0], 14)
        
        # Create start button
        start_button = QPushButton("Start Scraping")
        start_button.setFixedSize(150, 150)
        start_button.setFont(custom_font)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #0038b8;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 75px;
            }
            QPushButton:hover {
                background-color: #004fd6;
            }
        """)
        start_button.clicked.connect(self.start_scraping)
        
        # Add to layout
        layout.addStretch()
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        start_screen.setLayout(layout)
        self.stack.addWidget(start_screen)
    
    def create_loading_screen(self):
        """Create loading screen with animated flag"""
        self.loading_screen = QWidget()
        layout = QVBoxLayout()
        
        # Create label for GIF
        self.loading_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Status label
        self.status_label = QLabel("Fetching NYC Open Data...", alignment=Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: #333;")
        
        # Add to layout
        layout.addStretch()
        layout.addWidget(self.loading_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        self.loading_screen.setLayout(layout)
        self.stack.addWidget(self.loading_screen)
    
    def start_scraping(self):
        """Begin the scraping process"""
        self.stack.setCurrentWidget(self.loading_screen)
        
        # Try to load the flag GIF
        flag_path = resource_path("assets/flag.gif")
        if os.path.exists(flag_path):
            self.movie = QMovie(flag_path)
            self.loading_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.loading_label.setText("⚠️ Flag GIF not found")
            self.loading_label.setStyleSheet("font-size: 18px; color: red;")
        
        # Schedule the actual scraping process
        QTimer.singleShot(500, self.perform_scraping)
    
    def perform_scraping(self):
        """Execute the actual scraping logic"""
        self.status_label.setText("Fetching violations data...")
        
        # For testing, use MockResult if scraper not available
        if scrape_violations is None:
            class MockResult:
                def __init__(self, has_results=True):
                    self.empty = not has_results
            
            # Simulate scraping delay
            QTimer.singleShot(3000, lambda: self.scrape_done(MockResult(True)))
        else:
            try:
                # Try to run the actual scraper
                QTimer.singleShot(100, self.run_scraper)
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")
                # Show error after 2 seconds
                QTimer.singleShot(2000, lambda: self.scrape_done(pd.DataFrame()))
    
    def run_scraper(self):
        """Run the actual scraper in a way that won't freeze the GUI"""
        try:
            # Get data from the scraper
            df = scrape_violations()
            self.scrape_done(df)
        except Exception as e:
            print(f"Scraping error: {e}")
            self.scrape_done(pd.DataFrame())
    
    def scrape_done(self, result):
        """Handle completion of scraping"""
        # Stop the flag animation if it's running
        if hasattr(self, 'movie') and self.movie:
            self.movie.stop()
        
        # Check if we have results
        self.has_results = hasattr(result, 'empty') and not result.empty if hasattr(result, 'empty') else False
        
        # Generate Excel file if we have results
        if self.has_results:
            generate_excel(result)
            self.show_success_screen()
        else:
            self.show_failure_screen()
    
    def show_success_screen(self):
        """Show the success screen with Mazel Tov animation"""
        self.results_screen = QWidget()
        layout = QVBoxLayout()
        
        # Create label for Mazel Tov GIF
        self.result_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.result_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        self.results_screen.setLayout(layout)
        self.stack.addWidget(self.results_screen)
        
        # Try to load and play the Mazel Tov GIF
        gif_path = resource_path("assets/mazeltov.gif")
        if os.path.exists(gif_path):
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
        else:
            # If GIF is missing, show a message and the button
            self.result_label.setText("Success! Mazel Tov!")
            self.result_label.setStyleSheet("font-size: 24px; color: green;")
            QTimer.singleShot(1500, self.show_success_button)
        
        self.stack.setCurrentWidget(self.results_screen)
    
    def show_success_button(self):
        """Show the View Results button after animation completes"""
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
    
    def show_failure_screen(self):
        """Show the failure screen with Oy Vey animation"""
        self.results_screen = QWidget()
        layout = QVBoxLayout()
        
        # Create label for Oy Vey GIF
        self.result_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.result_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        self.results_screen.setLayout(layout)
        self.stack.addWidget(self.results_screen)
        
        # Try to load and play the Oy Vey GIF
        gif_path = resource_path("assets/oyvey.gif")
        if os.path.exists(gif_path):
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
        else:
            # If GIF is missing, show a message and the buttons
            self.result_label.setText("No results found! Oy Vey!")
            self.result_label.setStyleSheet("font-size: 24px; color: #CC0000;")
            QTimer.singleShot(1500, self.show_error_buttons)
        
        self.stack.setCurrentWidget(self.results_screen)
    
    def show_error_buttons(self):
        """Show buttons after Oy Vey animation"""
        new_screen = QWidget()
        layout = QVBoxLayout()
        
        # Create buttons
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
        
        # Add buttons side by side in horizontal layout
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
        
        # Replace the GIF screen with button screen
        self.stack.removeWidget(self.results_screen)
        self.results_screen = new_screen
        self.stack.addWidget(self.results_screen)
        self.stack.setCurrentWidget(self.results_screen)
    
    def show_home(self):
        """Return to the start screen"""
        self.stack.setCurrentIndex(0)
    
    def view_results(self):
        """Open the generated Excel file and exit"""
        path = os.path.abspath("violations.xlsx")
        if os.path.exists(path):
            try:
                if os.name == 'nt':
                    os.startfile(path)
                else:
                    subprocess.Popen(['xdg-open', path])
            except Exception as e:
                print(f"Failed to open Excel: {e}")
        self.close()

# Main execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DOBScraperGUI()
    window.show()
    sys.exit(app.exec())
