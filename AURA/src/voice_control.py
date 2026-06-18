"""
AURA - Módulo de Reconocimiento de Voz
Permite al usuario hacer preguntas por voz mediante el micrófono del auricular Bluetooth
"""

import speech_recognition as sr
import threading
from datetime import datetime


class VoiceCommandRecognizer:
    """Reconocimiento de comandos de voz del usuario"""
    
    def __init__(self, language='es-ES'):
        self.recognizer = sr.Recognizer()
        self.language = language
        self.running = False
        self.callback = None
        
        # Configurar recognizer
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        print("[i] Sistema de reconocimiento de voz inicializado")
        print(f"    Idioma: {language}")
    
    def listen(self, timeout=5, phrase_time_limit=10):
        """Escuchar comando de voz desde el micrófono"""
        try:
            with sr.Microphone() as source:
                print("[i] Escuchando...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, 
                                              phrase_time_limit=phrase_time_limit)
                
                # Reconocer con Google Speech Recognition
                text = self.recognizer.recognize_google(audio, language=self.language)
                return text.lower()
                
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[!] Error en servicio de reconocimiento: {e}")
            return None
        except Exception as e:
            print(f"[!] Error: {e}")
            return None
    
    def process_command(self, text):
        """Procesar comando de voz y determinar acción"""
        if not text:
            return None, None
        
        print(f"[🎤] Usuario dijo: '{text}'")
        
        # Comandos soportados
        commands = {
            'salida': ('location', '¿Dónde está la salida más cercana?'),
            'puerta': ('location', 'Hay una puerta cerca'),
            'escalera': ('warning', 'Cuidado, hay escaleras'),
            'persona': ('query', '¿Hay personas cerca?'),
            'caída': ('emergency', '¡ALERTA! Persona caída detectada'),
            'fuego': ('emergency', '¡PELIGRO! Fuego detectado'),
            'humo': ('emergency', '¡PELIGRO! Humo detectado'),
            'obstáculo': ('warning', 'Hay un obstáculo en el camino'),
            'silla': ('obstacle', 'Silla detectada en el camino'),
            'describe': ('describe', 'Describiendo el entorno...'),
            'ayuda': ('help', 'Comandos disponibles: salida, escalera, persona, fuego, describe'),
        }
        
        # Buscar coincidencias
        for keyword, (cmd_type, response) in commands.items():
            if keyword in text:
                return cmd_type, response
        
        # Si no hay coincidencia exacta, devolver como consulta general
        return ('query', f'Escuché: {text}')
    
    def start_listening_loop(self, callback_func):
        """Iniciar bucle de escucha en hilo separado"""
        self.callback = callback_func
        self.running = True
        
        def listen_thread():
            while self.running:
                command = self.listen(timeout=3, phrase_time_limit=5)
                if command:
                    cmd_type, response = self.process_command(command)
                    if cmd_type and self.callback:
                        self.callback(cmd_type, response)
        
        thread = threading.Thread(target=listen_thread, daemon=True)
        thread.start()
        print("[✓] Escucha de voz activada")
    
    def stop(self):
        """Detener escucha de voz"""
        self.running = False
        print("[i] Escucha de voz detenida")


# Ejemplo de uso
if __name__ == "__main__":
    def on_command(cmd_type, response):
        print(f"[{cmd_type.upper()}] {response}")
    
    recognizer = VoiceCommandRecognizer()
    
    print("\n=== Prueba de Reconocimiento de Voz ===")
    print("Di un comando (ej: 'salida', 'escalera', 'ayuda')")
    print("Presione Ctrl+C para salir\n")
    
    try:
        while True:
            command = recognizer.listen()
            if command:
                cmd_type, response = recognizer.process_command(command)
                if cmd_type:
                    print(f"[{cmd_type.upper()}] {response}\n")
    except KeyboardInterrupt:
        print("\nPrueba terminada")
