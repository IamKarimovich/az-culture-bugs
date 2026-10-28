@echo off
chcp 65001 >nul
dotnet run --project dotnet || exit /b 1
python python_tests.py || exit /b 1
node js_tests.mjs || exit /b 1
python report.py
