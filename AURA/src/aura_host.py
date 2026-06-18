"""
AURA - Host Processing System
Procesamiento de video con YOLOv8 + OpenCV + Síntesis de voz
Arquitectura Cliente-Servidor para ESP32-CAM
"""

import cv2
import numpy as np
from ultralytics import YOLO
import socket
import struct
import threading
import queue
import time
from datetime import datetime
import sys

# ==================== CONFIGURACIÓN ====================
ESP32_IP = "192.168.1.100"  # IP de la ESP32-CAM
ESP32_PORT = 80             # Puerto del servidor HTTP
YOLO_MODEL = "yolov8n.pt"   # Modelo ligero para tiempo real
CONFIDENCE_THRESHOLD = 0.5

# Objetos críticos para emergencias
EMERGENCY_OBJECTS = [
    'person',      # Personas (caídas, heridas)
    'fire',        # Fuego (si está en el modelo)
    'chair',       # Sillas/obstáculos
    'backpack',    # Mochilas/obstáculos
    'suitcase',    # Maletas/obstáculos
]

# Señales de seguridad
SAFETY_SIGNS = [
    'stop sign',   # Señales de tráfico
    'traffic light',
]

class ESP32VideoStream:
    """Clase para recibir el stream de video desde la ESP32-CAM"""
    
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.frame_queue = queue.Queue(maxsize=5)
        self.running = False
        self.socket_client = None
        
    def connect(self):
        """Conectar al servidor de streaming de la ESP32"""
        try:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.connect((self.ip, self.port))
            self.running = True
            print(f"[✓] Conectado a ESP32-CAM en {self.ip}:{self.port}")
            return True
        except Exception as e:
            print(f"[✗] Error conectando a ESP32: {e}")
            return False
    
    def read_frame(self):
        """Leer un frame del stream"""
        if not self.running or self.socket_client is None:
            return None
            
        try:
            # Leer header (4 bytes para tamaño)
            header = self.socket_client.recv(4)
            if len(header) < 4:
                return None
                
            # Verificar marker JPEG (0xFFD8)
            if header[0] == 0xFF and header[1] == 0xD8:
                # Leer tamaño del frame
                frame_size = struct.unpack('>H', header[2:4])[0]
                
                # Leer datos JPEG
                data = b""
                remaining = frame_size
                while remaining > 0:
                    chunk = self.socket_client.recv(min(4096, remaining))
                    if not chunk:
                        break
                    data += chunk
                    remaining -= len(chunk)
                
                if len(data) == frame_size:
                    # Decodificar imagen
                    nparr = np.frombuffer(data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    return frame
                    
        except Exception as e:
            print(f"[!] Error leyendo frame: {e}")
            self.running = False
            
        return None
    
    def stop(self):
        """Detener conexión"""
        self.running = False
        if self.socket_client:
            self.socket_client.close()


class ObjectDetector:
    """Detección de objetos con YOLOv8"""
    
    def __init__(self, model_path):
        print(f"[i] Cargando modelo YOLO: {model_path}")
        self.model = YOLO(model_path)
        self.class_names = self.model.names
        print(f"[✓] Modelo cargado. Clases disponibles: {len(self.class_names)}")
        
    def detect(self, frame, conf_threshold=0.5):
        """Detectar objetos en un frame"""
        results = self.model(frame, conf=conf_threshold, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                class_name = self.class_names[cls_id]
                
                detections.append({
                    'class': class_name,
                    'confidence': conf,
                    'bbox': (int(x1), int(y1), int(x2), int(y2)),
                    'center_x': (x1 + x2) / 2,
                    'center_y': (y1 + y2) / 2
                })
                
        return detections


class AudioFeedback:
    """Síntesis de voz para feedback al usuario"""
    
    def __init__(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Velocidad
            self.engine.setProperty('volume', 0.9)  # Volumen
            self.available = True
            print("[✓] Sistema de voz inicializado")
            
            # Voces en español
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.languages[0].lower() or 'es' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
                    
        except ImportError:
            print("[!] pyttsx3 no disponible. Usando prints.")
            self.available = False
    
    def speak(self, text):
        """Convertir texto a voz"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🗣️  {text}")
        
        if self.available:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass


class AURASystem:
    """Sistema principal AURA"""
    
    def __init__(self):
        self.video_stream = None
        self.detector = None
        self.audio = None
        self.running = False
        self.last_announcement = {}
        
    def initialize(self):
        """Inicializar todos los componentes"""
        print("\n" + "="*50)
        print("🌟 AURA SYSTEM - Iniciando")
        print("="*50)
        
        # Inicializar detector YOLO
        self.detector = ObjectDetector(YOLO_MODEL)
        
        # Inicializar sistema de audio
        self.audio = AudioFeedback()
        
        # Inicializar stream de video
        self.video_stream = ESP32VideoStream(ESP32_IP, ESP32_PORT)
        
        print("\n[i] Para conectar la ESP32-CAM, asegúrate de:")
        print("    1. Configurar SSID y contraseña en el firmware")
        print("    2. Subir el firmware a la ESP32-CAM")
        print("    3. Anotar la IP que muestra la ESP32")
        print("    4. Actualizar ESP32_IP en este script\n")
        
        return True
    
    def analyze_detections(self, detections):
        """Analizar detecciones y generar alertas"""
        alerts = []
        
        # Contar personas
        people_count = sum(1 for d in detections if d['class'] == 'person')
        
        # Detectar obstáculos en el camino
        obstacles = ['chair', 'backpack', 'suitcase', 'potted plant']
        detected_obstacles = [d for d in detections if d['class'] in obstacles]
        
        # Analizar por tipo de objeto
        for det in detections:
            cls = det['class']
            conf = det['confidence']
            
            # Alerta crítica: Persona caída (detectada cerca del suelo)
            if cls == 'person':
                height_ratio = det['bbox'][3] / det['bbox'][1] if det['bbox'][1] > 0 else 0
                if height_ratio < 0.3:  # Persona muy baja (posible caída)
                    alerts.append(f"¡ALERTA! Persona caída detectada")
            
            # Obstáculos en el camino
            if cls in obstacles and conf > 0.6:
                center_x = det['center_x']
                if 0.3 < center_x < 0.7:  # En el centro del camino
                    alerts.append(f"Cuidado: {cls} en el camino")
            
            # Fuego o humo (si el modelo lo detecta)
            if cls in ['fire', 'smoke']:
                alerts.append(f"¡PELIGRO! {cls} detectado")
        
        # Resumen de entorno
        if people_count > 0 and not alerts:
            if people_count == 1:
                alerts.append("Hay una persona cerca")
            else:
                alerts.append(f"Hay {people_count} personas cerca")
        
        return alerts
    
    def generate_directions(self, detections, frame_width):
        """Generar instrucciones de navegación"""
        directions = []
        
        # Buscar salidas o caminos libres
        exit_signs = [d for d in detections if 'exit' in d['class'].lower() or 'door' in d['class'].lower()]
        
        if exit_signs:
            for sign in exit_signs:
                center_x = sign['center_x']
                if center_x < frame_width / 3:
                    directions.append("Salida a la izquierda")
                elif center_x > 2 * frame_width / 3:
                    directions.append("Salida a la derecha")
                else:
                    directions.append("Salida al frente")
        
        # Camino libre
        if not detections:
            directions.append("Camino libre, puede avanzar")
        
        return directions
    
    def run(self):
        """Ejecutar el sistema principal"""
        if not self.initialize():
            return
        
        # Intentar conectar a la ESP32
        user_ip = input(f"Ingrese IP de la ESP32-CAM [{ESP32_IP}]: ").strip()
        if user_ip:
            self.video_stream.ip = user_ip
        
        if not self.video_stream.connect():
            print("\n[!] No se pudo conectar a la ESP32-CAM")
            print("    Verifique que:")
            print("    - La ESP32 esté encendida y conectada al WiFi")
            print("    - La IP sea correcta")
            print("    - El puerto 80 esté abierto")
            return
        
        self.running = True
        frame_count = 0
        start_time = time.time()
        
        print("\n[✓] Sistema AURA en ejecución")
        print("    Presione Ctrl+C para detener\n")
        
        try:
            while self.running:
                # Leer frame
                frame = self.video_stream.read_frame()
                
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                height, width = frame.shape[:2]
                
                # Detectar objetos
                detections = self.detector.detect(frame, CONFIDENCE_THRESHOLD)
                
                # Analizar detecciones
                alerts = self.analyze_detections(detections)
                
                # Generar direcciones
                directions = self.generate_directions(detections, width)
                
                # Mostrar resultados en pantalla
                self.display_results(frame, detections, alerts, directions)
                
                # Vocalizar alertas importantes (con debounce)
                current_time = time.time()
                for alert in alerts:
                    if alert not in self.last_announcement or \
                       current_time - self.last_announcement.get(alert, 0) > 10:
                        self.audio.speak(alert)
                        self.last_announcement[alert] = current_time
                
                # FPS counter
                elapsed = time.time() - start_time
                if elapsed > 0:
                    fps = frame_count / elapsed
                    if frame_count % 30 == 0:
                        print(f"[i] FPS: {fps:.1f} | Detecciones: {len(detections)}")
                
        except KeyboardInterrupt:
            print("\n[i] Deteniendo sistema...")
            self.running = False
        finally:
            self.video_stream.stop()
            print("[✓] Sistema detenido")
    
    def display_results(self, frame, detections, alerts, directions):
        """Mostrar resultados en ventana OpenCV"""
        # Dibujar detecciones
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            color = (0, 255, 0)  # Verde por defecto
            
            # Colores por categoría
            if det['class'] == 'person':
                color = (255, 0, 0)  # Azul para personas
            elif det['class'] in ['chair', 'backpack', 'suitcase']:
                color = (0, 165, 255)  # Naranja para obstáculos
            
            # Dibujar bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Etiquetar
            label = f"{det['class']} {det['confidence']:.2f}"
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Mostrar alertas
        y_offset = 30
        for alert in alerts[:5]:  # Máximo 5 alertas
            cv2.putText(frame, alert, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            y_offset += 25
        
        # Mostrar direcciones
        y_offset = frame.shape[0] - 30
        for direction in directions[:3]:  # Máximo 3 direcciones
            cv2.putText(frame, direction, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_offset -= 25
        
        # Mostrar frame
        cv2.imshow('AURA - Vision System', frame)
        
        # Teclas de control
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            self.running = False
        elif key == ord('s'):
            # Capturar foto
            cv2.imwrite(f'capture_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg', frame)
            self.audio.speak("Imagen capturada")


def main():
    """Función principal"""
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║   🌟  AURA - Assistive Urban Rescue Assistant  🌟 ║
    ║                                                   ║
    ║   Sistema de visión artificial para personas      ║
    ║   con discapacidad visual en emergencias          ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    system = AURASystem()
    system.run()


if __name__ == "__main__":
    main()
