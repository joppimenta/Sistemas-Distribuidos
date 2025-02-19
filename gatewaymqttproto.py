import paho.mqtt.client as mqtt
import system_pb2  # Importa Protobuf
from config import BROKER_HOST, BROKER_USER, BROKER_PASSWORD

TOPIC = "sensor/luminosidade"  # Certifique-se de que é o mesmo usado no Arduino

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
        """Processa dados recebidos dos sensores (em Protobuf)."""
        try:
            data = message.payload  # Mantemos os dados como bytes (NÃO FAÇA `.decode()`)
            print(f"[GATEWAY] Mensagem recebida (bruta): {data}")

            # Criar objeto Protobuf
            sensor_message = system_pb2.SensorData()
            sensor_message.ParseFromString(data)  # Decodifica Protobuf

            # Armazena os dados recebidos
            self.sensor_data[sensor_message.sensor_id] = {
                "tipo": sensor_message.device_type,
                "valor": sensor_message.value,
                "unidade": sensor_message.unit,
                "timestamp": sensor_message.timestamp
            }

            # Exibe os dados corretamente
            print(f"[GATEWAY] Sensor: {sensor_message.sensor_id}")
            print(f"[GATEWAY] Tipo: {sensor_message.device_type}")
            print(f"[GATEWAY] Valor: {sensor_message.value} {sensor_message.unit}")
            print(f"[GATEWAY] Timestamp: {sensor_message.timestamp}")

        except Exception as e:
            print(f"[ERRO] Falha ao processar mensagem Protobuf: {e}")

    def start_listening(self):
        """Inicia o consumo de mensagens MQTT."""
        print("[GATEWAY] Aguardando mensagens dos sensores...")
        self.client.loop_forever()

if __name__ == "__main__":
    gateway = Gateway()
    gateway.start_listening()
