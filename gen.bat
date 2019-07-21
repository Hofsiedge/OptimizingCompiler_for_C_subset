@ECHO OFF
rem Генерация кода транслятора по грамматике
@ECHO ON

java -jar antlr-4.7-complete.jar C.g4 -no-listener -no-visitor -o src

echo pass > src/__init__.py