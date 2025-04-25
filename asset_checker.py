# asset_checker.py
import os

required_assets = [
    "assets/flag.gif",
    "assets/mazeltov.gif",
    "assets/oyvey.gif",
    "assets/fonts/jewish.ttf"
]

def check_assets():
    print("\n🔎 Checking assets...\n")
    missing = []
    correct = 0

    for asset in required_assets:
        if os.path.exists(asset):
            correct += 1
        else:
            missing.append(asset)

    if correct > 0:
        print(f"✅ Correct files: {correct}")

    if missing:
        print(f"❌ Missing files: {missing}")
    else:
        print("\n🎯 All required assets are present!\n")
    
    print("\n✅ Asset Check Complete.")

if __name__ == "__main__":
    check_assets()
