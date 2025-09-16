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

class PDFVoiceReader:
    def __init__(self, root):
        self.root = root
        self.root.title("Lector de PDF en Voz Alta")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        # Configurar el motor de voz
        self.engine = pyttsx3.init()
        self.is_speaking = False
        self.is_paused = False
        self.current_text = ""
        self.current_position = 0
        
        # Variables para el botón flotante
        self.floating_button = None
        self.last_clipboard = ""
        self.clipboard_monitor_active = True
        
        self.setup_ui()
        self.setup_voice_settings()
        self.start_clipboard_monitor()
        
    def setup_ui(self):
        # Estilo personalizado
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TButton', font=('Arial', 10, 'bold'))
        style.configure('Custom.TLabel', font=('Arial', 11), background='#2c3e50', foreground='white')
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
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
        
        info_text = ("Para leer cualquier texto:\n"
                    "1. Selecciona texto en cualquier aplicación\n"
                    "2. Copia el texto (Ctrl+C)\n"
                    "3. Aparecerá automáticamente un botón flotante 'Leer'\n"
                    "4. Haz clic en el botón para escuchar el texto")
        
        info_label = tk.Label(info_frame, text=info_text, 
                             font=('Arial', 10), bg='#34495e', fg='#bdc3c7',
                             justify=tk.LEFT)
        info_label.pack()
        
        # Área de texto para mostrar contenido
        text_frame = tk.LabelFrame(main_frame, text="📄 Contenido del PDF", 
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
        self.status_var = tk.StringVar(value="Listo - Selecciona un PDF para comenzar")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, 
                             font=('Arial', 9), bg='#34495e', fg='#bdc3c7',
                             relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=5)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def setup_voice_settings(self):
        """Configurar las opciones iniciales del motor de voz"""
        voices = self.engine.getProperty('voices')
        if voices:
            # Intentar usar una voz en español si está disponible
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es-' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        
        self.engine.setProperty('rate', 200)
        self.engine.setProperty('volume', 0.9)
        
    def update_speed(self, value):
        """Actualizar la velocidad de lectura"""
        speed = int(value)
        self.engine.setProperty('rate', speed)
        self.speed_label.config(text=f"{speed} ppm")
        
    def update_volume(self, value):
        """Actualizar el volumen de lectura"""
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
            self.play_btn.config(state=tk.NORMAL)
            
            self.status_var.set(f"PDF cargado - {len(pdf_reader.pages)} páginas")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el PDF:\n{str(e)}")
            self.status_var.set("Error al cargar PDF")
            
    def play_pdf(self):
        """Reproducir el texto del PDF"""
        if not self.current_text.strip():
            messagebox.showwarning("Advertencia", "No hay texto para reproducir")
            return
            
        if not self.is_speaking:
            self.start_speaking(self.current_text)
        elif self.is_paused:
            self.pause_resume()
            
    def start_speaking(self, text):
        """Iniciar la lectura en un hilo separado"""
        if self.is_speaking:
            return
            
        self.is_speaking = True
        self.is_paused = False
        
        # Habilitar/deshabilitar botones
        self.play_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.status_var.set("Reproduciendo...")
        
        # Ejecutar en hilo separado para no bloquear la UI
        thread = threading.Thread(target=self._speak_text, args=(text,), daemon=True)
        thread.start()
        
    def _speak_text(self, text):
        """Función para hablar el texto (ejecutada en hilo separado)"""
        try:
            # Limpiar texto de caracteres problemáticos
            clean_text = text.replace('\n', ' ').replace('\r', ' ')
            clean_text = ' '.join(clean_text.split())  # Normalizar espacios
            
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
        self.play_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Reproducción completada")
        
    def pause_resume(self):
        """Pausar o reanudar la reproducción"""
        if self.is_speaking:
            if not self.is_paused:
                # Pausar
                self.engine.stop()
                self.is_paused = True
                self.pause_btn.config(text="▶️ Reanudar")
                self.status_var.set("Pausado")
            else:
                # Reanudar
                self.is_paused = False
                self.pause_btn.config(text="⏸️ Pausar")
                self.status_var.set("Reproduciendo...")
                # Reiniciar desde donde se pausó
                thread = threading.Thread(target=self._speak_text, 
                                        args=(self.current_text,), daemon=True)
                thread.start()
                
    def stop_reading(self):
        """Detener la reproducción"""
        if self.is_speaking:
            self.engine.stop()
            self._reset_buttons()
            self.pause_btn.config(text="⏸️ Pausar")
            self.status_var.set("Reproducción detenida")
            
    def start_clipboard_monitor(self):
        """Iniciar el monitoreo del portapapeles"""
        self.monitor_clipboard()
        
    def monitor_clipboard(self):
        """Monitorear cambios en el portapapeles"""
        if not self.clipboard_monitor_active:
            return
            
        try:
            current_clipboard = pyperclip.paste()
            
            # Si hay nuevo contenido en el portapapeles y no está vacío
            if (current_clipboard != self.last_clipboard and 
                current_clipboard.strip() and 
                len(current_clipboard.strip()) > 5):  # Mínimo 5 caracteres
                
                self.last_clipboard = current_clipboard
                self.show_floating_button(current_clipboard)
                
        except Exception as e:
            pass  # Ignorar errores del portapapeles
            
        # Programar la próxima verificación
        self.root.after(500, self.monitor_clipboard)
        
    def show_floating_button(self, text):
        """Mostrar botón flotante para leer texto"""
        # Cerrar botón anterior si existe
        if self.floating_button:
            self.floating_button.destroy()
            
        # Crear nueva ventana flotante
        self.floating_button = tk.Toplevel(self.root)
        self.floating_button.title("")
        self.floating_button.geometry("120x50")
        self.floating_button.resizable(False, False)
        self.floating_button.attributes("-topmost", True)
        self.floating_button.configure(bg='#3498db')
        
        # Remover decoraciones de ventana
        self.floating_button.overrideredirect(True)
        
        # Posicionar en la esquina superior derecha
        screen_width = self.floating_button.winfo_screenwidth()
        self.floating_button.geometry(f"120x50+{screen_width-140}+50")
        
        # Botón para leer
        read_btn = tk.Button(self.floating_button, text="🔊 Leer", 
                            command=lambda: self.read_clipboard_text(text),
                            font=('Arial', 10, 'bold'), bg='#2980b9', fg='white',
                            relief=tk.FLAT, cursor='hand2')
        read_btn.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Botón para cerrar
        close_btn = tk.Button(self.floating_button, text="✕", 
                             command=self.close_floating_button,
                             font=('Arial', 8), bg='#e74c3c', fg='white',
                             relief=tk.FLAT, cursor='hand2', width=3)
        close_btn.place(x=95, y=5, width=20, height=15)
        
        # Auto-cerrar después de 10 segundos
        self.root.after(10000, self.close_floating_button)
        
    def read_clipboard_text(self, text):
        """Leer el texto del portapapeles"""
        # Detener cualquier reproducción actual
        if self.is_speaking:
            self.stop_reading()
            
        # Cerrar botón flotante
        self.close_floating_button()
        
        # Leer el texto
        self.start_speaking(text)
        
    def close_floating_button(self):
        """Cerrar el botón flotante"""
        if self.floating_button:
            self.floating_button.destroy()
            self.floating_button = None
            
    def on_closing(self):
        """Manejar el cierre de la aplicación"""
        self.clipboard_monitor_active = False
        if self.is_speaking:
            self.engine.stop()
        if self.floating_button:
            self.floating_button.destroy()
        self.root.destroy()

def main():
    """Función principal"""
    # Verificar dependencias
    try:
        import pyttsx3
        import PyPDF2
        import pyperclip
    except ImportError as e:
        missing_module = str(e).split("'")[1]
        print(f"Error: Falta instalar el módulo {missing_module}")
        print("Ejecuta: pip install pyttsx3 PyPDF2 pyperclip")
        input("Presiona Enter para salir...")
        return
        
    # Crear y ejecutar aplicación
    root = tk.Tk()
    app = PDFVoiceReader(root)
    
    # Configurar el cierre de la aplicación
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Ejecutar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()