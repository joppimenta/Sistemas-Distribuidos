import socket
import system_pb2  # Arquivo gerado a partir de system.proto
from concurrent.futures import ThreadPoolExecutor


class Gateway:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.devices = {}  # Um dicionário de dispositivos simulados (por exemplo, lampadas, sensores)

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break  # Se não houver mais dados, encerra a conexão
                if data == b"LIST_DEVICES":
                    # Envia a lista de dispositivos conectados
                    devices_list = "\n".join(
                        [f"ID: {dev_id}, Tipo: {dev.device_type}, Estado: {dev.state}" for dev_id, dev in
                         self.devices.items()])
                    client_socket.sendall(devices_list.encode())
                else:
                    # Recebe comandos de controle de dispositivos
                    device_control = system_pb2.DeviceControl()
                    device_control.ParseFromString(data)
                    device_id = device_control.device_id
                    action = device_control.action

                    if device_id in self.devices:
                        device = self.devices[device_id]
                        if action == "ligar":
                            device.state = "on"
                        elif action == "desligar":
                            device.state = "off"
                        client_socket.sendall(f"Dispositivo {device_id} {action} com sucesso.".encode())
                    else:
                        client_socket.sendall(f"Dispositivo {device_id} não encontrado.".encode())
        except Exception as e:
            print(f"Erro no processamento do cliente: {e}")
        finally:
            client_socket.close()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(5)
        print(f"Gateway iniciado em {self.ip}:{self.port}")

        # Exemplo de dispositivos simulados
        self.devices['1'] = system_pb2.DeviceInfo(device_id="1", device_type="lamp", ip="localhost", port=6000, state="off")
        self.devices['2'] = system_pb2.DeviceInfo(device_id="2", device_type="sensor", ip="localhost", port=6001, state="on")

        with ThreadPoolExecutor() as executor:
            while True:
                client_socket, addr = server_socket.accept()
                print(f"Cliente conectado de {addr}")
                executor.submit(self.handle_client, client_socket)


if __name__ == "__main__":
    gateway = Gateway("localhost", 5000)
    gateway.start()
