import paho.mqtt.client as mqtt
import grpc
import system_pb2
import system_pb2_grpc
import time
from flask import Flask, jsonify, request
from config import BROKER_HOST, BROKER_USER, BROKER_PASSWORD
import threading

# Configuração do Servidor Intermediário gRPC
ACTUATOR_IP = "localhost"
ACTUATOR_PORT = 50052

# Tópicos MQTT para Sensores e seus respectivos IDs internos
TOPICS = {
    "sensor/temperatura": "temp_01",
    "sensor/luminosidade": "ldr_01"
}
MQTT_PORT = 1883

app = Flask(__name__)

class Gateway:
    def __init__(self):
        self.sensor_data = {}  # Armazena os últimos valores dos sensores
        self.atuadores = {
            "lampada": "lampada_1",
            "motor": "motor_1"
        }
        self.setup_mqtt()
        self.setup_grpc()

    def setup_mqtt(self):
        """Configura a conexão MQTT e se inscreve nos tópicos."""
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(BROKER_USER, BROKER_PASSWORD)
        self.mqtt_client.on_message = self.process_sensor_data
        
        try:
            self.mqtt_client.connect(BROKER_HOST, MQTT_PORT, 60)
            self.mqtt_client.subscribe([(topic, 0) for topic in TOPICS.keys()])
            self.mqtt_client.loop_start()
            print(f"[GATEWAY] Inscrito nos tópicos: {list(TOPICS.keys())}")
        except Exception as e:
            print(f"[ERRO] Falha ao conectar ao MQTT Broker: {e}")

    def setup_grpc(self):
        """Configura a comunicação com o Servidor Intermediário gRPC."""
        self.grpc_channel = grpc.insecure_channel(f"{ACTUATOR_IP}:{ACTUATOR_PORT}")
        self.grpc_stub = system_pb2_grpc.ActuatorStub(self.grpc_channel)

    def process_sensor_data(self, client, userdata, message):
        """Processa dados recebidos dos sensores via MQTT e Protobuf."""
        try:
            sensor_message = system_pb2.SensorData()
            sensor_message.ParseFromString(message.payload)

            topic = message.topic  # Ex: "sensor/temperatura"
            sensor_id = TOPICS.get(topic, sensor_message.sensor_id)  # Obtém o ID correto

            # Armazena os dados corretamente no dicionário
            self.sensor_data[sensor_id] = {
                "tipo": sensor_message.device_type,
                "valor": sensor_message.value,
                "unidade": sensor_message.unit,
                "timestamp": sensor_message.timestamp
            }

            print(f"[GATEWAY] Sensor atualizado: {sensor_id} ({sensor_message.device_type}) -> {sensor_message.value} {sensor_message.unit}")

        except Exception as e:
            print(f"[ERRO] Falha ao processar mensagem Protobuf: {e}")

    def enviar_comando(self, dispositivo, acao):
        """Envia um comando via gRPC para o Servidor Intermediário."""
        if dispositivo not in self.atuadores:
            return {"erro": "Dispositivo desconhecido"}

        atuador_id = self.atuadores[dispositivo]

        try:
            request = system_pb2.ActuatorCommand(
                device_type=dispositivo,
                actuator_id=atuador_id,
                action=acao,
                value=0
            )

            response = self.grpc_stub.ExecuteCommand(request)
            print(f"[GATEWAY] Atuador ({atuador_id}): {response.status}")

            return {"dispositivo": atuador_id, "status": response.status}

        except Exception as e:
            print(f"[ERRO] Falha ao enviar comando gRPC: {e}")
            return {"erro": "Falha ao comunicar com o atuador"}

    def listar_sensores(self):
        """Retorna todos os sensores armazenados atualmente."""
        return self.sensor_data

gateway = Gateway()

### **Rotas da API**

@app.route("/dispositivos", methods=["GET"])
def listar_dispositivos():
    """Retorna todos os sensores disponíveis."""
    return jsonify(gateway.listar_sensores())

@app.route("/dispositivos/<string:nome>/ligar", methods=["POST"])
def ligar_dispositivo(nome):
    """Liga um atuador."""
    resultado = gateway.enviar_comando(nome, "ligar")
    return jsonify(resultado)

@app.route("/dispositivos/<string:nome>/desligar", methods=["POST"])
def desligar_dispositivo(nome):
    """Desliga um atuador."""
    resultado = gateway.enviar_comando(nome, "desligar")
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)
