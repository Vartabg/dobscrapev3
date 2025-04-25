import os
import difflib

# Required correct asset names
REQUIRED_ASSETS = [
    'flag.gif',
    'mazeltov.gif',
    'oyvey.gif',
    'fonts/jewish.ttf'
]

ASSETS_FOLDER = "assets"
THRESHOLD = 0.7  # 70% similarity required to auto-suggest rename

def find_closest_match(filename, candidates):
    matches = difflib.get_close_matches(filename, candidates, n=1, cutoff=THRESHOLD)
    return matches[0] if matches else None

def main():
    print("\n🔎 Running Smart Auto-Renamer...\n")

    if not os.path.exists(ASSETS_FOLDER):
        print(f"❌ Assets folder '{ASSETS_FOLDER}' not found.")
        return

    existing_files = []
    for root, _, files in os.walk(ASSETS_FOLDER):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), ASSETS_FOLDER)
            existing_files.append(rel_path.replace("\\", "/"))

    missing = []
    rename_suggestions = {}

    for required_file in REQUIRED_ASSETS:
        if required_file not in existing_files:
            closest = find_closest_match(required_file, existing_files)
            if closest:
                rename_suggestions[closest] = required_file
            else:
                missing.append(required_file)

    if rename_suggestions:
        print("✅ Suggested renames:")
        for src, dst in rename_suggestions.items():
            print(f"- {src} ➡️ {dst}")

        approve = input("\nDo you want to automatically rename these files? (y/n): ").strip().lower()
        if approve == 'y':
            for src, dst in rename_suggestions.items():
                src_path = os.path.join(ASSETS_FOLDER, src)
                dst_path = os.path.join(ASSETS_FOLDER, dst)
                dst_dir = os.path.dirname(dst_path)
                os.makedirs(dst_dir, exist_ok=True)
                os.rename(src_path, dst_path)
                print(f"✔️ Renamed {src} ➔ {dst}")
            print("\n🎉 All files renamed successfully!")
        else:
            print("⚡ Rename canceled by user.")
    else:
        print("✅ No renames needed.")

    if missing:
        print("\n⚠️ Still missing files:")
        for file in missing:
            print(f"- {file}")

    print("\n🏁 Smart Auto-Renamer complete.\n")

if __name__ == "__main__":
    main()
