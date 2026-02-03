# ============================================================
# NADAKKI - GitHub Setup & Multi-PC Sync Guide
# ============================================================

# ============================================================
# STEP 1: First-time GitHub Setup (run ONCE on your main PC)
# ============================================================

# 1a. Create repo on GitHub
#     Go to: https://github.com/new
#     Name: nadakki-google-ads-mvp
#     Private: Yes
#     DO NOT add README (we already have one)
#     Click "Create repository"

# 1b. Initialize and push (PowerShell)

cd C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\nadakki-google-ads-mvp

# First apply the latest zip
$env:DATABASE_URL = ""
Remove-Item "C:\Users\cesar\Downloads\temp-nadakki" -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive -Path "C:\Users\cesar\Downloads\nadakki-google-ads-mvp-day7-FINAL.zip" -DestinationPath "C:\Users\cesar\Downloads\temp-nadakki\" -Force
Copy-Item -Path "C:\Users\cesar\Downloads\temp-nadakki\nadakki-google-ads-mvp\*" -Destination "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\nadakki-google-ads-mvp\" -Recurse -Force

# Verify the fix is applied
python -c "with open('tests/test_all.py','rb') as f: d=f.read(); print(f'Non-ASCII: {sum(1 for b in d if b>127)}')"
# Should print: Non-ASCII: 0

# Run tests to confirm
python main.py
# Should print: ALL DAYS 1-7 TESTS PASSED [OK]

# Initialize git
git init
git add .
git commit -m "NADAKKI Google Ads MVP - Day 7 Final (19 components, 64 tests, 43 endpoints)"

# Add remote (replace YOUR_USER with your GitHub username)
git remote add origin https://github.com/YOUR_USER/nadakki-google-ads-mvp.git
git branch -M main
git push -u origin main


# ============================================================
# STEP 2: Clone on a DIFFERENT PC
# ============================================================

# On any new computer:
git clone https://github.com/YOUR_USER/nadakki-google-ads-mvp.git
cd nadakki-google-ads-mvp
pip install -r requirements.txt
python main.py          # Run tests
uvicorn main:app --reload --port 8000   # Start API


# ============================================================
# STEP 3: Daily Workflow (any PC)
# ============================================================

# Pull latest changes
git pull origin main

# ... make changes ...

# Push changes
git add .
git commit -m "Description of changes"
git push origin main


# ============================================================
# STEP 4: Start API Server
# ============================================================

cd C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\nadakki-google-ads-mvp
pip install fastapi uvicorn
uvicorn main:app --reload --port 8000

# API Docs: http://localhost:8000/docs
# Health:   http://localhost:8000/health
