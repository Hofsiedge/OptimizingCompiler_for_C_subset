@ECHO OFF
rem Compile .c files into .asm files
@ECHO ON

cd src

FOR /R ..\test_dir\source %%f IN (*.c) DO (
	python compile.py "../test_dir/source/%%~nxf" > "..\test_dir\compiled\%%~nf.asm"
)

cd ..