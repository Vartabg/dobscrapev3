# Copilot: Summarize what this file does and why it may have been replaced or archived.


from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt
import sys

class MinimalDOBGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal DOB GUI Test")
        self.setFixedSize(800, 600)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        start_btn = QPushButton("Start")
        start_btn.setFixedSize(200, 200)
        start_btn.setStyleSheet("""
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

        layout.addWidget(start_btn)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MinimalDOBGui()
    win.show()
    sys.exit(app.exec())
