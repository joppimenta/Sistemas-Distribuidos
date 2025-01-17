#include <WiFiNINA.h>        // For WiFi functionality
#include "system.pb.h"       // Include generated Protobuf headers
#include "pb_encode.h"
#include "pb_decode.h"

// Define your WiFi credentials
const char* ssid = "Danilo";
const char* password = "daniloab";

// Gateway details
const char* gateway_ip = "192.168.212.93";  // Updated gateway IP
const int gateway_port = 5000;  // Gateway port for TCP communication

WiFiClient client;

// Button configuration
const int buttonPin = 7;  // GPIO pin for the button
bool buttonState = false; // Current button state
bool lastButtonState = false; // Previous button state
bool device_on = false; // State of the device

void setup() {
    Serial.begin(115200);
    while (!Serial);

    // Configure the button pin as input with pull-up
    pinMode(buttonPin, INPUT);

    // Connect to WiFi
    connectToWiFi();

    // Connect to Gateway
    connectToGateway();
}

void connectToWiFi() {
    Serial.print("Connecting to WiFi...");
    while (WiFi.begin(ssid, password) != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi!");
}

void connectToGateway() {
    while (!client.connect(gateway_ip, gateway_port)) {
        Serial.println("Connecting to Gateway...");
        delay(1000); // Retry every second
    }
    Serial.println("Connected to Gateway!");
}

void sendControlCommand(const char* device_id, const char* action, int temperature = -1) {
    if (client.connected()) {
        Serial.println("Sending command to Gateway.");

        // Create and populate the DeviceControl message
        system_DeviceControl control_message = system_DeviceControl_init_zero;
        strncpy(control_message.device_id, device_id, sizeof(control_message.device_id));
        strncpy(control_message.action, action, sizeof(control_message.action));
        if (temperature != -1) {
            control_message.temperature = temperature;
        }

        // Serialize the message
        uint8_t buffer[128];
        pb_ostream_t stream = pb_ostream_from_buffer(buffer, sizeof(buffer));
        if (!pb_encode(&stream, system_DeviceControl_fields, &control_message)) {
            Serial.println("Failed to encode control message.");
            return;
        }

        // Send the serialized message
        client.write(buffer, stream.bytes_written);
        client.flush();
        Serial.println("Command sent to Gateway.");
    } else {
        Serial.println("Failed to send command. Not connected to Gateway.");
    }
}

void sendListDevicesCommand() {
    if (client.connected()) {
        Serial.println("Sending LIST_DEVICES command to Gateway.");
        client.write("LIST_DEVICES");
        client.flush();

        // Wait for response
        while (client.connected() && client.available() == 0) {
            delay(100); // Wait for response
        }

        if (client.available() > 0) {
            uint8_t response[512];
            int len = client.read(response, sizeof(response) - 1);
            response[len] = '\0'; // Null-terminate for safe printing
            Serial.println("Received device list:");
            Serial.println((char*)response);
        }
    } else {
        Serial.println("Failed to send LIST_DEVICES. Not connected to Gateway.");
    }
}

void loop() {
    // Reconnect to the gateway if the connection is lost
    if (!client.connected()) {
        Serial.println("Connection to Gateway lost. Reconnecting...");
        connectToGateway();
    }

    // Check for button press
    buttonState = digitalRead(buttonPin);

    // Send a command on button press
    if (buttonState == HIGH && lastButtonState == LOW) { // Detect button press (active low)
        if (device_on == false){
          sendControlCommand("4", "ligar"); // Example: Turn on a device with ID "3"
          device_on == true;
          Serial.println("Button pressed! Sending command 'ligar'.");
        }
        else if (device_on == true){
          sendControlCommand("4", "desligar"); // Example: Turn on a device with ID "3"
          device_on == false;
          Serial.println("Button pressed! Sending command 'desligar'.");
        }
    }

    lastButtonState = buttonState; // Update button state

    // Add a small delay to debounce the button
    delay(100);
}
