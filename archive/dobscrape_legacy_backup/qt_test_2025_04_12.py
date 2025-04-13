
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
import sys

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("PyQt Test")
window.setFixedSize(400, 300)

layout = QVBoxLayout()
btn = QPushButton("If you can see this, Qt works!")
layout.addWidget(btn)

window.setLayout(layout)
window.show()

sys.exit(app.exec())
