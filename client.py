import socket
import system_pb2  # Arquivo gerado a partir de system.proto


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
            self.socket.sendall(b"LIST_DEVICES")
            data = self.socket.recv(1024)
            print("Dispositivos conectados:")
            print(data.decode())
        except Exception as e:
            print(f"Erro ao listar dispositivos: {e}")

    def control_device(self):
        try:
            # Solicita a lista de dispositivos para exibição
            self.list_devices()

            device_type = input("Qual dispositivo deseja controlar? (Lampada/Sensor/Ar-Condicionado): ").lower()

            if device_type not in ["lampada", "sensor", "ar-condicionado"]:
                print("Tipo de dispositivo inválido.")
                return

            # Determina o ID do dispositivo com base no tipo
            device_id = {"lampada": "1", "sensor": "2", "ar-condicionado": "3"}.get(device_type)

            action = input("Deseja ligar ou desligar o dispositivo? (ligar/desligar): ").lower()
            if action not in ["ligar", "desligar"]:
                print("Ação inválida.")
                return

            # Controle adicional para ar-condicionado
            temperature = None
            if device_type == "ar-condicionado":
                if action == "ligar":
                    temp_control = input("Deseja ajustar a temperatura? (sim/não): ").lower()
                    if temp_control == "sim":
                        try:
                            temperature = float(input("Informe a temperatura desejada (em °C): "))
                            if temperature < 16 or temperature > 30:
                                print("Temperatura fora do intervalo permitido (16°C - 30°C).")
                                return
                        except ValueError:
                            print("Temperatura inválida.")
                            return
                elif action == "desligar":
                    print("Desligando o ar-condicionado. Não será possível ajustar a temperatura.")
                else:
                    temp_control = input("Deseja controlar a temperatura do ar-condicionado? (sim/não): ").lower()
                    if temp_control == "sim":
                        print("O ar-condicionado está desligado. Ligue o aparelho antes de ajustar a temperatura.")
                        return

            # Criação da mensagem Protobuf
            control_message = system_pb2.DeviceControl(
                device_id=device_id,
                action=action,
                temperature=temperature if temperature is not None else 0.0
            )

            # Serialização e envio da mensagem
            message = control_message.SerializeToString()
            self.socket.sendall(message)
            print(f"Comando enviado: {action} para o dispositivo {device_type}.")
            if temperature is not None:
                print(f"Temperatura ajustada para: {temperature}°C.")

            # Recebendo a resposta do Gateway
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
    client = Client("192.168.18.45", 5000)
    client.run()
