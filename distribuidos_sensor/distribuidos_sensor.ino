#include <WiFiNINA.h>
#include <PubSubClient.h>
#include "system.pb.h"  // Arquivo Protobuf gerado pelo Nanopb
#include "pb_encode.h"
#include "pb_decode.h"

const int LDR_PIN = A0;  // Pino do sensor de luminosidade

// WiFi credentials
const char* ssid = "Danilo";
const char* password = "daniloab";

// MQTT Broker details
const char* mqtt_server = "192.168.229.93";  // IP do Broker MQTT (RabbitMQ)
const int mqtt_port = 1883;
const char* mqtt_user = "dan";
const char* mqtt_password = "dan";
const char* mqtt_topic = "sensor/luminosidade";  // Novo formato de tópico

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

void setup() {
  Serial.begin(9600);
  connectToWiFi();
  mqttClient.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();

  // Ler o sensor de luminosidade
  int lightLevel = analogRead(LDR_PIN);

  // Criar mensagem Protobuf
  system_SensorData message = system_SensorData_init_zero;

  // Copiar strings corretamente para arrays char[]
  strncpy(message.device_type, "sensor_luminosidade", sizeof(message.device_type));
  strncpy(message.sensor_id, "ldr_01", sizeof(message.sensor_id));
  message.value = (float)lightLevel;
  strncpy(message.unit, "lux", sizeof(message.unit));
  message.timestamp = millis();  // Usa o tempo desde que o Arduino iniciou

  // Serializar a mensagem Protobuf
  uint8_t buffer[128];  // Buffer para armazenar os dados serializados
  pb_ostream_t stream = pb_ostream_from_buffer(buffer, sizeof(buffer));

  if (!pb_encode(&stream, system_SensorData_fields, &message)) {
    Serial.println("[ERRO] Falha ao codificar mensagem Protobuf!");
    return;
  }

  // Publicar a mensagem no MQTT
  mqttClient.publish(mqtt_topic, buffer, stream.bytes_written);
  Serial.println("[SENSOR] Mensagem enviada via Protobuf!");

  delay(5000);  // Publica a cada 5 segundos
}

void connectToWiFi() {
  Serial.print("Conectando ao WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\n[SENSOR] Conectado ao WiFi.");
  Serial.print("[SENSOR] IP do dispositivo: ");
  Serial.println(WiFi.localIP());
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("[SENSOR] Tentando conectar ao MQTT...");
    if (mqttClient.connect("ArduinoLightSensor", mqtt_user, mqtt_password)) {
      Serial.println(" Conectado ao MQTT broker!");
    } else {
      Serial.print(" Falha, código de erro: ");
      Serial.print(mqttClient.state());
      Serial.println(" Tentando novamente em 5 segundos...");
      delay(5000);
    }
  }
}
