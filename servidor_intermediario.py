import grpc
import system_pb2
import system_pb2_grpc
import socket
from concurrent import futures

# Configuração do Atuador (Arduino)
ACTUATOR_IP = "192.168.240.82"
ACTUATOR_PORT = 50051

class AtuadorService(system_pb2_grpc.ActuatorServicer):
    def ExecuteCommand(self, request, context):
        """Recebe comandos gRPC e os encaminha para o Arduino via TCP."""
        try:
            print(f"[INTERMEDIÁRIO] Enviando comando: {request.action} para {request.actuator_id}")

            # Conectar ao Arduino via TCP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # Tempo limite para evitar travamento
                s.connect((ACTUATOR_IP, ACTUATOR_PORT))

                comando = f"{request.action}\n"
                s.sendall(comando.encode())

                # Receber resposta do Arduino
                resposta = s.recv(1024).decode()
                print(f"[INTERMEDIÁRIO] Resposta do Arduino: {resposta}")

                return system_pb2.ActuatorResponse(
                    actuator_id=request.actuator_id,
                    status=resposta.strip()
                )

        except Exception as e:
            print(f"[ERRO] Falha ao conectar ao Arduino: {e}")
            return system_pb2.ActuatorResponse(
                actuator_id=request.actuator_id,
                status="Erro"
            )

def serve():
    """Inicia o Servidor gRPC Intermediário"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    system_pb2_grpc.add_ActuatorServicer_to_server(AtuadorService(), server)
    server.add_insecure_port("[::]:50052")  # Porta do Servidor Intermediário
    server.start()
    print("[INTERMEDIÁRIO] Servidor gRPC rodando na porta 50052...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
