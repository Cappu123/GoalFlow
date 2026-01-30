@echo off
echo Starting GoalFlow Backend...
cd /d %~dp0

REM Navigate to backend directory
cd backend 

REM Activate virtual environment
call .venv\Scripts\activate

REM Navigate to the backend directory
cd app

REM Start the backend server
echo Launching the GoalFlow backend server...
uv run main.py