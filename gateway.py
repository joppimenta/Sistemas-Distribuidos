import socket
import struct
import system_pb2  # Arquivo gerado a partir de system.proto
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import paho.mqtt.client as mqtt  # Import MQTT library


class Gateway:
    def __init__(self, ip, port, multicast_group, multicast_port, mqtt_endpoint):
        self.ip = ip
        self.port = port
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.mqtt_endpoint = mqtt_endpoint
        self.devices = {}  # Armazena os dispositivos identificados
        self.lock = threading.Lock()  # Para acesso seguro à lista de dispositivos

        # Initialize MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.connect(self.mqtt_endpoint, 8883)  # Replace with your AWS IoT endpoint
        self.mqtt_client.loop_start()

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker")
            # Subscribe to topics here if needed
            self.mqtt_client.subscribe("gateway/commands")
        else:
            print(f"MQTT Connection failed with code {rc}")

    def on_mqtt_message(self, client, userdata, msg):
        print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
        # Handle incoming messages (e.g., commands to control devices)

    def send_to_mqtt(self, topic, message):
        """Publish a message to AWS IoT Core."""
        try:
            self.mqtt_client.publish(topic, message)
            print(f"Published message to topic {topic}: {message}")
        except Exception as e:
            print(f"Failed to publish MQTT message: {e}")

    def send_multicast_discovery(self):
        """Envia mensagem multicast para descobrir dispositivos inteligentes."""
        multicast_message = "DISCOVER_DEVICES".encode()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as multicast_socket:
            multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            multicast_socket.sendto(multicast_message, (self.multicast_group, self.multicast_port))
        print("Mensagem multicast de descoberta enviada.")

    def listen_for_device_responses(self):
        """Escuta respostas dos dispositivos após envio do multicast."""
        # Code remains unchanged

    def handle_client(self, client_socket):
        """Handles client connections."""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                if data == b"LIST_DEVICES":
                    # Envia a lista de dispositivos conectados
                    with self.lock:
                        devices_list = "\n".join(
                            [f"ID: {dev.device_id}, Tipo: {dev.device_type}, Estado: {dev.state}, "
                             f"Temperatura: {dev.temperature if dev.device_type == 'Ar-Condicionado' else 'N/A'}"
                             for dev in self.devices.values()]
                        )
                    client_socket.sendall(devices_list.encode())
                else:
                    # Handle other commands and send to MQTT if necessary
                    self.send_to_mqtt("gateway/updates", data.decode())
        except Exception as e:
            print(f"Erro no processamento do cliente: {e}")
        finally:
            client_socket.close()

    def start(self):
        """Starts the gateway."""
        # Code remains unchanged


if __name__ == "__main__":
    gateway = Gateway(
        ip="192.168.18.45",
        port=5000,
        multicast_group="224.0.0.1",
        multicast_port=10001,
        mqtt_endpoint="your_aws_endpoint"
    )
    gateway.start()
