#include <WiFiNINA.h>       // For WiFi functionality
#include "system.pb.h"      // Include generated Protobuf headers
#include "pb_encode.h"
#include "pb_decode.h"

// Define your WiFi credentials
const char* ssid = "Danilo";
const char* password = "daniloab";

// Gateway details
const char* gateway_ip = "192.168.212.93";  // Updated gateway IP
const int gateway_port = 7000;  // Gateway port for TCP communication

// Device Info
system_DeviceInfo device_info = system_DeviceInfo_init_zero;
WiFiUDP udp;

void setup() {  
    Serial.begin(115200);
    while (!Serial);

    // Connect to WiFi
    connectToWiFi();

    // Populate device info
    strncpy(device_info.device_id, "4", sizeof(device_info.device_id));
    strncpy(device_info.device_type, "Ar-Condicionado", sizeof(device_info.device_type));
    strncpy(device_info.state, "off", sizeof(device_info.state));
    device_info.temperature = 20;  // Initial temperature

    // Start listening for multicast discovery
    if (udp.beginMulticast(IPAddress(224, 0, 0, 1), 10001)) {
        Serial.println("UDP multicast started successfully.");
    } else {
        Serial.println("Failed to start UDP multicast.");
    }
}

void loop() {
    handleUDPCommands();
}

void connectToWiFi() {
    Serial.print("Connecting to WiFi...");
    while (WiFi.begin(ssid, password) != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("Connected!");
}

void handleUDPCommands() {
    int packetSize = udp.parsePacket();
    if (packetSize) {
        uint8_t buffer[128];
        udp.read(buffer, packetSize);

        // Print raw bytes for debugging
        Serial.print("Received raw data: ");
        for (int i = 0; i < packetSize; i++) {
            Serial.print(buffer[i], HEX);
            Serial.print(" ");
        }
        Serial.println();

        // Convert buffer to a string to check prefixes
        char receivedMessage[packetSize + 1];
        memset(receivedMessage, 0, packetSize + 1);
        memcpy(receivedMessage, buffer, packetSize);

        // Check if the message is DISCOVER_DEVICES
        if (strcmp(receivedMessage, "DISCOVER_DEVICES") == 0) {
            sendDeviceInfo();
            Serial.println("Responded to multicast discovery.");
            return;  // Skip further processing
        }

        // Check if the message is COMMAND_MESSAGE
        if (strncmp(receivedMessage, "COMMAND_MESSAGE", 15) == 0) {
            const uint8_t* protobufData = buffer + 15; // Skip the prefix
            size_t protobufLength = packetSize - 15;
            handleCommandMessage(protobufData, protobufLength);
        }
    }
}

void handleCommandMessage(const uint8_t* data, size_t length) {
    // Parse Protobuf message
    pb_istream_t stream = pb_istream_from_buffer(data, length);
    system_DeviceControl control = system_DeviceControl_init_zero;

    if (!pb_decode(&stream, system_DeviceControl_fields, &control)) {
        Serial.print("Decode error: ");
        Serial.println(PB_GET_ERROR(&stream));
        return;
    }

    // Log decoded fields
    Serial.print("Decoded device_id: ");
    Serial.println(control.device_id);

    Serial.print("Decoded action: ");
    Serial.println(control.action);

    Serial.print("Decoded temperature: ");
    Serial.println(control.temperature);

    // Process the command if intended for this device
    if (strcmp(control.device_id, device_info.device_id) == 0) {
        Serial.println("Command intended for this device.");

        if (strcmp(control.action, "ligar") == 0) {
            strncpy(device_info.state, "on", sizeof(device_info.state));
            device_info.temperature = control.temperature;
            Serial.println("Device turned on.");
        } else if (strcmp(control.action, "desligar") == 0) {
            strncpy(device_info.state, "off", sizeof(device_info.state));
            Serial.println("Device turned off.");
        } else {
            Serial.println("Unknown action received.");
        }
    } else {
        Serial.println("Command not intended for this device.");
    }
}

void sendDeviceInfo() {
    // Serialize device info to protobuf
    uint8_t outBuffer[128];
    pb_ostream_t stream = pb_ostream_from_buffer(outBuffer, sizeof(outBuffer));
    if (pb_encode(&stream, system_DeviceInfo_fields, &device_info)) {
        // Send the device info as a UDP packet to the gateway
        udp.beginPacket(gateway_ip, gateway_port);
        udp.write(outBuffer, stream.bytes_written);
        udp.endPacket();
        Serial.println("Device info sent to the gateway.");
    } else {
        Serial.println("Failed to encode device info.");
    }
}
