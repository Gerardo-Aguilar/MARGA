/*
 * AURA - ESP32-CAM Firmware
 * Servidor de Streaming de Video + Bluetooth Audio
 * 
 * Hardware: ESP32-CAM (AI-Thinker)
 * Conexiones:
 *   - GPIO 4: Flash LED
 *   - GPIO 0: Boot button (para entrar en modo flash)
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <BluetoothSerial.h>

// ==================== CONFIGURACIÓN WIFI ====================
const char* ssid = "TU_RED_WIFI";
const char* password = "TU_CONTRASEÑA_WIFI";

// ==================== CONFIGURACIÓN CÁMARA ====================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ==================== VARIABLES GLOBALES ====================
BluetoothSerial BT;
String comandoBT = "";
bool streamingActivo = false;

// ==================== FUNCIONES ====================

void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Configuración para mejor calidad/velocidad
  if(psramFound()){
    config.frame_size = FRAMESIZE_SVGA; // 800x600
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QVGA; // 320x240
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }
  
  // Inicializar cámara
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Error de cámara: 0x%x", err);
    return;
  }
  
  sensor_t * s = esp_camera_sensor_get();
  s->set_brightness(s, 0);
  s->set_contrast(s, 0);
  s->set_saturation(s, 0);
  s->set_gainceiling(s, (gainceiling_t)0);
  s->set_colorbar(s, 0);
  s->set_whitebal(s, 1);
  s->set_aec2(s, 1);
  s->set_awb_gain(s, 1);
  s->set_agc_gain(s, 0);
  s->set_raw_gma(s, 1);
  s->set_lenc(s, 1);
  s->set_hmirror(s, 1); // Espejo horizontal
  s->set_vflip(s, 0);   // Sin volteo vertical
  
  Serial.println("Cámara inicializada correctamente");
}

void connectWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void setupBluetooth() {
  BT.begin("AURA-ESP32");
  Serial.println("Bluetooth iniciado: AURA-ESP32");
}

void processBluetoothCommand(String cmd) {
  cmd.toLowerCase();
  
  if (cmd.indexOf("iniciar") >= 0 || cmd.indexOf("start") >= 0) {
    streamingActivo = true;
    BT.println("STREAM_INICIADO");
    Serial.println("Streaming iniciado por Bluetooth");
  }
  else if (cmd.indexOf("detener") >= 0 || cmd.indexOf("stop") >= 0) {
    streamingActivo = false;
    BT.println("STREAM_DETENIDO");
    Serial.println("Streaming detenido por Bluetooth");
  }
  else if (cmd.indexOf("foto") >= 0 || cmd.indexOf("capture") >= 0) {
    captureAndSendPhoto();
  }
  else if (cmd.indexOf("ayuda") >= 0 || cmd.indexOf("help") >= 0) {
    BT.println("COMANDOS: iniciar, detener, foto, ayuda");
  }
}

void captureAndSendPhoto() {
  camera_fb_t * fb = NULL;
  fb = esp_camera_fb_get();
  
  if (!fb) {
    BT.println("ERROR_FOTO");
    return;
  }
  
  // Enviar tamaño primero
  BT.write(0xFF); // Marker
  BT.write(0xD8); // SOI
  BT.write((fb->len >> 8) & 0xFF);
  BT.write(fb->len & 0xFF);
  
  // Enviar datos JPEG
  for (size_t i = 0; i < fb->len; i++) {
    BT.write(fb->buf[i]);
  }
  
  esp_camera_fb_return(fb);
  BT.println("FOTO_ENVIADA");
}

void streamVideo() {
  camera_fb_t * fb = NULL;
  
  fb = esp_camera_fb_get();
  if (!fb) {
    return;
  }
  
  // Enviar frame con header
  BT.write(0xFF); // Start marker
  BT.write(0xD8); // JPEG SOI
  BT.write((fb->len >> 24) & 0xFF);
  BT.write((fb->len >> 16) & 0xFF);
  BT.write((fb->len >> 8) & 0xFF);
  BT.write(fb->len & 0xFF);
  
  // Enviar datos
  for (size_t i = 0; i < fb->len; i++) {
    BT.write(fb->buf[i]);
  }
  
  esp_camera_fb_return(fb);
}

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  
  pinMode(4, OUTPUT);
  digitalWrite(4, LOW); // Apagar flash
  
  setupCamera();
  connectWiFi();
  setupBluetooth();
  
  Serial.println("\n=== AURA SYSTEM READY ===");
  Serial.println("Esperando comandos Bluetooth...");
}

// ==================== LOOP ====================
void loop() {
  // Leer comandos Bluetooth
  while (BT.available()) {
    char c = BT.read();
    if (c == '\n' || c == '\r') {
      if (comandoBT.length() > 0) {
        processBluetoothCommand(comandoBT);
        comandoBT = "";
      }
    } else {
      comandoBT += c;
    }
  }
  
  // Streaming de video si está activo
  if (streamingActivo) {
    streamVideo();
    delay(100); // ~10 FPS
  }
  
  delay(10);
}
