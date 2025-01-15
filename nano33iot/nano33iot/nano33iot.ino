#include <WiFiNINA.h>       // For WiFi functionality
#include "system.pb.h"      // Include generated Protobuf headers
#include "pb_encode.h"
#include "pb_decode.h"

// Define your WiFi credentials
const char* ssid = "brisa-2593962";
const char* password = "cdnf30li";

// Gateway details
const char* gateway_ip = "192.168.0.16";  // Updated gateway IP
const int gateway_port = 7000;  // Gateway port for TCP communication

// Device Info
system_DeviceInfo device_info = system_DeviceInfo_init_default;
WiFiUDP udp;

// Helper function to set string fields in Nanopb
bool set_string_field(pb_callback_t* field, const char* value) {
    field->funcs.encode = &pb_encode_string;
    field->arg = (void*)value;
    return true;
}

// Callback function for encoding strings in Nanopb
bool pb_encode_string(pb_ostream_t* stream, const pb_field_t* field, void* const* arg) {
    const char* str = (const char*)(*arg);
    if (!pb_encode_tag_for_field(stream, field)) {
        return false;
    }
    return pb_encode_string(stream, (uint8_t*)str, strlen(str));
}

void setup() {  
    Serial.begin(115200);
    while (!Serial);

    // Connect to WiFi
    connectToWiFi();

    // Populate device info
    set_string_field(&device_info.device_id, "4");  // Example device ID
    set_string_field(&device_info.device_type, "Ar-Condicionado");  // Device type
    set_string_field(&device_info.state, "off");  // Initial state
    device_info.temperature = 20.0;  // Initial temperature

    // Start listening for multicast discovery
    if (udp.beginMulticast(IPAddress(224, 0, 0, 1), 10001)) {
    Serial.println("UDP multicast started successfully.");
    } 
    else {
        Serial.println("Failed to start UDP multicast.");
    }
}

void loop() {
    // Handle UDP commands (both discovery and control)
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

        // Convert buffer to a string to check if it's a DISCOVER_DEVICES message
        char receivedMessage[packetSize + 1];
        memset(receivedMessage, 0, packetSize + 1);
        memcpy(receivedMessage, buffer, packetSize);

        // Check if the message is DISCOVER_DEVICES
        if (strcmp(receivedMessage, "DISCOVER_DEVICES") == 0) {
            // Handle the DISCOVER_DEVICES message (send device info back)
            sendDeviceInfo();
            Serial.println("Responded to multicast discovery.");
            return;  // Skip control message processing
        }

        // Handle the control message (turn on/off lamp, change temperature)
        system_DeviceControl control = system_DeviceControl_init_default;
        pb_istream_t stream = pb_istream_from_buffer(buffer, packetSize);

        if (pb_decode(&stream, system_DeviceControl_fields, &control)) {
            const char* action = (const char*)(control.action.arg);
            if (strcmp(action, "ligar") == 0) {
                set_string_field(&device_info.state, "on");
                device_info.temperature = control.temperature;
                Serial.println("Lamp turned on.");
            } else if (strcmp(action, "desligar") == 0) {
                set_string_field(&device_info.state, "off");
                Serial.println("Lamp turned off.");
            }
        } else {
            Serial.println("Failed to decode control message.");
        }
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
