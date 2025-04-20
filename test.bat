@echo off
REM Windows batch file to test the LangChain Assistant

echo Running tests for LangChain Assistant...

REM Create test directory if it doesn't exist
if not exist tests mkdir tests

REM Run the unit tests
python -m unittest tests\test_assistant.py

echo Tests completed!
pause
