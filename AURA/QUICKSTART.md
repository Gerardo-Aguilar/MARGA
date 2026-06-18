# AURA - Guía de Instalación Rápida

## 🚀 Inicio Rápido (5 minutos)

### Paso 1: Instalar dependencias Python

```bash
cd AURA
chmod +x install.sh
./install.sh
```

O manualmente:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Paso 2: Programar ESP32-CAM

**Opción A - Arduino IDE:**

1. Instalar Arduino IDE desde https://www.arduino.cc/en/software
2. Agregar soporte ESP32:
   - Ir a `Archivo > Preferencias`
   - En "URLs adicionales de Gestor de Placas" agregar:
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
3. Instalar board ESP32:
   - `Herramientas > Placa > Gestor de Placas`
   - Buscar "ESP32" e instalar "ESP32 by Espressif Systems"
4. Conectar ESP32-CAM al PC con cable FTDI
5. Abrir `firmware/aura_esp32cam.ino`
6. Editar WiFi:
   ```cpp
   const char* ssid = "TU_RED";
   const char* password = "TU_CLAVE";
   ```
7. Seleccionar placa: `Herramientas > Placa > ESP32 > AI Thinker ESP32-CAM`
8. Subir código (mantener GPIO 0 a GND durante subida)

**Opción B - PlatformIO:**

```bash
# Instalar VS Code y extensión PlatformIO
# Abrir carpeta AURA en VS Code
# PlatformIO detectará platformio.ini automáticamente
# Click en "Upload"
```

### Paso 3: Ejecutar sistema

1. Encender ESP32-CAM (alimentación 5V)
2. Abrir Serial Monitor (115200 baud) para ver la IP
3. Ejecutar en PC:
   ```bash
   source venv/bin/activate
   python src/aura_host.py
   ```
4. Ingresar la IP de la ESP32 cuando se solicite
5. ¡Listo! El sistema comenzará a detectar objetos

## 🔧 Configuración Bluetooth

### Windows
1. Emparejar auricular Bluetooth con el PC
2. El audio saldrá automáticamente por el dispositivo conectado

### Linux
```bash
bluetoothctl
power on
scan on
pair XX:XX:XX:XX:XX:XX  # MAC de tu auricular
connect XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
```

## ✅ Verificación

El sistema está funcionando si ves:
- ✓ Ventana con video de la cámara
- ✓ Rectángulos alrededor de objetos detectados
- ✓ Alertas en pantalla
- ✓ Audio describiendo el entorno

## 🐛 Problemas Comunes

### "No module named 'cv2'"
```bash
pip install opencv-python
```

### "No module named 'ultralytics'"
```bash
pip install ultralytics
```

### ESP32 no conecta al WiFi
- Verificar SSID y contraseña (distingue mayúsculas)
- Acercar al router
- Usar alimentación externa de 5V (no solo USB)

### Video lento
- Cambiar a modelo YOLO más pequeño en `aura_host.py`:
  ```python
  YOLO_MODEL = "yolov8n.pt"  # Más rápido
  ```

### No hay audio
- Verificar volumen del sistema
- En Linux: `sudo apt install espeak`
- Revisar que el auricular esté conectado

## 📱 Comandos Disponibles

### Por Bluetooth (desde app de terminal):
- `iniciar` - Iniciar streaming
- `detener` - Detener streaming
- `foto` - Capturar foto
- `ayuda` - Listar comandos

### Por Voz (hablando al micrófono):
- "¿Dónde está la salida?"
- "¿Hay personas?"
- "¿Hay fuego?"
- "Describe el entorno"
- "Ayuda"

## 🎯 Siguientes Pasos

1. **Personalizar detecciones**: Editar lista de objetos en `aura_host.py`
2. **Entrenar modelo propio**: Para detectar señales específicas de tu edificio
3. **Mejorar audio**: Configurar voz y velocidad en `AudioFeedback` class
4. **Agregar más sensores**: Integrar ultrasónico para distancia de obstáculos

## 📞 Soporte

Para más información, ver el README.md completo.

---

**¡Tu sistema AURA está listo para ayudar!** 🌟
