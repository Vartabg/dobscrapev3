# asset_checker.py

import os
import hashlib
import shutil

# === Official Asset Manifest ===
ASSETS_MANIFEST = {
    "flag.gif": "expected_hash_here",
    "mazeltov.gif": "expected_hash_here",
    "oyvey.gif": "expected_hash_here",
    "fonts/jewish.ttf": "expected_hash_here"
}

ASSETS_FOLDER = "assets"

# === Helper Functions ===

def calculate_sha256(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# === Checker ===

def check_assets():
    print("\n🔎 Checking assets...\n")
    found_files = []
    missing_files = []
    wrong_files = []
    extra_files = []

    for filename, expected_hash in ASSETS_MANIFEST.items():
        path = os.path.join(ASSETS_FOLDER, filename)
        if not os.path.exists(path):
            missing_files.append(filename)
        else:
            found_files.append(filename)
            # You can optionally compare hashes if needed

    # Detect extra files
    actual_files = []
    for root, dirs, files in os.walk(ASSETS_FOLDER):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), ASSETS_FOLDER)
            actual_files.append(rel_path)

    for file in actual_files:
        if file not in ASSETS_MANIFEST:
            extra_files.append(file)

    # Summary
    print(f"✅ Correct files: {len(found_files)}")
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
    if extra_files:
        print(f"❌ Extra files: {extra_files}")

    return missing_files, extra_files

# === Safe Renamer ===

def safe_rename(extra_files):
    if not extra_files:
        print("\n✅ No files to rename.")
        return

    print("\n✨ Safe Rename Mode: ")

    for wrong_file in extra_files:
        new_name = input(f"Rename '{wrong_file}' to what? (Leave blank to skip) > ")
        if new_name:
            old_path = os.path.join(ASSETS_FOLDER, wrong_file)
            new_path = os.path.join(ASSETS_FOLDER, new_name)

            if os.path.exists(new_path):
                print(f"⚠️ Target {new_name} already exists. Skipping.")
            else:
                try:
                    shutil.move(old_path, new_path)
                    print(f"✅ Renamed {wrong_file} -> {new_name}")
                except Exception as e:
                    print(f"❌ Failed to rename {wrong_file}: {e}")

# === Main ===

if __name__ == "__main__":
    missing, extra = check_assets()

    if extra:
        answer = input("\nWould you like to safely rename extra files now? (y/n) > ").strip().lower()
        if answer == 'y':
            safe_rename(extra)

    print("\n✅ Asset Check Complete.")
