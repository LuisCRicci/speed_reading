import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pyttsx3
import PyPDF2
import threading
import pyperclip
import time
import sys
import os
from tkinter import font
import subprocess

class PDFVoiceReader:
    def __init__(self, root):
        self.root = root
        self.root.title("Lector de PDF en Voz Alta")
        self.root.geometry("725x700")
        self.root.configure(bg='#2c3e50')
        
        # Configurar el motor de voz
        try:
            self.engine = pyttsx3.init()
            self.voice_available = True
        except Exception as e:
            self.voice_available = False
            messagebox.showerror("Error de Voz", 
                               f"Error al inicializar el motor de voz:\n{str(e)}\n\n"
                               "El programa continuará pero sin funcionalidad de voz.")
        
        self.is_speaking = False
        self.is_paused = False
        self.current_text = ""
        self.current_position = 0
        
        # Variables para el botón flotante
        self.floating_button = None
        self.last_clipboard = ""
        self.clipboard_monitor_active = True
        self.clipboard_thread = None
        
        self.setup_ui()
        if self.voice_available:
            self.setup_voice_settings()
        self.start_clipboard_monitor()
        
        # Mostrar instrucciones al inicio
        self.show_startup_instructions()
        
    def show_startup_instructions(self):
        """Mostrar instrucciones de uso al iniciar"""
        instructions = """
🎤 INSTRUCCIONES DE USO:

📄 Para leer PDFs:
• Haz clic en "Seleccionar PDF"
• Ajusta velocidad y volumen
• Presiona "Reproducir"

📝 Para leer texto seleccionado:
• Selecciona texto en cualquier aplicación
• Presiona Ctrl+C para copiar
• Aparecerá un botón flotante "Leer"
• Haz clic en el botón para escuchar

⚠️ IMPORTANTE: 
• Ejecuta desde la terminal: python pdf_voice_reader.py
• Mantén esta ventana abierta
• El monitoreo del portapapeles está activo
        """
        
        # Mostrar en el área de texto
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, instructions)
        
    def setup_ui(self):
        # Estilo personalizado
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TButton', font=('Arial', 10, 'bold'))
        style.configure('Custom.TLabel', font=('Arial', 11), background='#2c3e50', foreground='white')
        
        # ===== Scroll general (vertical y horizontal) =====
        container = tk.Frame(self.root, bg='#2c3e50')
        container.pack(fill=tk.BOTH, expand=True)

        # Canvas con scroll
        canvas = tk.Canvas(container, bg='#2c3e50', highlightthickness=0)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        
        scroll_frame = tk.Frame(canvas, bg='#2c3e50')

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Empaquetar scrollbars y canvas
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        
        
        

        # Ahora usamos scroll_frame en lugar de self.root como contenedor
        main_frame = scroll_frame

        # ============================
        # Título
        title_label = tk.Label(main_frame, text="📚 Lector de PDF en Voz Alta", 
                            font=('Arial', 20, 'bold'), 
                            bg='#2c3e50', fg='#ecf0f1')
        title_label.pack(pady=(0, 20))
        
        # Frame de controles de archivo
        file_frame = tk.Frame(main_frame, bg='#2c3e50')
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.file_label = tk.Label(file_frame, text="Ningún archivo seleccionado", 
                                  font=('Arial', 10), bg='#2c3e50', fg='#bdc3c7')
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        select_btn = tk.Button(file_frame, text="📁 Seleccionar PDF", 
                              command=self.select_pdf, 
                              font=('Arial', 10, 'bold'),
                              bg='#3498db', fg='white', 
                              relief=tk.FLAT, padx=20, pady=8,
                              cursor='hand2')
        select_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Botón de prueba para el portapapeles
        test_btn = tk.Button(file_frame, text="🧪 Probar Portapapeles", 
                            command=self.test_clipboard, 
                            font=('Arial', 10, 'bold'),
                            bg='#9b59b6', fg='white', 
                            relief=tk.FLAT, padx=15, pady=8,
                            cursor='hand2')
        test_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Frame de configuración de voz
        voice_frame = tk.LabelFrame(main_frame, text="⚙️ Configuración de Voz", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#34495e', fg='#ecf0f1', 
                                   relief=tk.FLAT, padx=10, pady=10)
        voice_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Velocidad
        speed_frame = tk.Frame(voice_frame, bg='#34495e')
        speed_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(speed_frame, text="Velocidad:", 
                font=('Arial', 10, 'bold'), bg='#34495e', fg='#ecf0f1').pack(side=tk.LEFT)
        
        self.speed_var = tk.IntVar(value=200)
        speed_scale = tk.Scale(speed_frame, from_=50, to=400, orient=tk.HORIZONTAL, 
                              variable=self.speed_var, command=self.update_speed,
                              bg='#34495e', fg='#ecf0f1', highlightthickness=0,
                              troughcolor='#2c3e50', activebackground='#3498db')
        speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        self.speed_label = tk.Label(speed_frame, text="200 ppm", 
                                   font=('Arial', 10), bg='#34495e', fg='#bdc3c7')
        self.speed_label.pack(side=tk.RIGHT)
        
        
        
        # Volumen 
        volume_frame = tk.Frame(voice_frame, bg='#34495e')
        volume_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(volume_frame, text="Volumen:", 
                font=('Arial', 10, 'bold'), bg='#34495e', fg='#ecf0f1').pack(side=tk.LEFT)
        
        self.volume_var = tk.DoubleVar(value=0.9)
        volume_scale = tk.Scale(volume_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, 
                               resolution=0.1, variable=self.volume_var, 
                               command=self.update_volume,
                               bg='#34495e', fg='#ecf0f1', highlightthickness=0,
                               troughcolor='#2c3e50', activebackground='#3498db')
        volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        self.volume_label = tk.Label(volume_frame, text="90%", 
                                    font=('Arial', 10), bg='#34495e', fg='#bdc3c7')
        self.volume_label.pack(side=tk.RIGHT)

        # Selección de voz
        voice_select_frame = tk.Frame(voice_frame, bg='#34495e')
        voice_select_frame.pack(fill=tk.X, pady=5)
        tk.Label(voice_select_frame, text="Voz:", font=('Arial', 10, 'bold'), bg='#34495e', fg='#ecf0f1').pack(side=tk.LEFT)
        self.voice_var = tk.StringVar()
        self.voice_combobox = ttk.Combobox(voice_select_frame, textvariable=self.voice_var, state="readonly", width=40)
        self.voice_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        self.voice_combobox.bind("<<ComboboxSelected>>", self.change_voice)
        
        
        
        # Frame de controles de reproducción
        control_frame = tk.Frame(main_frame, bg='#2c3e50')
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botones de control
        self.play_btn = tk.Button(control_frame, text="▶️ Reproducir", 
                                 command=self.play_pdf, state=tk.DISABLED,
                                 font=('Arial', 11, 'bold'), bg='#27ae60', fg='white',
                                 relief=tk.FLAT, padx=20, pady=10, cursor='hand2')
        self.play_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.pause_btn = tk.Button(control_frame, text="⏸️ Pausar", 
                                  command=self.pause_resume, state=tk.DISABLED,
                                  font=('Arial', 11, 'bold'), bg='#f39c12', fg='white',
                                  relief=tk.FLAT, padx=20, pady=10, cursor='hand2')
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Detener", 
                                 command=self.stop_reading, state=tk.DISABLED,
                                 font=('Arial', 11, 'bold'), bg='#e74c3c', fg='white',
                                 relief=tk.FLAT, padx=20, pady=10, cursor='hand2')
        self.stop_btn.pack(side=tk.LEFT)
        
        # Información del botón flotante
        info_frame = tk.LabelFrame(main_frame, text="💡 Función de Lectura de Texto", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#34495e', fg='#ecf0f1', 
                                  relief=tk.FLAT, padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        info_text = ("🔍 Estado del Monitoreo: ACTIVO\n"
                    "1. Selecciona texto y Copia el texto (Ctrl+C)\n"
                    "3. Aparecerá automáticamente un botón flotante 'Leer'\n"
                    "4. Haz clic en el botón para escuchar el texto\n\n"
                    "💡 Consejo: Usa el botón 'Probar Portapapeles' para verificar")
        
        self.info_label = tk.Label(info_frame, text=info_text, 
                                  font=('Arial', 10), bg='#34495e', fg='#bdc3c7',
                                  justify=tk.LEFT)
        self.info_label.pack()
        
        # Área de texto para mostrar contenido
        text_frame = tk.LabelFrame(main_frame, text="📄 Contenido / Instrucciones", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#34495e', fg='#ecf0f1', 
                                  relief=tk.FLAT, padx=10, pady=10)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                  font=('Arial', 11),
                                                  bg='#ecf0f1', fg='#2c3e50',
                                                  relief=tk.FLAT, padx=10, pady=10)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Barra de estado
        self.status_var = tk.StringVar(value="✅ Listo - Monitoreo de portapapeles ACTIVO")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, 
                             font=('Arial', 9), bg='#34495e', fg='#bdc3c7',
                             relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=5)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def test_clipboard(self):
        """Probar la funcionalidad del portapapeles"""
        test_text = "¡Hola! Esta es una prueba del sistema de lectura de texto. Si escuchas este mensaje, todo está funcionando correctamente."
        
        try:
            # Copiar texto de prueba al portapapeles
            pyperclip.copy(test_text)
            self.status_var.set("✅ Texto de prueba copiado al portapapeles - Esperando botón flotante...")
            
            # Forzar la aparición del botón flotante
            self.root.after(1000, lambda: self.show_floating_button(test_text))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al acceder al portapapeles:\n{str(e)}")
        
    def setup_voice_settings(self):
        """Configurar las opciones iniciales del motor de voz"""
        if not self.voice_available:
            return
        try:
            voices = self.engine.getProperty('voices')
            self.voices = voices
            voice_names = [f"{v.name} ({v.id})" for v in voices]
            self.voice_combobox['values'] = voice_names
            # Seleccionar voz en español si existe
            selected = 0
            for idx, voice in enumerate(voices):
                if ('spanish' in voice.name.lower() or 
                    'es-' in voice.id.lower() or 
                    'helena' in voice.name.lower() or
                    'sabina' in voice.name.lower()):
                    selected = idx
                    break
            self.voice_combobox.current(selected)
            self.engine.setProperty('voice', voices[selected].id)
            self.voice_var.set(voice_names[selected])
            self.engine.setProperty('rate', 200)
            self.engine.setProperty('volume', 0.9)
        except Exception as e:
            print(f"Error configurando voz: {e}")

    def change_voice(self, event=None):
        """Cambiar la voz del motor de voz"""
        if not self.voice_available:
            return
        idx = self.voice_combobox.current()
        if hasattr(self, 'voices') and 0 <= idx < len(self.voices):
            self.engine.setProperty('voice', self.voices[idx].id)
        
    def update_speed(self, value):
        """Actualizar la velocidad de lectura"""
        if not self.voice_available:
            return
        speed = int(value)
        self.engine.setProperty('rate', speed)
        self.speed_label.config(text=f"{speed} ppm")
        
    def update_volume(self, value):
        """Actualizar el volumen de lectura"""
        if not self.voice_available:
            return
        volume = float(value)
        self.engine.setProperty('volume', volume)
        self.volume_label.config(text=f"{int(volume*100)}%")
        
    def select_pdf(self):
        """Seleccionar archivo PDF"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.load_pdf(file_path)
            
    def load_pdf(self, file_path):
        """Cargar y extraer texto del PDF"""
        try:
            self.status_var.set("Cargando PDF...")
            self.root.update()
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text_content += f"\n--- Página {page_num + 1} ---\n"
                    text_content += page.extract_text()
                    
            self.current_text = text_content
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, text_content)
            
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"Archivo: {filename}")
            
            # Habilitar botones
            if self.voice_available:
                self.play_btn.config(state=tk.NORMAL)
            
            self.status_var.set(f"PDF cargado - {len(pdf_reader.pages)} páginas")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el PDF:\n{str(e)}")
            self.status_var.set("Error al cargar PDF")
            
    def play_pdf(self):
        """Reproducir el texto del PDF"""
        if not self.voice_available:
            messagebox.showerror("Error", "Motor de voz no disponible")
            return
            
        if not self.current_text.strip():
            messagebox.showwarning("Advertencia", "No hay texto para reproducir")
            return
            
        if not self.is_speaking:
            self.start_speaking(self.current_text)
        elif self.is_paused:
            self.pause_resume()
            
    def start_speaking(self, text):
        """Iniciar la lectura en un hilo separado"""
        if not self.voice_available or self.is_speaking:
            return
            
        self.is_speaking = True
        self.is_paused = False
        
        # Habilitar/deshabilitar botones
        self.play_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.status_var.set("🔊 Reproduciendo...")
        
        # Ejecutar en hilo separado para no bloquear la UI
        thread = threading.Thread(target=self._speak_text, args=(text,), daemon=True)
        thread.start()
        
    def _speak_text(self, text):
        """Función para hablar el texto (ejecutada en hilo separado)"""
        try:
            # Limpiar texto de caracteres problemáticos
            clean_text = text.replace('\n', ' ').replace('\r', ' ')
            clean_text = ' '.join(clean_text.split())  # Normalizar espacios
            
            # Limitar longitud del texto para evitar problemas
            if len(clean_text) > 5000:
                clean_text = clean_text[:5000] + "..."
            
            self.engine.say(clean_text)
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"Error al reproducir: {e}")
        finally:
            # Restaurar estado de botones en el hilo principal
            self.root.after(0, self._reset_buttons)
            
    def _reset_buttons(self):
        """Restaurar el estado de los botones después de terminar"""
        self.is_speaking = False
        self.is_paused = False
        if self.voice_available:
            self.play_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("✅ Reproducción completada")
        
    def pause_resume(self):
        """Pausar o reanudar la reproducción"""
        if not self.voice_available:
            return
            
        if self.is_speaking:
            if not self.is_paused:
                # Pausar
                self.engine.stop()
                self.is_paused = True
                self.pause_btn.config(text="▶️ Reanudar")
                self.status_var.set("⏸️ Pausado - Al reanudar, se reiniciará la lectura")
            else:
                # Reanudar desde el principio (limitación de pyttsx3)
                self.is_paused = False
                self.pause_btn.config(text="⏸️ Pausar")
                self.status_var.set("🔊 Reanudando desde el inicio...")
                thread = threading.Thread(target=self._speak_text, 
                                        args=(self.current_text,), daemon=True)
                thread.start()
                
    def stop_reading(self):
        """Detener la reproducción"""
        if not self.voice_available:
            return
            
        if self.is_speaking:
            self.engine.stop()
            self._reset_buttons()
            self.pause_btn.config(text="⏸️ Pausar")
            self.status_var.set("⏹️ Reproducción detenida")
            
    def start_clipboard_monitor(self):
        """Iniciar el monitoreo del portapapeles en un hilo separado"""
        def monitor_worker():
            while self.clipboard_monitor_active:
                try:
                    current_clipboard = pyperclip.paste()
                    
                    # Si hay nuevo contenido en el portapapeles y no está vacío
                    if (current_clipboard != self.last_clipboard and 
                        current_clipboard.strip() and 
                        len(current_clipboard.strip()) > 10):  # Mínimo 10 caracteres
                        
                        self.last_clipboard = current_clipboard
                        # Ejecutar en el hilo principal
                        self.root.after(0, lambda text=current_clipboard: self.show_floating_button(text))
                        
                except Exception as e:
                    print(f"Error en monitoreo de portapapeles: {e}")
                
                time.sleep(0.5)  # Verificar cada 500ms
        
        # Iniciar el hilo de monitoreo
        self.clipboard_thread = threading.Thread(target=monitor_worker, daemon=True)
        self.clipboard_thread.start()
        
    def show_floating_button(self, text):
        """Mostrar botón flotante para leer texto"""
        # Cerrar botón anterior si existe
        if self.floating_button:
            try:
                self.floating_button.destroy()
            except:
                pass
            
        try:
            # Crear nueva ventana flotante
            self.floating_button = tk.Toplevel(self.root)
            self.floating_button.title("Leer Texto")
            self.floating_button.geometry("140x60")
            self.floating_button.resizable(False, False)
            self.floating_button.attributes("-topmost", True)
            self.floating_button.configure(bg='#3498db')
            
            # Remover decoraciones de ventana
            self.floating_button.overrideredirect(True)
            
            # Posicionar en la esquina superior derecha
            screen_width = self.floating_button.winfo_screenwidth()
            self.floating_button.geometry(f"140x60+{screen_width-160}+50")
            
            # Frame principal
            main_frame = tk.Frame(self.floating_button, bg='#3498db')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            # Botón para leer
            read_btn = tk.Button(main_frame, text="🔊 Leer Texto", 
                                command=lambda: self.read_clipboard_text(text),
                                font=('Arial', 10, 'bold'), bg='#2980b9', fg='white',
                                relief=tk.FLAT, cursor='hand2')
            read_btn.pack(fill=tk.X, pady=(0, 2))
            
            # Botón para cerrar
            close_btn = tk.Button(main_frame, text="✕ Cerrar", 
                                 command=self.close_floating_button,
                                 font=('Arial', 8), bg='#e74c3c', fg='white',
                                 relief=tk.FLAT, cursor='hand2')
            close_btn.pack(fill=tk.X)
            
            # Actualizar barra de estado
            self.status_var.set("🎯 Botón flotante mostrado - Texto listo para leer")
            
            # Auto-cerrar después de 15 segundos
            self.root.after(15000, self.close_floating_button)
            
        except Exception as e:
            print(f"Error creando botón flotante: {e}")
            messagebox.showinfo("Texto Copiado", f"Texto listo para leer:\n{text[:100]}...")
        
    def read_clipboard_text(self, text):
        """Leer el texto del portapapeles"""
        if not self.voice_available:
            messagebox.showerror("Error", "Motor de voz no disponible")
            return
            
        # Detener cualquier reproducción actual
        if self.is_speaking:
            self.stop_reading()
            # Esperar a que el motor se detenga realmente
            time.sleep(0.3)
            
        # Cerrar botón flotante
        self.close_floating_button()
        
        # Mostrar texto en el área de texto
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, f"📋 Texto del Portapapeles:\n\n{text}")
        
        # ¡IMPORTANTE! Asignar este texto como el actual, para que los controles funcionen
        self.current_text = text
        
        # Leer el texto
        self.start_speaking(text)
        
        
        
        
        
    def close_floating_button(self):
        """Cerrar el botón flotante"""
        if self.floating_button:
            try:
                self.floating_button.destroy()
            except:
                pass
            finally:
                self.floating_button = None
                
    def on_closing(self):
        """Manejar el cierre de la aplicación"""
        self.clipboard_monitor_active = False
        if self.voice_available and self.is_speaking:
            self.engine.stop()
        if self.floating_button:
            try:
                self.floating_button.destroy()
            except:
                pass
        self.root.destroy()

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    missing_deps = []
    
    try:
        import pyttsx3
    except ImportError:
        missing_deps.append("pyttsx3")
        
    try:
        import PyPDF2
    except ImportError:
        missing_deps.append("PyPDF2")
        
    try:
        import pyperclip
    except ImportError:
        missing_deps.append("pyperclip")
    
    if missing_deps:
        print("❌ ERROR: Faltan dependencias por instalar:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\n📦 Para instalar las dependencias ejecuta:")
        print("   pip install " + " ".join(missing_deps))
        print("\n🔧 O ejecuta el archivo install.bat si lo tienes")
        input("\nPresiona Enter para salir...")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando Lector de PDF en Voz Alta...")
    print("📋 Verificando dependencias...")
    
    # Verificar dependencias
    if not check_dependencies():
        return
        
    print("✅ Todas las dependencias están instaladas")
    print("🎤 Iniciando aplicación...")
    
    # Crear y ejecutar aplicación
    root = tk.Tk()
    app = PDFVoiceReader(root)
    
    # Configurar el cierre de la aplicación
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    print("✨ Aplicación iniciada correctamente")
    print("💡 Mantén esta ventana de terminal abierta")
    
    # Ejecutar aplicación
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()