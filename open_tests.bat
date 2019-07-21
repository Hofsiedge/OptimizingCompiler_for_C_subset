@ECHO OFF
rem Open compiled files in SASM IDE (change the path to SASM if it doesn't match with this one)
@ECHO ON

FOR %%f IN (test_dir\compiled\*.asm) DO (
	start "C:\Program Files (x86)\SASM\sasm.exe" %%f
)