import socket
import system_pb2  # Arquivo gerado a partir de system.proto
import time


class Client:
    def __init__(self, gateway_ip, gateway_port):
        self.gateway_ip = gateway_ip
        self.gateway_port = gateway_port

    def connect_to_gateway(self):
        # Conecta-se ao Gateway via TCP
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.gateway_ip, self.gateway_port))
            print("Conectado ao Gateway.")
        except Exception as e:
            print(f"Erro ao conectar ao Gateway: {e}")
            exit(1)

    def list_devices(self):
        # Solicita ao Gateway a lista de dispositivos conectados
        try:
            # Envia o comando para listar dispositivos
            self.socket.sendall(b"LIST_DEVICES")
            # Recebe a resposta com a lista de dispositivos
            data = self.socket.recv(1024)
            print("Dispositivos conectados:")
            print(data.decode())
        except Exception as e:
            print(f"Erro ao listar dispositivos: {e}")

    def control_device(self):
        # Envia um comando para controlar um dispositivo
        device_id = input("Informe o ID do dispositivo que deseja controlar: ")
        action = input("Informe a ação (ligar/desligar): ").lower()

        if action not in ['ligar', 'desligar']:
            print("Ação inválida.")
            return

        try:
            # Cria a mensagem Protobuf para enviar ao Gateway
            control_message = system_pb2.DeviceControl(
                device_id=device_id,
                action=action
            )
            # Serializa a mensagem
            message = control_message.SerializeToString()
            # Envia o comando de controle
            self.socket.sendall(message)
            print(f"Comando '{action}' enviado para o dispositivo {device_id}.")

            # Aguarda a resposta do Gateway
            response = self.socket.recv(1024)
            print(f"Resposta do Gateway: {response.decode()}")
        except Exception as e:
            print(f"Erro ao enviar comando: {e}")

    def close_connection(self):
        # Fecha a conexão com o Gateway
        try:
            self.socket.close()
            print("Conexão fechada.")
        except Exception as e:
            print(f"Erro ao fechar conexão: {e}")

    def run(self):
        # Exibe o menu para o usuário interagir
        self.connect_to_gateway()

        while True:
            print("\n--- Menu ---")
            print("1. Listar dispositivos")
            print("2. Controlar dispositivo")
            print("3. Sair")
            option = input("Escolha uma opção: ")

            if option == '1':
                self.list_devices()
            elif option == '2':
                self.control_device()
            elif option == '3':
                self.close_connection()
                break
            else:
                print("Opção inválida!")


if __name__ == "__main__":
    client = Client("localhost", 5000)
    client.run()
