# 🤖 AI Task Force Briefing: DOBScraper v1.0 (April 12, 2025)

> **Mission**: Complete and ship the DOBScraper product by coordinating multiple AI agents.  
> **Owner**: Garo Vartabedian  
> **AI Project Director**: ChatGPT  
> **Status**: Code freeze and packaging in progress

---

## ✅ ChatGPT (Lead Engineer / Project Director)

**Scope:**
- Finalize `gui.py` with proper animations, `resource_path`, and loop logic
- Handle PyInstaller spec creation and EXE packaging
- Manage naming conventions (`DOBScraperGUI`, `gui.py`, `violations.xlsx`)
- Organize `/archive/` and maintain `version_log.txt`
- Coordinate across all AI contributors

---

## 📄 Claude — Documentation / Archive Historian

**Task**:
- For each file in `/archive/dobscrape_legacy/`, create a `summary.md` with:
  - What it attempted
  - What AI/model created it (if known)
  - Why it was replaced
- Update `version_log.txt` with milestone history
- Keep formatting clean and human-readable

---

## 🧪 Gemini — UX QA Engineer

**Task**:
- Load and test `gui.py` to verify:
  - ✅ Start button triggers date screen
  - ✅ Flag GIF plays on loading screen
  - ✅ Mazel Tov GIF loops *exactly 3 times* using `frameChanged`
  - ✅ View Results & Home buttons appear only after animation
  - ✅ Oy Vey screen displays on empty fetch
  - ✅ All buttons follow UI specs (radius, font, color)
- Reference the latest `AI_README.md` or `AI_README_v2.md`

---

## 🧰 GitHub Copilot — Logic Assistant

**Task**:
- Assist in:
  - `violations_utils.py`
  - `generate_insights.py`
  - `dashboard_export.py`
- Only offer code completion and optimization
- DO NOT touch:
  - `gui.py`
  - `DOBScraper.spec`
  - Any EXE packaging or assets

---

## 📊 Abacus.ai — Data Intelligence

**Task**:
- Analyze `violations.xlsx` and generate:
  - `Insights` tab with:
    - Top 5 streets with repeat violations
    - Violation type & borough breakdown
    - Unresolved violations (oldest first)
    - Flags for "hot leads" based on age and recurrence
- Output to: `violations_with_insights.xlsx`
- Optional: Provide JSON of insights for future frontend use

---

## 📋 Garo's Deployment Checklist

| Task | Action |
|------|--------|
| ✅ Claude | Paste directive, upload `/archive` |
| ✅ Gemini | Paste UX checklist, upload `gui.py` |
| ✅ Copilot | Use in VSCode only, helper scripts only |
| ✅ Abacus | Upload `violations.xlsx`, paste directive |
| ✅ ChatGPT | Build EXE, archive, tag as v1.0 |

---

## 🧠 Final Note

This is a **collaborative, ego-free AI team effort**.  
Each model works independently but communicates through these unified naming and structure rules.

Let’s deliver this for the client — no delays, no confusion, just clean execution.