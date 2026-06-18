#!/bin/bash

# AURA - Script de Instalación y Configuración
# Este script instala todas las dependencias necesarias

echo "╔═══════════════════════════════════════════════════╗"
echo "║                                                   ║"
echo "║   🌟  AURA - Instalador del Sistema            🌟 ║"
echo "║                                                   ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Verificar Python
print_info "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "$PYTHON_VERSION detectado"
else
    print_error "Python 3 no encontrado. Por favor instálalo primero."
    exit 1
fi

# Crear entorno virtual
print_info "Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Entorno virtual creado"
else
    print_info "El entorno virtual ya existe"
fi

# Activar entorno virtual
print_info "Activando entorno virtual..."
source venv/bin/activate
print_success "Entorno activado"

# Actualizar pip
print_info "Actualizando pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip actualizado"

# Instalar dependencias principales
print_info "Instalando dependencias de Python..."
pip install opencv-python numpy ultralytics pyttsx3

if [ $? -eq 0 ]; then
    print_success "Dependencias instaladas correctamente"
else
    print_error "Error instalando dependencias"
    exit 1
fi

# Descargar modelo YOLO por defecto
print_info "Descargando modelo YOLOv8 nano..."
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" 2>/dev/null
print_success "Modelo YOLO listo"

# Verificar OpenCV
print_info "Verificando OpenCV..."
python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"

# Crear directorios necesarios
print_info "Creando estructura de directorios..."
mkdir -p captures logs config
print_success "Directorios creados"

# Mostrar resumen
echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║                                                   ║"
echo "║        ✅ Instalación Completada Exitosamente     ║"
echo "║                                                   ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
echo "Próximos pasos:"
echo "1. Configura tu ESP32-CAM con el firmware en firmware/aura_esp32cam.ino"
echo "2. Edita src/aura_host.py y configura la IP de tu ESP32"
echo "3. Ejecuta: python src/aura_host.py"
echo ""
echo "Para activar el entorno virtual en el futuro:"
echo "  source venv/bin/activate"
echo ""
print_info "¡Sistema AURA listo para usar!"
