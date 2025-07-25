@echo off
REM 2025 Hakka Hackathon Project Start Script for Windows
REM This script starts both frontend and backend services

echo 🚀 Starting 2025 Hakka Hackathon Project...

REM Check if required directories exist
if not exist "frontend" (
    echo ❌ Error: frontend directory not found
    exit /b 1
)
if not exist "backend" (
    echo ❌ Error: backend directory not found
    exit /b 1
)

REM Start backend
echo 📦 Starting backend server...
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo 🔧 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Please copy .env.example to .env and configure it.
    echo ℹ️  Creating .env from .env.example...
    copy .env.example .env
)

REM Start FastAPI server
echo 🖥️  Starting FastAPI server on http://localhost:8000
start /b uvicorn main:app --reload --host 0.0.0.0 --port 8000

cd ..

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend
echo 🎨 Starting frontend server...
cd frontend

REM Install dependencies
echo 📥 Installing Node.js dependencies...
call npm install

REM Start Vite dev server
echo 🖥️  Starting Vite dev server on http://localhost:5173
start /b npm run dev

cd ..

echo.
echo ✅ Both servers are starting up!
echo 📱 Frontend: http://localhost:5173
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop...
pause > nul