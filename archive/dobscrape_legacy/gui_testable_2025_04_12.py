
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt
import sys

class DOBTestableGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOB GUI - Testable Layout")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: white;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.init_ui()

    def init_ui(self):
        self.clear_layout()

        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(200, 200)
        self.start_button.setStyleSheet("""
            QPushButton {
                border-radius: 100px;
                background-color: white;
                color: #002B7F;
                font-size: 24pt;
                border: 2px solid #002B7F;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.start_button.clicked.connect(self.show_date_options)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addStretch()
        layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.main_layout.addWidget(container)

    def show_date_options(self):
        self.clear_layout()

        options = [
            "Last 30 Days", "Last 3 Months", "Last 6 Months",
            "Past Year", "Past 2 Years", "All Since 2020"
        ]

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        for label in options:
            btn = QPushButton(label)
            btn.setFixedSize(300, 50)
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 25px;
                    background-color: white;
                    font-size: 16pt;
                    border: 1px solid #ccc;
                }
                QPushButton:hover {
                    background-color: #f8f8f8;
                }
            """)
            layout.addWidget(btn)

        self.main_layout.addWidget(container)

    def clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DOBTestableGUI()
    window.show()
    sys.exit(app.exec())
