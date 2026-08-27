@echo off
setlocal enabledelayedexpansion

if "!GCST_WERROR!"=="" set GCST_WERROR=OFF

python3 .gcst/scripts/build.py "%*"