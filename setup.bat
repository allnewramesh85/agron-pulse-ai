@echo off
setlocal enabledelayedexpansion

echo [1/4] Checking for uv and ollama tools...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing uv via pip...
    pip install uv
)

where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: ollama is not installed on this system.
    echo Please download and install it from https://ollama.com
    pause
    exit /b 1
)

echo [2/4] Creating ultra-fast virtual environment...
uv venv

echo Activating virtual environment...
call .venv\Scripts\activate

echo [3/4] Installing Python packages with uv...
uv pip install -r requirements.txt

echo [4/4] Pulling the gemma4:e4b model via Ollama...
ollama pull gemma4:e4b

echo Setup complete! Environment activated.
pause
