@echo off
echo ========================================
echo Instalador de Lector PDF en Voz Alta
echo ========================================
echo.

echo Verificando Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python no esta instalado o no esta en PATH
    pause
    exit /b 1
)
echo.

echo Instalando dependencias necesarias...
echo.

echo Instalando pyttsx3 (Motor de sintesis de voz)...
pip show pyttsx3 > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Instalando pyttsx3...
    pip install pyttsx3
) else (
    echo pyttsx3 ya está instalado.
)

echo Instalando PyPDF2 (Lector de PDF)...
pip show PyPDF2 > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Instalando PyPDF2...
    pip install PyPDF2
) else (
    echo PyPDF2 ya está instalado.
)

echo Instalando pyperclip (Monitor de portapapeles)...
pip show pyperclip > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Instalando pyperclip...
    pip install pyperclip
) else (
    echo pyperclip ya está instalado.
)

echo.
echo ========================================
echo Instalacion completada!
echo ========================================
echo.
echo Ahora puedes ejecutar el programa:
echo python pdf_voice_reader.py
echo.
pause
exit /b 0