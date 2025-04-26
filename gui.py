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

class HarmonizedButton(QPushButton):
    """Aesthetically pleasing button with subtle animations and color harmony"""
    def __init__(self, text, color_scheme="blue", parent=None):
        super().__init__(text, parent)
        
        # Define color palettes - more variety, less intense blues
        self.color_schemes = {
            "blue": {
                "primary": "#3a75c4",  # Softer blue
                "hover": "#4b86d5",    # Slightly lighter blue
                "pressed": "#2f64b3",  # Slightly darker blue
                "text": "#ffffff",     # White text
                "shadow": QColor(48, 71, 94, 70)  # Blue-gray shadow, more transparent
            },
            "slate": {
                "primary": "#546e7a",  # Slate gray-blue
                "hover": "#607d8b",    # Lighter slate
                "pressed": "#455a64",  # Darker slate
                "text": "#ffffff",     # White text
                "shadow": QColor(45, 45, 45, 60)  # Dark gray shadow
            },
            "teal": {
                "primary": "#26a69a",  # Teal
                "hover": "#2bbbad",    # Lighter teal
                "pressed": "#00897b",  # Darker teal
                "text": "#ffffff",     # White text
                "shadow": QColor(38, 166, 154, 70)  # Teal shadow
            },
            "sand": {
                "primary": "#d4b483",  # Sand color
                "hover": "#e5c595",    # Lighter sand
                "pressed": "#c3a372",  # Darker sand
                "text": "#3e2723",     # Dark brown text
                "shadow": QColor(150, 136, 112, 60)  # Sand shadow
            }
        }
        
        # Set color scheme
        self.color_scheme = color_scheme if color_scheme in self.color_schemes else "blue"
        self.colors = self.color_schemes[self.color_scheme]
        
        # Set up gradient colors
        self.gradient_top = QColor(self.colors["primary"])
        self.gradient_bottom = QColor(self.colors["primary"]).darker(105)
        
        # Track states
        self._hovered = False
        self._pressed = False
        self.setMouseTracking(True)
        
        # Set up effects
        self.setup_effects()
        
        # Custom styling - use properties, not stylesheet for better performance
        self.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors["text"]};
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                text-align: center;
            }}
        """)
        
    def setup_effects(self):
        """Set up visual effects for the button"""
        # Shadow effect for depth
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(self.colors["shadow"])
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        
    def paintEvent(self, event):
        """Custom painting for gradient background and rounded corners"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate corner radius - responsive to button height
        corner_radius = min(10, self.height() / 4)
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), corner_radius, corner_radius)
        
        # Clip to the rounded rectangle
        painter.setClipPath(path)
        
        # Create gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        
        if self._pressed:
            # Pressed state - darker gradient, flipped
            gradient.setColorAt(0, self.gradient_bottom.darker(110))
            gradient.setColorAt(1, self.gradient_top.darker(110))
        elif self._hovered:
            # Hover state - lighter gradient
            hover_top = self.gradient_top.lighter(107)
            hover_bottom = self.gradient_bottom.lighter(107)
            gradient.setColorAt(0, hover_top)
            gradient.setColorAt(1, hover_bottom)
        else:
            # Normal state - standard gradient
            gradient.setColorAt(0, self.gradient_top)
            gradient.setColorAt(1, self.gradient_bottom)
            
        # Fill with gradient
        painter.fillPath(path, QBrush(gradient))
        
        # Draw subtle inner border
        if not self._pressed:
            border_color = QColor(self.colors["primary"])
            border_color.setAlpha(80)
            pen = QPen(border_color)
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawPath(path)
        
        # Draw text - center aligned
        painter.setPen(QColor(self.colors["text"]))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        
    def enterEvent(self, event):
        """Handle mouse enter with animation"""
        self._hovered = True
        
        # Animate shadow and subtle scale effect
        animations = QParallelAnimationGroup(self)
        
        # Shadow animation
        shadow_anim = QPropertyAnimation(self.shadow, b"blurRadius")
        shadow_anim.setStartValue(10)
        shadow_anim.setEndValue(15)
        shadow_anim.setDuration(180)
        shadow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        animations.addAnimation(shadow_anim)
        
        # Shadow offset animation
        offset_anim = QPropertyAnimation(self.shadow, b"offset")
        offset_anim.setStartValue(QPoint(0, 2))
        offset_anim.setEndValue(QPoint(0, 4))
        offset_anim.setDuration(180)
        offset_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        animations.addAnimation(offset_anim)
        
        # Start animations
        animations.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        
        self.update()  # Repaint with hover state
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave with animation"""
        self._hovered = False
        
        # Animate shadow and scale back to normal
        animations = QParallelAnimationGroup(self)
        
        # Shadow animation
        shadow_anim = QPropertyAnimation(self.shadow, b"blurRadius")
        shadow_anim.setStartValue(15)
        shadow_anim.setEndValue(10)
        shadow_anim.setDuration(180)
        shadow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        animations.addAnimation(shadow_anim)
        
        # Shadow offset animation
        offset_anim = QPropertyAnimation(self.shadow, b"offset")
        offset_anim.setStartValue(QPoint(0, 4))
        offset_anim.setEndValue(QPoint(0, 2))
        offset_anim.setDuration(180)
        offset_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        animations.addAnimation(offset_anim)
        
        # Start animations
        animations.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        
        self.update()  # Repaint with normal state
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse press with animation"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            
            # Quick shadow shrink
            self.shadow.setBlurRadius(5)
            self.shadow.setOffset(0, 1)
            
            self.update()  # Repaint with pressed state
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release with animation"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            
            # Create release ripple effect
            self._create_ripple_at(event.position().x(), event.position().y())
            
            # Return to hover or normal state
            if self._hovered:
                self.shadow.setBlurRadius(15)
                self.shadow.setOffset(0, 4)
            else:
                self.shadow.setBlurRadius(10)
                self.shadow.setOffset(0, 2)
                
            self.update()  # Repaint with normal/hover state
        super().mouseReleaseEvent(event)

    def _create_ripple_at(self, x, y):
        """Create a ripple effect at the specified position"""
        # Create ripple widget as child
        ripple = QWidget(self)
        ripple.setGeometry(0, 0, 10, 10)
        ripple.setStyleSheet("background-color: rgba(255, 255, 255, 120); border-radius: 5px;")
        ripple.show()
        
        # Center ripple at click position
        ripple.move(int(x - 5), int(y - 5))
        
        # Make it transparent
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.7)
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
        
        # Animate opacity
        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setStartValue(0.7)
        fade_anim.setEndValue(0.0)
        
        # Create animation group
        group = QParallelAnimationGroup(self)
        group.addAnimation(size_anim)
        group.addAnimation(fade_anim)
        group.setDuration(400)
        group.setEasingCurve(QEasingCurve.Type.OutQuad)
        
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

        # Color scheme with more variety
        self.primary_color = "#3a75c4"  # Softer blue
        self.accent_color = "#26a69a"   # Teal accent
        self.neutral_color = "#546e7a"  # Slate gray
        self.warm_color = "#d4b483"     # Sand color
        
        # Button color assignments - create visual hierarchy
        self.primary_button_color = "blue"   # Primary actions
        self.secondary_button_color = "teal" # Secondary actions
        self.tertiary_button_color = "slate" # Tertiary actions
        self.special_button_color = "sand"   # Special accent buttons
        
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
        
        # Then check system fonts - FIXED: Use static methods instead
        # In PyQt6, we need to use QFontDatabase.families() to get the list of available system fonts
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

    def create_styled_button(self, text, width=200, height=50, color_scheme=None, connect_to=None):
        """Create an aesthetically pleasing button with visual diversity"""
        # Use provided color scheme or default to primary_button_color
        scheme = color_scheme if color_scheme else self.primary_button_color
        button = HarmonizedButton(text, color_scheme=scheme)
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
        title_label.setStyleSheet(f"color: {self.primary_color};")
        
        # Subtitle
        subtitle_label = QLabel("Building Violation Reports")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(self.subtitle_font)

        # Start button with special styling
        start_button = self.create_styled_button("Start", 220, 60, self.special_button_color, self.show_category_screen)

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
        title_label.setStyleSheet(f"color: {self.primary_color};")
        
        layout.addWidget(title_label)
        layout.addSpacing(30)

        # Category buttons with visual variety
        recent_button = self.create_styled_button("Recent Periods", 250, 60, 
                                                self.primary_button_color, 
                                                self.show_recent_periods)
        
        years_button = self.create_styled_button("Past Years", 250, 60, 
                                                self.secondary_button_color, 
                                                self.show_past_years)
        
        all_button = self.create_styled_button("All Since 2015", 250, 60,
                                              self.special_button_color, 
                                              lambda: self.begin_scraping("2015-01-01"))

        layout.addWidget(recent_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(years_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(all_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        
        # Back button (tertiary style)
        back_button = self.create_styled_button("Back", 120, 40, 
                                              self.tertiary_button_color,
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
        ], "Recent Periods", self.primary_button_color)

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
        ], "Past Years", self.secondary_button_color)

    def show_period_buttons(self, options, title_text, button_color_scheme):
        """Generate dynamic period buttons in a grid layout with visual rhythm"""
        self.period_screen = QWidget()
        main_layout = QVBoxLayout()
        
        # Header
        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet(f"color: {self.primary_color};")
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)
        
        # Grid layout for buttons - 3 columns
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # Add buttons to grid with alternating visual patterns
        for i, (label, days) in enumerate(options):
            # Create subtle visual rhythm by alternating button styles
            row, col = divmod(i, 3)  # 3 columns
            
            # Subtle size variance creates visual interest
            width = 180 + ((i % 3) * 5)  # Slightly vary widths
            
            button = self.create_styled_button(
                label, width, 50, 
                button_color_scheme,
                lambda checked, d=days: self.calculate_start_date(d)
            )
            
            grid_layout.addWidget(button, row, col)
        
        # Back button (tertiary style)
        back_button = self.create_styled_button(
            "Back", 120, 40, 
            self.tertiary_button_color,
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
        title_label.setStyleSheet(f"color: {self.primary_color};")
        
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
        title_label.setStyleSheet(f"color: {self.primary_color}; font-size: 32px;")
        
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
        
        # Action buttons with visual variety
        view_button = self.create_styled_button("View Report", 200, 50, 
                                               self.special_button_color, 
                                               self.view_excel)
        
        home_button = self.create_styled_button("Return Home", 180, 50, 
                                               self.primary_button_color, 
                                               self.restart_app)
        
        exit_button = self.create_styled_button("Exit", 180, 50, 
                                              self.tertiary_button_color, 
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
        title_label.setStyleSheet(f"color: {self.primary_color}; font-size: 32px;")
        
        # Subtitle
        subtitle_label = QLabel("No building violations were found for the selected dates")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(self.subtitle_font)
        subtitle_label.setWordWrap(True)
        
        # Modern styled buttons with visual variety
        home_button = self.create_styled_button("Try Again", 180, 50, 
                                               self.primary_button_color, 
                                               self.restart_app)
        
        exit_button = self.create_styled_button("Exit", 180, 50, 
                                               self.tertiary_button_color, 
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