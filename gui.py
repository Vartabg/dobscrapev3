import sys
import os
import subprocess
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QMovie, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller --onefile """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# The rest of your gui.py would follow... we’ll simulate only the patch logic here.
# Normally this would be a full file with all logic from the previously working GUI, 
# just with all asset loads replaced to use resource_path().