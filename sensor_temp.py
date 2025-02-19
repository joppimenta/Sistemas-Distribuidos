import pika
import time
import random
import system_pb2  # Importa Protobuf para estrutura de mensagens
from config import BROKER_HOST, BROKER_USER, BROKER_PASSWORD

QUEUE_NAME = "sensor_temperatura"

def publish_temperature():
    credentials = pika.PlainCredentials(BROKER_USER, BROKER_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER_HOST, credentials=credentials))
    channel = connection.channel()

    # Criar a fila como durável (mensagens persistentes)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    while True:
        temperature = random.uniform(18.0, 30.0)  # Simula um sensor real
        message = system_pb2.DeviceInfo(
            device_type="sensor_temperatura",
            ip="192.168.1.10",
            port=5001,
            state=str(temperature),
        )

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=message.SerializeToString(),
            properties=pika.BasicProperties(delivery_mode=2)  # Mensagem persistente
        )

        print(f"[SENSOR TEMPERATURA] Publicou: {temperature}°C")
        time.sleep(10)  # Publica a cada 10 segundos

if __name__ == "__main__":
    publish_temperature()
