@echo off
REM Windows batch file to install dependencies for the LangChain Assistant

echo Installing dependencies for LangChain Assistant...

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Install frontend dependencies
echo Installing frontend dependencies...
cd src\frontend
npm install

echo All dependencies installed successfully!
echo You can now run the application using run.bat
