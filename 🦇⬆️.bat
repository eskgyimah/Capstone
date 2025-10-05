@echo off
REM Push to GitHub - COVID-19 Bibliometric Analysis Framework
REM Author: Edward Solomon Kweku Gyimah

echo.
echo ========================================
echo   Git Push Script
echo   UCC Capstone Project
echo ========================================
echo.

REM Check if there are changes to commit
git status --short
if %errorlevel% neq 0 (
    echo [ERROR] Git not initialized or repository not found!
    pause
    exit /b 1
)

echo.
echo Checking for changes...
git diff-index --quiet HEAD --
if %errorlevel% equ 0 (
    echo [INFO] No changes to commit
    echo.
    echo Checking if push is needed...
    git status | findstr /C:"Your branch is ahead" >nul
    if %errorlevel% equ 0 (
        echo [INFO] Local commits found, pushing to remote...
        goto :push
    ) else (
        echo [INFO] Everything is up to date!
        pause
        exit /b 0
    )
)

echo.
echo Changes detected:
git status --short
echo.

REM Add all changes
echo Adding changes...
git add .

REM Get commit message from user
echo.
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" (
    set commit_msg=Update: Academic production improvements
)

REM Commit changes
echo.
echo Committing with message: %commit_msg%
git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo [ERROR] Commit failed!
    pause
    exit /b 1
)

:push
REM Push to remote
echo.
echo Pushing to GitHub...
git push
if %errorlevel% neq 0 (
    echo [WARNING] Regular push failed. Trying force push...
    echo.
    choice /C YN /M "Force push (WARNING: This will overwrite remote)? "
    if errorlevel 2 goto :cancel
    git push --force
    if %errorlevel% neq 0 (
        echo [ERROR] Force push failed!
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Push completed successfully!
echo ========================================
echo.
git log --oneline -3
echo.
pause
exit /b 0

:cancel
echo.
echo [INFO] Push cancelled by user
pause
exit /b 0
