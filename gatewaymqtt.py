import paho.mqtt.client as mqtt
import system_pb2  # Importa as mensagens Protobuf
import json
from config import BROKER_HOST, BROKER_USER, BROKER_PASSWORD

TOPIC = "sensor_luminosidade"  # Certifique-se de que é o mesmo usado no Arduino

class Gateway:
    def __init__(self):
        self.sensor_data = {}
        self.setup_mqtt()

    def setup_mqtt(self):
        """Configura a conexão MQTT com o RabbitMQ."""
        self.client = mqtt.Client()
        self.client.username_pw_set(BROKER_USER, BROKER_PASSWORD)
        self.client.on_message = self.process_sensor_data

        try:
            self.client.connect(BROKER_HOST, 1883, 60)
            print("[GATEWAY] Conectado ao MQTT Broker")
            self.client.subscribe(TOPIC)
        except Exception as e:
            print(f"[ERRO] Falha ao conectar ao MQTT Broker: {e}")

    def process_sensor_data(self, client, userdata, message):
        """Processa dados recebidos dos sensores."""
        try:
            data = message.payload.decode()  # Decodifica a mensagem
            print(f"[GATEWAY] Mensagem recebida: {data}")

            # Converte JSON para Protobuf (se necessário)
            sensor_message = system_pb2.DeviceInfo()
            sensor_message.ParseFromString(data)

            self.sensor_data[sensor_message.device_type] = sensor_message.state
            print(f"[GATEWAY] Recebido de {sensor_message.device_type}: {sensor_message.state}")

        except Exception as e:
            print(f"[ERRO] Falha ao processar mensagem: {e}")

    def start_listening(self):
        """Inicia o consumo de mensagens MQTT."""
        print("[GATEWAY] Aguardando mensagens dos sensores...")
        self.client.loop_forever()

if __name__ == "__main__":
    gateway = Gateway()
    gateway.start_listening()
