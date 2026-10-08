@echo off
REM =====================================================================
REM  Jyotisha publish — one-click rebuild & push.
REM
REM  Workflow:
REM    1. You edit Classification_for_Horoscope_Analysis_v7_1.xlsx and save.
REM    2. In File Explorer, open:
REM         C:\Users\bp_gi\OneDrive\Documents\GitHub\Vedic_horoscope
REM       Double-click this file (publish.bat).
REM    3. This script runs the Python extractors (scripts\build_data.py and
REM       build_session23.py), commits the regenerated index.html and
REM       session23_rules.json, and pushes to GitHub. GitHub Pages republishes
REM       within ~1 minute at https://girishbp-wq.github.io/Vedic_horoscope/
REM
REM  (The Excel "PUBLISH TO GITHUB" button only works when the workbook is
REM   opened in Desktop Excel, not Excel Online. Running this .bat
REM   directly from File Explorer always works.)
REM
REM  Requirements on this machine:
REM    - Python 3 on PATH         (python --version)
REM    - openpyxl                 (pip install openpyxl)
REM    - git configured to push   (git push works from this folder)
REM =====================================================================
setlocal
cd /d "%~dp0"

echo.
echo === Jyotisha publish ===
echo.

REM Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found on PATH. Install Python 3 from python.org
    echo         and re-run.
    pause
    exit /b 1
)

REM Ensure openpyxl is available (cheap check; install if missing)
python -c "import openpyxl" 2>nul
if errorlevel 1 (
    echo openpyxl not installed. Installing...
    python -m pip install --user --quiet openpyxl
    if errorlevel 1 (
        echo [ERROR] Could not install openpyxl. Run manually:
        echo         pip install openpyxl
        pause
        exit /b 1
    )
)

REM Rebuild index.html from the workbook
echo [1/5] Rebuilding index.html from the workbook...
python scripts\build_data.py
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. See message above.
    pause
    exit /b 1
)

REM Session 23 (bhava classes, prediction layers, dasha roles): the S23_ sheets of the same workbook
echo.
echo [2/5] Rebuilding the Session 23 data from the S23_ sheets...
python build_session23.py
if errorlevel 1 (
    echo.
    echo [ERROR] Session 23 build failed. See message above.
    pause
    exit /b 1
)

REM Stage only the file that goes into git
echo.
echo [3/5] Staging index.html and session23_rules.json...
git add index.html session23_rules.json

REM If nothing changed, stop here with a friendly note
git diff --cached --quiet
if %errorlevel%==0 (
    echo.
    echo No changes to publish — the workbook produced the same index.html.
    echo Nothing was committed.
    pause
    exit /b 0
)

echo.
echo [4/5] Committing...
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set DT=%%a
set STAMP=%DT:~0,4%-%DT:~4,2%-%DT:~6,2% %DT:~8,2%:%DT:~10,2%
git commit -m "Rebuild index.html from workbook (%STAMP%)"
if errorlevel 1 (
    echo [ERROR] Commit failed. See message above.
    pause
    exit /b 1
)

echo.
echo [5/5] Pushing to GitHub...
git push
if errorlevel 1 (
    echo.
    echo [ERROR] Push failed. See message above.
    echo         Common causes: no network, auth not configured, protected branch.
    pause
    exit /b 1
)

echo.
echo === DONE ===
echo The horoscope page will republish on GitHub Pages within ~1 minute.
echo.
pause
