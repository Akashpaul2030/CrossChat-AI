@echo off
REM Windows batch file to run the LangChain Assistant (backend and frontend)

echo Starting LangChain Assistant...

REM Check if .env file exists
if not exist .env (
    echo Creating .env file...
    echo OPENAI_API_KEY=your_openai_api_key_here > .env
    echo TAVILY_API_KEY=your_tavily_api_key_here >> .env
    echo Please edit the .env file with your actual API keys before running again.
    echo Exiting...
    exit /b 1
)

REM Check if API keys are set
findstr "your_openai_api_key_here" .env >nul
if %ERRORLEVEL% EQU 0 (
    echo Please edit the .env file with your actual API keys.
    echo Exiting...
    exit /b 1
)

findstr "your_tavily_api_key_here" .env >nul
if %ERRORLEVEL% EQU 0 (
    echo Please edit the .env file with your actual API keys.
    echo Exiting...
    exit /b 1
)

REM Create memory directory if it doesn't exist
if not exist memory mkdir memory

REM Create a file to track the backend process ID
set PID_FILE=%TEMP%\langchain_backend_pid.txt

REM Check if backend is already running
if exist "%PID_FILE%" (
    echo Checking if backend is already running...
    set /p BACKEND_PID=<"%PID_FILE%"
    
    REM Try to query the process to see if it's running
    tasklist /FI "PID eq %BACKEND_PID%" | find "%BACKEND_PID%" >nul
    if %ERRORLEVEL% EQU 0 (
        echo Backend is already running with PID %BACKEND_PID%.
        choice /M "Do you want to stop it and start a new one"
        if %ERRORLEVEL% EQU 1 (
            echo Stopping existing backend process...
            taskkill /PID %BACKEND_PID% /F
        ) else (
            echo Using existing backend process.
            goto start_frontend
        )
    ) else (
        echo Previous backend process is not running.
        del "%PID_FILE%"
    )
)

REM Start the backend API server with a visible window to help with debugging
echo Starting backend API server...
start "LangChain Backend" cmd /c "python -m src.api & echo Backend server started with PID %%^PID%% & pause"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak
echo Backend should be running now.

:start_frontend
REM Start the frontend development server
echo Starting frontend development server...
cd src\frontend && npm start

echo.
echo Note: The backend server will continue running in its own window.
echo To stop it, close the "LangChain Backend" window.
echo.

exit /b 0