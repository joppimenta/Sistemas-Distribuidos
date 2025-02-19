import pika
import system_pb2  # Importa as mensagens Protobuf
import threading
from config import BROKER_HOST, BROKER_USER, BROKER_PASSWORD, SENSOR_QUEUES

class Gateway:
    def __init__(self):
        self.sensor_data = {}  # Armazena as últimas leituras dos sensores
        self.setup_connection()

    def setup_connection(self):
        """Conecta-se ao RabbitMQ e assina os tópicos dos sensores."""
        credentials = pika.PlainCredentials(BROKER_USER, BROKER_PASSWORD)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER_HOST, credentials=credentials))
        self.channel = self.connection.channel()

        for queue in SENSOR_QUEUES:
            self.channel.queue_declare(queue=queue, durable=True)
            self.channel.basic_consume(queue=queue, on_message_callback=self.process_sensor_data, auto_ack=True)

        print("[GATEWAY] Conectado ao RabbitMQ e escutando sensores...")

    def process_sensor_data(self, ch, method, properties, body):
        """Processa dados recebidos dos sensores."""
        message = system_pb2.DeviceInfo()
        message.ParseFromString(body)

        self.sensor_data[message.device_type] = message.state
        print(f"[GATEWAY] Recebido de {message.device_type}: {message.state}")

    def start_listening(self):
        """Inicia o consumo de mensagens em uma thread separada."""
        thread = threading.Thread(target=self.channel.start_consuming, daemon=True)
        thread.start()

if __name__ == "__main__":
    gateway = Gateway()
    gateway.start_listening()

    # Mantém o programa rodando
    input("[GATEWAY] Pressione Enter para sair...\n")