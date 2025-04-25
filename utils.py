import os
import sys
import pandas as pd

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
        data.to_excel(output_path, index=False)
        if hasattr(sys, 'DEBUG') and sys.DEBUG:
            print(f"✔️ Results saved to: {output_path}")
        return True
    except Exception as e:
        if hasattr(sys, 'DEBUG') and sys.DEBUG:
            print(f"❌ Failed to generate Excel: {e}")
        return False