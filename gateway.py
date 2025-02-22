import paho.mqtt.client as mqtt
import grpc
import system_pb2
import system_pb2_grpc
import time
from flask import Flask, request, jsonify
from config import BROKER_HOST, BROKER_USER, BROKER_PASSWORD
import threading

# Configuração do Servidor Intermediário gRPC
ACTUATOR_IP = "localhost"  # O servidor intermediário deve rodar na mesma máquina do Gateway
ACTUATOR_PORT = 50052  # Porta do Servidor Intermediário gRPC

# Tópicos MQTT para Sensores
TOPICS = [("sensor/temperatura", 0), ("sensor/luminosidade", 0)]
MQTT_PORT = 1883

app = Flask(__name__)

class Gateway:
    def __init__(self):
        self.sensor_data = {}
        self.atuadores = {
            "1": "lampada",
            "2": "motor"
        }
        self.setup_mqtt()
        self.setup_grpc()

    def setup_mqtt(self):
        """Configura a conexão MQTT com o RabbitMQ."""
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(BROKER_USER, BROKER_PASSWORD)
        self.mqtt_client.on_message = self.process_sensor_data

        try:
            self.mqtt_client.connect(BROKER_HOST, MQTT_PORT, 60)
            self.mqtt_client.subscribe(TOPICS)
            print(f"[GATEWAY] Inscrito nos tópicos: {[t[0] for t in TOPICS]}")
        except Exception as e:
            print(f"[ERRO] Falha ao conectar ao MQTT Broker: {e}")

    def setup_grpc(self):
        """Configura a comunicação com o Servidor Intermediário gRPC."""
        self.grpc_channel = grpc.insecure_channel(f"{ACTUATOR_IP}:{ACTUATOR_PORT}")
        self.grpc_stub = system_pb2_grpc.ActuatorStub(self.grpc_channel)

    def process_sensor_data(self, client, userdata, message):
        """Processa dados recebidos dos sensores via MQTT."""
        try:
            data = message.payload
            sensor_message = system_pb2.SensorData()
            sensor_message.ParseFromString(data)

            self.sensor_data[sensor_message.sensor_id] = {
                "tipo": sensor_message.device_type,
                "valor": sensor_message.value,
                "unidade": sensor_message.unit,
                "timestamp": sensor_message.timestamp
            }

            print(f"[GATEWAY] Sensor: {sensor_message.sensor_id} | {sensor_message.value} {sensor_message.unit}")

        except Exception as e:
            print(f"[ERRO] Falha ao processar mensagem Protobuf: {e}")

    def enviar_comando(self, dispositivo, acao, valor=0):
        """Envia um comando via gRPC para o Servidor Intermediário."""
        if dispositivo not in self.atuadores.values():
            print(f"[ERRO] Dispositivo desconhecido: {dispositivo}")
            return

        atuador_id = f"{dispositivo}_1"  # Mantemos um identificador fixo para cada tipo

        try:
            request = system_pb2.ActuatorCommand(
                device_type=dispositivo,
                actuator_id=atuador_id,
                action=acao,
                value=valor
            )

            response = self.grpc_stub.ExecuteCommand(request)
            print(f"[GATEWAY] Atuador ({atuador_id}): {response.status}")
            return {"dispositivo": atuador_id, "status": response.status}

        except Exception as e:
            print(f"[ERRO] Falha ao enviar comando gRPC: {e}")

    def listar_atuadores(self):
        """Retorna os tipos de atuadores disponíveis."""
        return self.atuadores

    def start_listening(self):
        """Inicia o consumo de mensagens MQTT."""
        print("[GATEWAY] Aguardando mensagens dos sensores...")
        self.mqtt_client.loop_start()

gateway = Gateway()

### Rotas da API

@app.route("/dispositivos", methods=["GET"])
def listar_dispositivos():
    return jsonify(gateway.listar_atuadores())

@app.route("/dispositivos/<string:nome>", methods=["GET"])
def consultar_estado(nome):
    if nome in gateway.sensor_data:
        return jsonify(gateway.sensor_data[nome])
    return jsonify({"erro": "Dispositivo não encontrado"}), 404

@app.route("/dispositivos/<string:nome>/ligar", methods=["POST"])
def ligar_dispositivo(nome):
    return gateway.enviar_comando(nome, "ligar")

@app.route("/dispositivos/<string:nome>/desligar", methods=["POST"])
def desligar_dispositivo(nome):
    return gateway.enviar_comando(nome, "desligar")

@app.route("/dispositivos/<string:nome>/configurar", methods=["POST"])
def configurar_dispositivo(nome):
    dados = request.get_json()
    print(dados)
    if not dados or "valor" not in dados:
        return jsonify({"erro": "Valor não especificado"}), 400
    return gateway.enviar_comando(nome, "configurar", dados["valor"])

if __name__ == "__main__":
    threading.Thread(target=gateway.start_listening, daemon=True).start()
    app.run(host="localhost", port=5001, debug=True)