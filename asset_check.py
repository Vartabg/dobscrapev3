import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller compatibility"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def check_asset(path):
    full_path = resource_path(path)
    exists = os.path.exists(full_path)
    print(f"Checking: {path}")
    print(f"Full path: {full_path}")
    print(f"Exists: {'✓' if exists else '✗'}")
    print("-" * 50)
    return exists

if __name__ == "__main__":
    print("\n=== DOBScraper Asset Checker ===\n")
    
    # Check if assets folder exists
    assets_dir = resource_path("assets")
    print(f"Assets directory: {assets_dir}")
    print(f"Exists: {'✓' if os.path.exists(assets_dir) else '✗'}")
    print("-" * 50)
    
    # Check required GIFs
    gifs_ok = all([
        check_asset("assets/flag.gif"),
        check_asset("assets/mazeltov.gif"),
        check_asset("assets/oyvey.gif")
    ])
    
    # Check font
    font_ok = check_asset("assets/fonts/jewish.ttf")
    
    print("\n=== Summary ===")
    print(f"GIFs status: {'✓ All good' if gifs_ok else '✗ Missing files'}")
    print(f"Font status: {'✓ Good' if font_ok else '✗ Missing'}")
    
    if not gifs_ok or not font_ok:
        print("\n⚠️ There are missing assets that will prevent the app from working properly.")
        print("Please make sure all files are in the correct location.")
    else:
        print("\n✅ All assets are in place! If the app still doesn't work,")
        print("the issue may be elsewhere.")
