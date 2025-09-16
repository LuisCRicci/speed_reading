@echo off
title Lector PDF en Voz Alta
color 0A

echo.
echo ========================================
echo    🎤 LECTOR PDF EN VOZ ALTA 🎤
echo ========================================
echo.

echo 📋 Verificando Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error: Python no esta instalado o no esta en PATH
    echo.
    echo 💡 Solucion:
    echo    1. Instala Python desde https://python.org
    echo    2. Asegurate de marcar "Add to PATH" durante la instalacion
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

echo 🚀 Iniciando el programa...
echo.
echo 💡 INSTRUCCIONES:
echo    • Para PDFs: Usa el boton "Seleccionar PDF"
echo    • Para texto: Selecciona texto en cualquier app y presiona Ctrl+C
echo    • Usa el boton "Probar Portapapeles" para verificar funcionamiento
echo.
echo ⚠️  IMPORTANTE: NO cierres esta ventana mientras uses el programa
echo.

python pdf_voice_reader.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ El programa termino con errores
    echo 💡 Si falta algun modulo, ejecuta: pip install pyttsx3 PyPDF2 pyperclip
    echo.
)

echo.
echo 👋 Programa finalizado
pause