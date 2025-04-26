# gui.py

import os
import sys
import subprocess
import pandas as pd
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, QSize, QParallelAnimationGroup, QAbstractAnimation
from PyQt6.QtGui import QMovie, QKeySequence, QShortcut, QFont, QFontDatabase, QColor, QPalette, QLinearGradient, QPainter, QPen, QPainterPath, QBrush
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QHBoxLayout, QGridLayout, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect
)

# Import scraper
from scraper_async import scrape_violations
from excel_generator import generate_excel

# Utility
def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller compatibility"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class IsraeliButton(QPushButton):
    """Modern blue and white button with clear visibility and sleek animations"""
    def __init__(self, text, button_style="primary", parent=None):
        super().__init__(text, parent)
        
        # Define button styles with blue and white only
        self.button_styles = {
            # Primary style: White with strong blue accents
            "primary": {
                "bg_normal": "#ffffff",
                "bg_hover": "#f0f7ff",    # Very light blue on hover
                "bg_pressed": "#e1edff",  # Slightly deeper light blue when pressed
                "accent": "#0046b8",      # Strong Israeli blue
                "text": "#0046b8",        # Blue text for contrast
                "border": "#0046b8"       # Blue border
            },
            # Secondary style: Blue with white text
            "secondary": {
                "bg_normal": "#0046b8",   # Strong Israeli blue
                "bg_hover": "#0052d4",    # Slightly lighter blue on hover
                "bg_pressed": "#003a9c",  # Slightly darker blue when pressed
                "accent": "#ffffff",      # White accent
                "text": "#ffffff",        # White text for contrast
                "border": "#0052d4"       # Slightly lighter blue border
            }
        }
        
        # Set button style
        self.button_style = button_style if button_style in self.button_styles else "primary"
        self.colors = self.button_styles[self.button_style]
        
        # Track states
        self._hovered = False
        self._pressed = False
        self.setMouseTracking(True)
        
        # Set up effects
        self.setup_effects()
        
        # Custom styling - minimal stylesheet
        self.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                text-align: center;
            }
        """)
        
    def setup_effects(self):
        """Set up visual effects for the button"""
        # Enhanced shadow effect for better visibility
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(8)
        
        # Set shadow color based on button style
        if self.button_style == "primary":
            self.shadow.setColor(QColor(0, 70, 184, 50))  # Blue shadow for white buttons
        else:
            self.shadow.setColor(QColor(0, 0, 0, 60))     # Darker shadow for blue buttons
            
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        
    def paintEvent(self, event):
        """Custom painting for sleek design"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate corner radius - responsive to button height
        corner_radius = min(8, self.height() / 5)
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(1, 1, self.width()-2, self.height()-2, corner_radius, corner_radius)
        
        # Clip to the rounded rectangle
        painter.setClipPath(path)
        
        # Fill background based on state
        if self._pressed:
            painter.fillPath(path, QColor(self.colors["bg_pressed"]))
        elif self._hovered:
            painter.fillPath(path, QColor(self.colors["bg_hover"]))
        else:
            painter.fillPath(path, QColor(self.colors["bg_normal"]))
        
        # Draw accent border - clear and visible
        pen = QPen()
        
        # Primary (white) buttons have thicker border for better visibility
        if self.button_style == "primary":
            pen.setWidth(2)  # Thicker border for white buttons
        else:
            pen.setWidth(1)  # Standard border for blue buttons
            
        pen.setColor(QColor(self.colors["border"]))
        painter.setPen(pen)
        
        # Draw a complete border around the button
        painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, corner_radius, corner_radius)
        
        # Draw text with precise color
        painter.setPen(QColor(self.colors["text"]))
        
        # Draw centered text
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        
    def enterEvent(self, event):
        """Handle mouse enter with smooth animation"""
        self._hovered = True
        
        # Animate shadow effect
        shadow_anim = QPropertyAnimation(self.shadow, b"blurRadius")
        shadow_anim.setStartValue(8)
        shadow_anim.setEndValue(12)
        shadow_anim.setDuration(150)
        shadow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animate shadow offset
        offset_anim = QPropertyAnimation(self.shadow, b"offset")
        offset_anim.setStartValue(QPoint(0, 2))
        offset_anim.setEndValue(QPoint(0, 3))
        offset_anim.setDuration(150)
        offset_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Group animations
        self.hover_anim_group = QParallelAnimationGroup(self)
        self.hover_anim_group.addAnimation(shadow_anim)
        self.hover_anim_group.addAnimation(offset_anim)
        self.hover_anim_group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave with smooth animation"""
        self._hovered = False
        
        # Animate shadow effect
        shadow_anim = QPropertyAnimation(self.shadow, b"blurRadius")
        shadow_anim.setStartValue(12)
        shadow_anim.setEndValue(8)
        shadow_anim.setDuration(150)
        shadow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animate shadow offset
        offset_anim = QPropertyAnimation(self.shadow, b"offset")
        offset_anim.setStartValue(QPoint(0, 3))
        offset_anim.setEndValue(QPoint(0, 2))
        offset_anim.setDuration(150)
        offset_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Group animations
        self.leave_anim_group = QParallelAnimationGroup(self)
        self.leave_anim_group.addAnimation(shadow_anim)
        self.leave_anim_group.addAnimation(offset_anim)
        self.leave_anim_group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        
        self.update()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse press with inset effect"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            
            # Button appears to be pressed inward
            self.shadow.setBlurRadius(4)
            self.shadow.setOffset(0, 1)
            
            self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release with animation and ripple effect"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            
            # Create elegant ripple
            self._create_clean_ripple(event.position().x(), event.position().y())
            
            # Restore shadow based on current hover state
            if self._hovered:
                self.shadow.setBlurRadius(12)
                self.shadow.setOffset(0, 3)
            else:
                self.shadow.setBlurRadius(8)
                self.shadow.setOffset(0, 2)
                
            self.update()
        super().mouseReleaseEvent(event)

    def _create_clean_ripple(self, x, y):
        """Create modern ripple effect"""
        # Create ripple widget as child
        ripple = QWidget(self)
        ripple.setGeometry(0, 0, 10, 10)
        
        # Set ripple color based on button style
        if self.button_style == "primary":
            ripple_color = QColor(self.colors["accent"])
            ripple_color.setAlpha(40)  # Semi-transparent blue ripple on white
        else:
            ripple_color = QColor(255, 255, 255, 50)  # Semi-transparent white ripple on blue
            
        ripple.setStyleSheet(f"background-color: {ripple_color.name(QColor.NameFormat.HexArgb)}; border-radius: 5px;")
        ripple.show()
        
        # Center ripple at click position
        ripple.move(int(x - 5), int(y - 5))
        
        # Create opacity effect
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.8)
        ripple.setGraphicsEffect(opacity_effect)
        
        # Animate ripple expansion
        size_anim = QPropertyAnimation(ripple, b"geometry")
        size_anim.setStartValue(QRect(int(x - 5), int(y - 5), 10, 10))
        
        # Target ripple size based on button size
        final_size = max(self.width(), self.height()) * 2
        size_anim.setEndValue(QRect(
            int(x - final_size/2), 
            int(y - final_size/2), 
            final_size, 
            final_size
        ))
        size_anim.setDuration(400)  # Slightly longer for elegance
        size_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Animate opacity
        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setStartValue(0.8)
        fade_anim.setEndValue(0.0)
        fade_anim.setDuration(400)
        fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Create animation group
        group = QParallelAnimationGroup(self)
        group.addAnimation(size_anim)
        group.addAnimation(fade_anim)
        
        # Delete ripple when done
        group.finished.connect(ripple.deleteLater)
        group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)


class DOBScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOB Violations Scraper")
        self.setFixedSize(800, 600)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: white;
            }
            QLabel {
                color: #333333;
            }
        """)

        self.start_date = "2015-01-01"
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.setup_shortcuts()
        self.output_file_path = os.path.abspath("violations.xlsx")

        # Clear Israeli blue color scheme
        self.israeli_blue = "#0046b8"  # Strong Israeli blue
        self.israeli_blue_light = "#0052d4"  # Lighter blue for hover states
        self.israeli_blue_dark = "#003a9c"  # Darker blue for pressed states
        
        # Button styles - only primary (white) and secondary (blue)
        self.primary_btn_style = "primary"   # White with blue accents
        self.secondary_btn_style = "secondary"  # Blue with white text
        
        # Load Jewish fonts
        self.setup_fonts()

        self.start_screen()
        self.stack.setCurrentIndex(0)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Esc"), self, self.close)
    
    def setup_fonts(self):
        """Set up Jewish fonts with corrected QFontDatabase usage"""
        # Define Jewish font priority list (system fonts first)
        self.jewish_fonts = [
            "Frank Ruehl CLM",  # Traditional Jewish font
            "Hadassah Friedlaender", 
            "David CLM",        # Classic Hebrew font
            "Narkisim",         # Popular Hebrew font
            "Miriam CLM", 
            "David Libre",      # Google's Hebrew font
            "Shofar"            # Decorative Jewish font
        ]
        
        # Add embedded fonts from assets
        font_paths = [
            ("assets/fonts/FrankRuehlCLM-Medium.ttf", "Frank Ruehl CLM"),
            ("assets/fonts/DavidCLM-Medium.ttf", "David CLM"),
            ("assets/fonts/MiriamCLM-Book.ttf", "Miriam CLM"),
            ("assets/fonts/ShofarRegular.ttf", "Shofar"),
            ("assets/fonts/jewish.ttf", "Jewish")  # Fallback
        ]
        
        # Try to load the fonts
        self.available_jewish_fonts = []
        
        # First try embedded fonts
        for font_path, font_name in font_paths:
            full_path = resource_path(font_path)
            if os.path.exists(full_path):
                font_id = QFontDatabase.addApplicationFont(full_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        actual_name = families[0]
                        print(f"Loaded font: {actual_name} from {font_path}")
                        self.available_jewish_fonts.append(actual_name)
        
        # Then check system fonts - Using static methods
        system_families = QFontDatabase.families()
        for font_name in self.jewish_fonts:
            if font_name not in self.available_jewish_fonts and font_name in system_families:
                print(f"Found system font: {font_name}")
                self.available_jewish_fonts.append(font_name)
        
        # Set the main font based on availability
        if self.available_jewish_fonts:
            self.main_font_family = self.available_jewish_fonts[0]
            print(f"Using Jewish font: {self.main_font_family}")
        else:
            self.main_font_family = "Arial"  # Fallback
            print("No Jewish fonts available, using Arial")
        
        # Set font sizes
        self.title_font = QFont(self.main_font_family, 24, QFont.Weight.Bold)
        self.subtitle_font = QFont(self.main_font_family, 16)
        self.button_font = QFont(self.main_font_family, 12, QFont.Weight.Bold)
        self.small_font = QFont(self.main_font_family, 10)

    def create_styled_button(self, text, width=200, height=50, is_primary=True, connect_to=None):
        """Create a blue and white button with clear visibility"""
        # Use primary (white) or secondary (blue) style
        button_style = self.primary_btn_style if is_primary else self.secondary_btn_style
        button = IsraeliButton(text, button_style=button_style)
        button.setFixedSize(width, height)
        button.setFont(self.button_font)
        
        # Connect signal if provided
        if connect_to:
            button.clicked.connect(connect_to)
            
        return button

    # Safe QMovie loader
    def _create_safe_qmovie(self, asset_path, target_label, fallback_text, scaled_size=None):
        """
        Safely creates and assigns a QMovie to a QLabel, checking for file
        existence and movie validity. Sets fallback text on the label if the
        asset is missing or invalid.
        """
        movie = None
        is_valid = False

        # Default label alignment and font for fallback
        target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if os.path.exists(asset_path):
            try:
                movie = QMovie(asset_path)
                if movie.isValid():
                    if scaled_size:
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

    def start_screen(self):
        """First screen with Start button"""
        start_screen = QWidget()
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("DOB Violations Scraper")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet(f"color: {self.israeli_blue};")
        
        # Subtitle
        subtitle_label = QLabel("Building Violation Reports")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(self.subtitle_font)

        # Start button with blue styling (secondary/blue)
        start_button = self.create_styled_button("Start", 220, 60, False, self.show_category_screen)

        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(subtitle_label)
        layout.addSpacing(40)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        start_screen.setLayout(layout)
        self.stack.addWidget(start_screen)

    def show_category_screen(self):
        """Show the accordion menu"""
        self.category_screen = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Select Category")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet(f"color: {self.israeli_blue};")
        
        layout.addWidget(title_label)
        layout.addSpacing(30)

        # Category buttons alternating blue and white for visual hierarchy
        recent_button = self.create_styled_button("Recent Periods", 250, 60, 
                                                False,  # Blue button 
                                                self.show_recent_periods)
        
        years_button = self.create_styled_button("Past Years", 250, 60, 
                                                True,   # White button
                                                self.show_past_years)
        
        all_button = self.create_styled_button("All Since 2015", 250, 60,
                                              False,  # Blue button
                                              lambda: self.begin_scraping("2015-01-01"))

        layout.addWidget(recent_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(years_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(all_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        
        # Back button (white)
        back_button = self.create_styled_button("Back", 120, 40, 
                                              True,
                                              lambda: self.stack.setCurrentIndex(0))
        
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.category_screen.setLayout(layout)
        self.stack.addWidget(self.category_screen)
        self.stack.setCurrentWidget(self.category_screen)

    def show_recent_periods(self):
        """Show Recent Periods selection"""
        self.show_period_buttons([
            ("Today", 0),
            ("1 Week", 7),
            ("2 Weeks", 14),
            ("1 Month", 30),
            ("3 Months", 90),
            ("6 Months", 180),
        ], "Recent Periods", False)  # Blue buttons

    def show_past_years(self):
        """Show Past Years selection"""
        self.show_period_buttons([
            ("1 Year", 365),
            ("2 Years", 730),
            ("3 Years", 1095),
            ("4 Years", 1460),
            ("5 Years", 1825),
            ("6 Years", 2190),
            ("7 Years", 2555),
            ("8 Years", 2920),
            ("9 Years", 3285),
        ], "Past Years", True)  # White buttons

    def show_period_buttons(self, options, title_text, use_primary_style):
        """Generate dynamic period buttons in a grid layout with visual rhythm"""
        self.period_screen = QWidget()
        main_layout = QVBoxLayout()
        
        # Header
        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet(f"color: {self.israeli_blue};")
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)
        
        # Grid layout for buttons - 3 columns
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # Add buttons to grid
        for i, (label, days) in enumerate(options):
            row, col = divmod(i, 3)  # 3 columns
            
            # Create buttons with consistent style
            button = self.create_styled_button(
                label, 180, 50, 
                use_primary_style,  # Consistent style across all buttons in this grid
                lambda checked, d=days: self.calculate_start_date(d)
            )
            
            grid_layout.addWidget(button, row, col)
        
        # Back button (opposite style for contrast)
        back_button = self.create_styled_button(
            "Back", 120, 40, 
            not use_primary_style,  # Opposite style for visual distinction
            self.show_category_screen
        )
        
        # Add grid to main layout
        main_layout.addLayout(grid_layout)
        main_layout.addSpacing(30)
        main_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.period_screen.setLayout(main_layout)
        self.stack.addWidget(self.period_screen)
        self.stack.setCurrentWidget(self.period_screen)

    def calculate_start_date(self, days_back):
        today = datetime.today()
        new_start = today - timedelta(days=days_back)
        # Enforce minimum date of Jan 1, 2015
        if new_start < datetime(2015, 1, 1):
            new_start = datetime(2015, 1, 1)
        self.begin_scraping(new_start.strftime("%Y-%m-%d"))

    def begin_scraping(self, start_date):
        self.start_date = start_date
        self.show_loading_screen()

    def show_loading_screen(self):
        """Show Israeli flag while scraping"""
        loading_screen = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Processing Request")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet(f"color: {self.israeli_blue};")
        
        # Subtitle with date
        subtitle_label = QLabel(f"Searching for violations since {self.start_date}")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(self.subtitle_font)

        self.flag_label = QLabel()
        self.flag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flag_path = resource_path("assets/flag.gif")
        
        # Use safe QMovie loader
        self.flag_movie, is_flag_valid = self._create_safe_qmovie(
            flag_path,
            self.flag_label,
            "Processing..."
        )
        
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(subtitle_label)
        layout.addSpacing(30)
        layout.addWidget(self.flag_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        loading_screen.setLayout(layout)
        self.stack.addWidget(loading_screen)
        self.stack.setCurrentWidget(loading_screen)
        
        # Start the movie if valid
        if is_flag_valid:
            self.flag_movie.start()

        # Start scraping after short delay
        QTimer.singleShot(500, self.scrape_violations)

    def scrape_violations(self):
        try:
            result = scrape_violations(start_date=self.start_date)
            self.handle_scrape_result(result)
        except Exception as e:
            print(f"Error during scraping: {e}")
            self.handle_scrape_result(pd.DataFrame())  # Empty DataFrame for failure

    def handle_scrape_result(self, result):
        if result.empty:
            self.show_failure_screen()
        else:
            try:
                generate_excel(result)
                self.show_success_screen()
            except Exception as e:
                print(f"Error generating Excel: {e}")
                self.show_failure_screen()

    def show_success_screen(self):
        """Show Mazel Tov after success"""
        success_screen = QWidget()
        layout = QVBoxLayout()

        self.success_label = QLabel()
        self.success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gif_path = resource_path("assets/mazeltov.gif")

        # Use safe QMovie loader
        self.success_movie, is_success_valid = self._create_safe_qmovie(
            gif_path,
            self.success_label,
            "Mazel Tov!"
        )

        layout.addStretch()
        layout.addWidget(self.success_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        success_screen.setLayout(layout)
        self.stack.addWidget(success_screen)
        self.stack.setCurrentWidget(success_screen)

        # After 1 playthrough plus 500ms delay, show final success screen
        if is_success_valid:
            self.success_movie.start()
            self.success_movie.frameChanged.connect(self.check_success_complete)
            # Add delay by using a global variable
            self.completed_frames = 0
        else:
            # If GIF is missing or invalid, show final success screen after a delay
            QTimer.singleShot(1000, self.show_final_success_screen)
    
    def check_success_complete(self):
        total_frames = self.success_movie.frameCount()
        current_frame = self.success_movie.currentFrameNumber()
        
        # Check if we've completed one full playthrough
        if current_frame == total_frames - 1:
            self.completed_frames += 1
            
            # If we've seen the complete animation once, wait a bit longer then proceed
            if self.completed_frames >= 1:
                # Stop the movie after 500ms delay
                QTimer.singleShot(500, self.stop_success_and_proceed)

    def stop_success_and_proceed(self):
        """Stop the success movie and proceed to final screen"""
        if hasattr(self, 'success_movie') and self.success_movie:
            self.success_movie.stop()
        self.show_final_success_screen()

    def show_final_success_screen(self):
        """Show final success screen with elegant design"""
        screen = QWidget()
        layout = QVBoxLayout()
        
        # Title with Jewish font
        title_label = QLabel("Mazel Tov!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet(f"color: {self.israeli_blue}; font-size: 32px;")
        
        # Subtitle
        subtitle_label = QLabel("Violation report generated successfully")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(self.subtitle_font)
        
        # File info with clean styling
        file_label = QLabel("Report saved to:")
        file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_label.setFont(QFont("Arial", 12))
        
        file_path = QLabel(self.output_file_path)
        file_path.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_path.setFont(QFont("Arial", 11))
        file_path.setStyleSheet("color: #555555; font-style: italic;")
        file_path.setWordWrap(True)
        
        # Action buttons with alternating blue/white styling
        view_button = self.create_styled_button("View Report", 200, 50, 
                                               False,  # Blue button 
                                               self.view_excel)
        
        home_button = self.create_styled_button("Return Home", 180, 50, 
                                               True,   # White button
                                               self.restart_app)
        
        exit_button = self.create_styled_button("Exit", 180, 50, 
                                              False,  # Blue button
                                              self.close)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(home_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(exit_button)
        
        # Main layout with elegant spacing
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(20)
        layout.addWidget(subtitle_label)
        layout.addSpacing(15)
        layout.addWidget(file_label)
        layout.addWidget(file_path)
        layout.addSpacing(30)
        layout.addWidget(view_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        screen.setLayout(layout)
        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)

    def show_failure_screen(self):
        """Show Oy Vey after failure"""
        fail_screen = QWidget()
        layout = QVBoxLayout()

        self.fail_label = QLabel()
        self.fail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gif_path = resource_path("assets/oyvey.gif")

        # Use safe QMovie loader
        self.fail_movie, is_fail_valid = self._create_safe_qmovie(
            gif_path,
            self.fail_label,
            "Oy Vey!"
        )

        layout.addStretch()
        layout.addWidget(self.fail_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        fail_screen.setLayout(layout)
        self.stack.addWidget(fail_screen)
        self.stack.setCurrentWidget(fail_screen)

        # After 1 playthrough plus 500ms delay, show final failure screen
        if is_fail_valid:
            self.fail_movie.start()
            self.fail_movie.frameChanged.connect(self.check_failure_complete)
            # Add delay by using a global variable
            self.completed_frames_failure = 0
        else:
            # If GIF is missing or invalid, show final failure screen after a delay
            QTimer.singleShot(1000, self.show_final_failure_screen)

    def check_failure_complete(self):
        total_frames = self.fail_movie.frameCount()
        current_frame = self.fail_movie.currentFrameNumber()
        
        # Check if we've completed one full playthrough
        if current_frame == total_frames - 1:
            self.completed_frames_failure += 1
            
            # If we've seen the complete animation once, wait a bit longer then proceed
            if self.completed_frames_failure >= 1:
                # Stop the movie after 500ms delay
                QTimer.singleShot(500, self.stop_failure_and_proceed)

    def stop_failure_and_proceed(self):
        """Stop the failure movie and proceed to final screen"""
        if hasattr(self, 'fail_movie') and self.fail_movie:
            self.fail_movie.stop()
        self.show_final_failure_screen()

    def show_final_failure_screen(self):
        """Show final failure screen with elegant design"""
        screen = QWidget()
        layout = QVBoxLayout()
        
        # Title with Jewish font
        title_label = QLabel("Oy Vey!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet(f"color: {self.israeli_blue}; font-size: 32px;")
        
        # Subtitle
        subtitle_label = QLabel("No building violations were found for the selected dates")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(self.subtitle_font)
        subtitle_label.setWordWrap(True)
        
        # Modern styled buttons with alternating blue/white styling
        home_button = self.create_styled_button("Try Again", 180, 50, 
                                               False,  # Blue button
                                               self.restart_app)
        
        exit_button = self.create_styled_button("Exit", 180, 50, 
                                               True,   # White button
                                               self.close)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(home_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(exit_button)
        
        # Main layout with elegant spacing
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(20)
        layout.addWidget(subtitle_label)
        layout.addSpacing(40)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        screen.setLayout(layout)
        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)

    def restart_app(self):
        self.stack.setCurrentIndex(0)

    def view_excel(self):
        """Open the generated Excel file"""
        if os.path.exists(self.output_file_path):
            try:
                if sys.platform == "win32":
                    os.startfile(self.output_file_path)
                elif sys.platform == "darwin":  # macOS
                    subprocess.Popen(["open", self.output_file_path])
                else:  # Linux
                    subprocess.Popen(["xdg-open", self.output_file_path])
                print(f"Opening Excel file at: {self.output_file_path}")
            except Exception as e:
                print(f"Failed to open Excel file: {e}")
        else:
            print(f"Excel file not found at: {self.output_file_path}")

# Main Execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DOBScraperGUI()
    window.show()
    sys.exit(app.exec())