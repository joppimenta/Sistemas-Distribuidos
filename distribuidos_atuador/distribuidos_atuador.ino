#include <WiFiNINA.h>

const int LED_PIN = B10;  // Simula um atuador (ex: lâmpada)

// WiFi credentials
// WiFi credentials
const char* ssid = "Danilo";
const char* password = "daniloab";

// Servidor TCP para receber comandos do Gateway
WiFiServer server(50051);

void setup() {
    Serial.begin(9600);
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);  // Garante que o atuador começa desligado

    // Conectar ao WiFi
    Serial.print("[ATUADOR] Conectando ao WiFi...");
    WiFi.begin(ssid, password);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    
    Serial.println("\n[ATUADOR] Conectado ao WiFi!");
    Serial.print("[ATUADOR] IP do dispositivo: ");
    Serial.println(WiFi.localIP());

    // Iniciar o servidor TCP
    server.begin();
    Serial.println("[ATUADOR] Servidor TCP rodando na porta 50051...");
}

void processCommand(WiFiClient client) {
    while (!client.available()) {
        delay(100);
    }

    String command = client.readStringUntil('\n');
    command.trim(); // Remove espaços extras

    Serial.print("[ATUADOR] Comando Recebido: ");
    Serial.println(command);

    if (command == "ligar") {
        digitalWrite(LED_PIN, HIGH);
        Serial.println("[ATUADOR] Ligado!");
        client.println("OK - Ligado");
    } else if (command == "desligar") {
        digitalWrite(LED_PIN, LOW);
        Serial.println("[ATUADOR] Desligado!");
        client.println("OK - Desligado");
    } else {
        Serial.println("[ATUADOR] Comando inválido!");
        client.println("ERRO - Comando inválido");
    }

    client.stop();
}

void loop() {
    WiFiClient client = server.available();
    if (client) {
        Serial.println("[ATUADOR] Conexão recebida do Gateway.");
        processCommand(client);
    }
}