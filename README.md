# 📚 Lector de PDF en Voz Alta + Lectura de Texto Seleccionado

> Una aplicación de escritorio en Python que lee en voz alta el contenido de archivos PDF o cualquier texto copiado al portapapeles. Ideal para accesibilidad, estudio o multitarea, la razon principal es evitar el cansancio visual y dar descanzo a la vista al momento de leer  libros o documentos prologandamemte en pantallas.

---

## 🎯 Características principales

- 📄 **Lectura de PDFs completos** con control de velocidad y volumen.
- 📋 **Lectura automática de texto copiado** (Ctrl+C en cualquier app) mediante un botón flotante.
- ⏸️ **Controles de reproducción**: Pausar, Reanudar, Detener.
- 🎚️ **Ajustes de voz**: Velocidad, volumen y selección de voz (si está disponible).
- 🖥️ **Interfaz gráfica intuitiva** con scroll horizontal y vertical.
- 🌐 **Multiplataforma**: Funciona en Windows, macOS y Linux.

---

## 🚀 Instalación paso a paso

### 1. Instalar Python

#### ✅ Windows

1. Ve a [python.org/downloads](https://www.python.org/downloads/)
2. Descarga la última versión de Python 3.x (por ejemplo, Python 3.12)
3. **¡Importante!** Marca la casilla ✅ **"Add Python to PATH"** durante la instalación.
4. Completa la instalación.

#### ✅ macOS

**Opción A: Usando Homebrew (recomendado)**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.12
```

**Opción B: Descargar desde python.org**

1. Ve a [python.org/downloads](https://www.python.org/downloads/)
2. Descarga el instalador para macOS.
3. Sigue las instrucciones del instalador.

#### ✅ Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install python3 python3-pip
```

#### ✅ Linux (Fedora)

```bash
sudo dnf install python3 python3-pip
```

---

### 2. Instalar pip (si no se instaló junto con Python)

- **Windows/macOS:** pip suele instalarse automáticamente con Python.
- **Linux:** Si no tienes pip, instálalo con:

```bash
sudo apt install python3-pip   # Debian/Ubuntu
sudo dnf install python3-pip   # Fedora
```

---

### 3. Instalar las dependencias del proyecto

#### Opción A: Usando requirements.txt

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

#### Opción B: Instalación manual

```bash
pip install pyttsx3 PyPDF2 pyperclip
```

#### Opción C: Instalador automático para Windows

Si usas Windows, puedes ejecutar el archivo `install.bat` incluido:

```bat
install.bat
```

Este script verifica Python y pip, e instala automáticamente las dependencias necesarias.

---

## 🖥️ Modo de uso

1. **Descarga o clona este repositorio.**
2. Abre una terminal en la carpeta del proyecto.
3. Ejecuta la aplicación con:

```bash
python pdf_voice_reader.py
```

4. **Para leer un PDF:**
   - Haz clic en "Seleccionar PDF".
   - Ajusta velocidad, volumen y voz.
   - Pulsa "Reproducir".

5. **Para leer texto de cualquier aplicación:**
   - Selecciona el texto y cópialo (Ctrl+C).
   - Aparecerá un botón flotante "Leer".
   - Haz clic en el botón para escuchar el texto.

---

## ℹ️ Notas adicionales

- En **Windows** puedes instalar más voces desde Configuración > Hora e idioma > Voz.
- En **Linux** y **macOS** la calidad y cantidad de voces puede variar.
- Si tienes problemas con el portapapeles en Linux, instala `xclip` o `xsel`:

```bash
sudo apt install xclip
```

- Si tienes problemas con permisos, ejecuta los comandos con `sudo` (Linux/macOS) o como administrador (Windows).

---

## 🛠️ Soporte

¿Tienes dudas o sugerencias? Abre un issue en este repositorio.

---