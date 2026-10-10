@echo off
REM =====================================================================
REM  Jyotisha publish - one-click rebuild & push.
REM
REM  Workflow:
REM    1. You edit Classification_for_Horoscope_Analysis_v7_1.xlsx and save.
REM    2. In File Explorer, open:
REM         C:\Users\bp_gi\OneDrive\Documents\GitHub\Vedic_horoscope
REM       Double-click this file (publish.bat).
REM    3. This script checks that the folder is on the main branch, pulls the
REM       latest main from GitHub, checks the S23_ sheets, runs the Python extractors
REM       (scripts\build_data.py and build_session23.py), commits ONLY the
REM       regenerated index.html and session23_rules.json, and pushes to
REM       GitHub. GitHub Pages republishes within ~1 minute at
REM       https://girishbp-wq.github.io/Vedic_horoscope/
REM       If an earlier run committed but could not push, running it again
REM       pushes that commit.
REM
REM  (The Excel "PUBLISH TO GITHUB" button only works when the workbook is
REM   opened in Desktop Excel, not Excel Online. Running this .bat
REM   directly from File Explorer always works.)
REM
REM  Requirements on this machine:
REM    - Python 3                 (python --version, or py --version)
REM    - openpyxl                 (installed by this script if missing)
REM    - git configured to push   (git push works from this folder)
REM =====================================================================

REM Step 0 pulls from GitHub and may replace this very file, and cmd reads a running batch
REM file line by line. So run from a copy in %TEMP%, working in this folder (passed as %2).
if /i not "%~1"=="--from-copy" (
    copy /y "%~f0" "%TEMP%\jyotisha_publish.bat" >nul
    call "%TEMP%\jyotisha_publish.bat" --from-copy "%~dp0."
    exit /b
)
setlocal
cd /d "%~2"

echo.
echo === Jyotisha publish ===
echo.

REM Find a Python that actually runs: Windows has a "python" shortcut to the Microsoft Store even
REM when no Python is installed, so finding the command proves nothing. python.org also installs "py".
set "PY="
python -c "import sys" >nul 2>nul
if not errorlevel 1 set "PY=python"
if not defined PY (
    py -3 -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PY=py -3"
)
if not defined PY (
    echo [ERROR] Python 3 was not found on this PC.
    echo         Install it from https://www.python.org/downloads/ and on the first screen
    echo         tick "Add python.exe to PATH". Then close this window and run publish.bat again.
    goto :fail
)

REM Ensure openpyxl is available (cheap check; install if missing)
%PY% -c "import openpyxl" 2>nul
if errorlevel 1 (
    echo openpyxl not installed. Installing...
    %PY% -m pip install --user --quiet openpyxl
    if errorlevel 1 (
        echo [ERROR] Could not install openpyxl. Run manually:
        echo         %PY% -m pip install openpyxl
        goto :fail
    )
)

REM GitHub Pages publishes the main branch: never publish from another branch
set "BRANCH="
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set "BRANCH=%%b"
if /i not "%BRANCH%"=="main" (
    echo [ERROR] This folder is on branch "%BRANCH%", not main.
    echo         In GitHub Desktop choose Current branch: main, then run publish.bat again.
    goto :fail
)

REM Start from the latest main, so the push is not rejected later
echo [0/5] Fetching the latest main from GitHub...
git pull --ff-only
if errorlevel 1 (
    echo.
    echo [ERROR] Could not bring main up to date with GitHub.
    echo         Common causes: no network, or local commits/changes that clash.
    echo         Open GitHub Desktop, click Pull origin, then run publish.bat again.
    goto :fail
)

REM Check the Session 23 sheets before anything is rebuilt, so a typo there leaves index.html untouched
echo.
echo [1/5] Checking the Session 23 sheets, then rebuilding index.html from the workbook...
%PY% build_session23.py --check
if errorlevel 1 (
    echo.
    echo [ERROR] The Session 23 sheets need fixing - nothing was rebuilt or published.
    echo         Fix the cells listed above in the workbook, save, and run publish.bat again.
    goto :fail
)
%PY% scripts\build_data.py
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. See message above.
    goto :fail
)

REM Session 23 (bhava classes, prediction layers, dasha roles): the S23_ sheets of the same workbook
echo.
echo [2/5] Rebuilding the Session 23 data from the S23_ sheets...
%PY% build_session23.py
if errorlevel 1 (
    echo.
    echo [ERROR] Session 23 build failed - nothing was published. Fix the cells
    echo         listed above in the workbook, save, and run publish.bat again.
    goto :fail
)

REM Stage only the files this script produces
echo.
echo [3/5] Staging index.html and session23_rules.json...
git add index.html session23_rules.json
git diff --cached --quiet -- index.html session23_rules.json
if not errorlevel 1 goto :nochange

echo.
echo [4/5] Committing...
set "STAMP="
for /f "delims=" %%a in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-ddTHH:mm"') do set "STAMP=%%a"
git commit -m "Rebuild index.html from workbook (%STAMP%)" -- index.html session23_rules.json
if errorlevel 1 (
    echo [ERROR] Commit failed. See message above.
    goto :fail
)
goto :push

:nochange
REM Nothing new to commit - but an earlier commit may still be waiting to be pushed
set "AHEAD=0"
for /f %%n in ('git rev-list --count @{u}..HEAD 2^>nul') do set "AHEAD=%%n"
if "%AHEAD%"=="0" (
    echo.
    echo No changes to publish - the workbook produced the same index.html.
    echo Nothing was committed.
    echo.
    pause
    exit /b 0
)
echo.
echo No new changes, but %AHEAD% earlier commit(s) have not reached GitHub yet.

:push
echo.
echo [5/5] Pushing to GitHub...
git push
if errorlevel 1 (
    echo.
    echo [ERROR] Push failed. See message above.
    echo         Common causes: no network, auth not configured, protected branch.
    echo         Run publish.bat again once fixed - it pushes the waiting commit.
    goto :fail
)

echo.
echo === DONE ===
echo The horoscope page will republish on GitHub Pages within ~1 minute.
echo.
pause
exit /b 0

:fail
echo.
pause
exit /b 1
