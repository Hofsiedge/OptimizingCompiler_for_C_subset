@ECHO OFF
rem Cleaning up target directories
@ECHO ON

RMDIR /S /Q src\__pycache__
del /Q /F test_dir\compiled\*.asm
del /Q /F src\CParser.py
del /Q /F src\CLexer.py
del /Q /F src\__init__.py
del /Q /F src\*.tokens