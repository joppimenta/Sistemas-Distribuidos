import paho.mqtt.client as mqtt
import system_pb2  # Importa a definição do Protobuf
import time
import random
from config import BROKER_HOST, BROKER_USER, BROKER_PASSWORD

# Configuração do MQTT
TOPIC = "sensor/temperatura"
MQTT_PORT = 1883

# Função para conectar ao MQTT Broker
def connect_mqtt():
    client = mqtt.Client()
    client.username_pw_set(BROKER_USER, BROKER_PASSWORD)
    client.connect(BROKER_HOST, MQTT_PORT, 60)
    return client

# Função para gerar e publicar leituras simuladas
def publish_temperature(client):
    while True:
        # Gerar uma temperatura entre 20°C e 30°C
        temperature = round(random.uniform(20.0, 30.0), 2)

        # Criar a mensagem Protobuf
        message = system_pb2.SensorData()
        message.device_type = "sensor_temperatura"
        message.sensor_id = "temp_01"
        message.value = temperature
        message.unit = "°C"
        message.timestamp = int(time.time())  # Timestamp UNIX

        # Serializar a mensagem
        serialized_message = message.SerializeToString()

        # Publicar no tópico MQTT
        client.publish(TOPIC, serialized_message)
        print(f"[SENSOR] Publicado: {temperature}°C no tópico {TOPIC}")

        time.sleep(5)  # Publica a cada 5 segundos

# Configuração e execução do sensor
if __name__ == "__main__":
    client = connect_mqtt()
    publish_temperature(client)
