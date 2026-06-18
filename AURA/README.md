# AURA - Assistive Urban Rescue Assistant

Sistema de visión artificial para mejorar la seguridad de personas ciegas durante situaciones de emergencia en edificios públicos.

## 🌟 Descripción

AURA utiliza una arquitectura Cliente-Servidor donde:
- **ESP32-CAM**: Captura video y lo envía vía WiFi
- **PC/Laptop**: Ejecuta Python + OpenCV + YOLOv8 para detectar objetos y generar audio
- **Bluetooth**: Conecta el PC con auriculares del usuario para comunicación bidireccional

## 📋 Requisitos de Hardware

### ESP32-CAM
- Módulo ESP32-CAM (AI-Thinker)
- Cable FTDI para programación
- Fuente de alimentación 5V estable
- Antena WiFi (opcional pero recomendada)

### Host (PC/Laptop)
- Python 3.8+
- Bluetooth integrado o dongle USB
- Webcam (opcional, para pruebas sin ESP32)

## 🚀 Instalación

### 1. Configurar el entorno Python

```bash
# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Programar la ESP32-CAM

#### Opción A: Arduino IDE
1. Instalar Arduino IDE
2. Agregar URL de boards ESP32:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Instalar board "ESP32 Dev Module" desde Board Manager
4. Abrir `firmware/aura_esp32cam.ino`
5. Configurar WiFi:
   ```cpp
   const char* ssid = "TU_RED_WIFI";
   const char* password = "TU_CONTRASEÑA_WIFI";
   ```
6. Seleccionar board: **AI Thinker ESP32-CAM**
7. Subir código

#### Opción B: PlatformIO (VS Code)
```bash
# En VS Code, instalar extensión PlatformIO
# Crear nuevo proyecto ESP32
# Copiar contenido de firmware/aura_esp32cam.ino
```

### 3. Configurar el sistema

1. Encender ESP32-CAM
2. Anotar la IP que muestra en el Serial Monitor
3. Ejecutar el host:
   ```bash
   python src/aura_host.py
   ```
4. Ingresar la IP de la ESP32 cuando se solicite

## 🔧 Configuración

### Firmware ESP32-CAM

Editar `firmware/aura_esp32cam.ino`:
```cpp
const char* ssid = "TuRedWiFi";
const char* password = "TuContraseña";
```

### Host Python

Editar `src/aura_host.py`:
```python
ESP32_IP = "192.168.1.100"  # IP de tu ESP32
YOLO_MODEL = "yolov8n.pt"   # Modelo ligero (n=nano, s=small, m=medium)
CONFIDENCE_THRESHOLD = 0.5  # Umbral de detección
```

## 🎯 Objetos Detectables

El sistema detecta automáticamente:
- **Personas**: Detección de caídas, presencia humana
- **Obstáculos**: Sillas, mochilas, maletas, plantas
- **Señales**: Puertas, salidas (si están en el modelo)
- **Peligros**: Fuego, humo (con modelos entrenados)

## 💬 Comandos de Voz

El usuario puede preguntar:
- "¿Hay personas caídas?"
- "¿Dónde está la salida?"
- "¿Hay fuego?"
- "¿Hay escaleras?"
- "Describe el entorno"

## 🔌 Conexión Bluetooth

### Windows
1. Emparejar auricular Bluetooth con el PC
2. Configurar como dispositivo de audio predeterminado
3. El sistema usará automáticamente la salida de audio

### Linux
```bash
# Instalar pulseaudio si no está
sudo apt install pulseaudio pulseaudio-utils

# Conectar dispositivo Bluetooth
bluetoothctl
scan on
pair [MAC_ADDRESS]
connect [MAC_ADDRESS]
```

## 🎮 Uso

### Iniciar el sistema
```bash
python src/aura_host.py
```

### Controles en pantalla
- **Q**: Salir del programa
- **S**: Capturar imagen
- Espacio: Pausar/reanudar

### Comandos Bluetooth desde ESP32
- `iniciar`: Iniciar streaming de video
- `detener`: Detener streaming
- `foto`: Capturar foto
- `ayuda`: Listar comandos disponibles

## 🏗️ Arquitectura

```
┌─────────────┐      WiFi       ┌──────────────┐    Bluetooth    ┌──────────┐
│  ESP32-CAM  │ ◄────────────► │   PC/Laptop  │ ◄────────────► │ Auricular│
│             │   Video Stream  │              │   Audio/TTS    │          │
│  • Cámara   │                 │  • Python    │                 │  Usuario │
│  • WiFi     │                 │  • YOLOv8    │                 │          │
│  • BT       │                 │  • OpenCV    │                 │          │
└─────────────┘                 └──────────────┘                 └──────────┘
```

## ⚙️ Personalización

### Cambiar modelo YOLO
```python
# Modelos disponibles (más preciso = más lento)
YOLO_MODEL = "yolov8n.pt"  # Nano (más rápido)
YOLO_MODEL = "yolov8s.pt"  # Small
YOLO_MODEL = "yolov8m.pt"  # Medium
YOLO_MODEL = "yolov8l.pt"  # Large
```

### Entrenar modelo personalizado
Para detectar señales específicas de tu edificio:
```bash
# Ver documentación de Ultralytics
https://docs.ultralytics.com/modes/train/
```

### Ajustar sensibilidad
```python
CONFIDENCE_THRESHOLD = 0.3  # Más bajo = más detecciones (más falsos positivos)
CONFIDENCE_THRESHOLD = 0.7  # Más alto = menos detecciones (más preciso)
```

## 🐛 Solución de Problemas

### ESP32 no se conecta al WiFi
- Verificar SSID y contraseña
- Acercar al router
- Usar alimentación externa de 5V

### No hay video en el host
- Verificar IP de la ESP32
- Confirmar que el streaming esté activo
- Revisar firewall del PC

### Detecciones lentas
- Usar modelo más pequeño (yolov8n)
- Reducir resolución de cámara
- Usar GPU si está disponible

### Audio no funciona
- Verificar que pyttsx3 esté instalado
- Chequear configuración de audio del sistema
- En Linux: `sudo apt install espeak`

## 📁 Estructura del Proyecto

```
AURA/
├── firmware/
│   └── aura_esp32cam.ino    # Código para ESP32-CAM
├── src/
│   └── aura_host.py         # Sistema principal Python
├── config/
│   └── (configuraciones)    # Futuras configuraciones
├── requirements.txt         # Dependencias Python
└── README.md               # Este archivo
```

## 🔐 Seguridad y Privacidad

- El video NO se almacena por defecto
- Las imágenes capturadas son locales
- No hay conexión a internet externa
- Todo el procesamiento es local

## 🤝 Contribuciones

Este proyecto es open-source. Contribuciones bienvenidas:
- Mejoras en detección de objetos
- Nuevos comandos de voz
- Optimizaciones de rendimiento
- Soporte para más hardware

## 📄 Licencia

MIT License - Ver archivo LICENSE

## 👥 Autores

Proyecto AURA - Asistente de Rescate Urbano Asistivo

---

**Nota**: Este sistema es una herramienta de asistencia. No reemplaza la supervisión humana ni los protocolos de emergencia establecidos.
