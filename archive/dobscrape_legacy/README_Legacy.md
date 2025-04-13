# DOBScraper Legacy File Summaries

This document provides a centralized overview of the legacy files archived in `archive/dobscrape_legacy/` as part of the DOBScraper v1.0 consolidation process. Each file listed here has been preserved for historical reference and includes an accompanying `.md` summary in `archive/dobscrape_legacy/summaries/`.

---

## 🔍 What’s in this Archive?

This folder contains:

- Legacy `.py` and `.spec` files used during earlier phases of development.
- Experimental GUIs, scraper prototypes, PyInstaller build specs, test harnesses, and auto-generated hooks.
- Code authored by multiple AI assistants across different tools (ChatGPT, Claude, Copilot, etc.).
- Annotated metadata and backup copies of each legacy file.
- Git history retained to trace who contributed what and why replacements were made.

---

## 📁 Summary Index

Each legacy file listed below links to its human- or AI-generated summary stored in the `summaries/` folder:

| Filename                        | Summary File                                      | Description                                               |
|--------------------------------|--------------------------------------------------|-----------------------------------------------------------|
| `gui_testable_2025_04_12.py`   | `summaries/gui_testable_2025_04_12.md`           | Early GUI concept with test harness; deprecated by v1.0.  |
| `gui_embed_assets_2025_04_12.spec` | `summaries/gui_embed_assets_2025_04_12.md`  | Custom PyInstaller spec file to embed assets directly.    |
| `main_2025_04_12.py`           | `summaries/main_2025_04_12.md`                   | An early script to launch scraper + GUI; replaced.        |
| `test_summary_2025_04_12.py`   | `summaries/test_summary_2025_04_12.md`           | Testing logic for `generate_summary_statistics()`         |
| `Mr4InARow_2025_04_12.spec`    | `summaries/Mr4InARow_2025_04_12.md`              | Original build spec for “Mr. 4 in a Row” GUI prototype.   |
| `hook-PyQt6.QtTest_2025_04_12.py` | `summaries/hook-PyQt6.QtTest_2025_04_12.md`  | Auto-generated PyInstaller hook; no longer used.          |

> ⚠️ For the full list of over 800 legacy files and their summaries, browse the `summaries/` folder directly or search by filename using your IDE.

---

## 📜 How Summaries Were Created

- Annotated via PowerShell using a Copilot-assisted script.
- GitHub Copilot generated `.md` summaries using heuristic analysis.
- File timestamps, commit authorship, and naming patterns were preserved.
- Final summaries committed on 2025-04-12 via commit `257276a`.

---

## 🔁 Why Keep Legacy Code?

We retain legacy files to:

- Preserve audit trails of previous attempts and designs.
- Learn from deprecated patterns or broken implementations.
- Reference structure and logic that influenced final solutions.
- Demonstrate iterative collaboration across AI systems.

---

## 🧠 Related Files

- `version_log.txt`: Documents key milestones in DOBScraper development.
- `annotate_legacy_files.ps1`: PowerShell script used to insert Copilot annotation headers.
- `.gitignore`: Configured to **include** archived code.

---

## 🤝 AI Collaboration Credits

| Role                | Contributor            |
|---------------------|------------------------|
| Lead Engineer        | ChatGPT                |
| GUI Refactorist      | Claude                 |
| Summary Generator    | GitHub Copilot         |
| Directory Architect  | Vart Vartabedian       |

---

## ✅ How to Contribute a Summary

If you encounter an unlisted `.py` file:

1. Write a short summary describing its purpose and history.
2. Save it as `summaries/{original_filename}.md`.
3. Commit with message: `"Add legacy summary for {filename}"`.

Let’s keep it clean and documented.

---

📁 **This archive is frozen as of v1.0.0.** For current builds, use `/projects/dobscrape`.

