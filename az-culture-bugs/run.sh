#!/usr/bin/env bash
set -e
dotnet run --project dotnet
python3 python_tests.py
node js_tests.mjs
python3 report.py
