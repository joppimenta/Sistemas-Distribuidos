import socket
import struct
import system_pb2  # Arquivo gerado a partir de system.proto
from concurrent.futures import ThreadPoolExecutor
import threading
import time


class Gateway:
    def __init__(self, ip, port, multicast_group, multicast_port):
        self.ip = ip
        self.port = port
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.devices = {}  # Armazena os dispositivos identificados
        self.lock = threading.Lock()  # Para acesso seguro à lista de dispositivos

    def send_multicast_discovery(self):
        """Envia mensagem multicast para descobrir dispositivos inteligentes."""
        multicast_message = "DISCOVER_DEVICES".encode()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as multicast_socket:
            multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            multicast_socket.sendto(multicast_message, (self.multicast_group, self.multicast_port))  # Usando o multicast_group e a porta configurados
        print("Mensagem multicast de descoberta enviada.")

    def listen_for_device_responses(self):
        """Escuta respostas dos dispositivos após envio do multicast."""
        start_time = time.time()  # Marca o tempo de início
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind((self.ip, self.multicast_port))
            print(f"Aguardando respostas dos dispositivos em {self.ip}...")

            # Adiciona o socket ao grupo multicast
            group = socket.inet_aton(self.multicast_group)
            mreq = group + socket.inet_aton('0.0.0.0')  # Escuta em todas as interfaces
            udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            udp_socket.settimeout(5)

            while True:
                # Verifica se o tempo de escuta atingiu o limite
                if time.time() - start_time > 5:
                    print(f"Tempo de escuta de 5s expirado. Finalizando...")
                    break

                try:
                    # Aguarda por novos pacotes
                    data, addr = udp_socket.recvfrom(1024)
                    device_info = system_pb2.DeviceInfo()
                    device_info.ParseFromString(data)

                    # Registra o dispositivo no dicionário, evitando duplicação
                    with self.lock:
                        if device_info.device_id not in self.devices:
                            self.devices[device_info.device_id] = device_info
                            print(
                                f"Dispositivo identificado: ID={device_info.device_id}, Tipo={device_info.device_type}, IP={addr}")
                except socket.timeout:
                    # Apenas ignora o timeout e continua esperando
                    continue

            # Finaliza a escuta
            udp_socket.close()
            print("Escuta finalizada.")

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                if data == b"LIST_DEVICES":
                    # Envia a lista de dispositivos conectados
                    with self.lock:
                        devices_list = "\n".join(
                            [f"ID: {dev.device_id}, Tipo: {dev.device_type}, Estado: {dev.state}, "
                             f"Temperatura: {dev.temperature if dev.device_type == 'Ar-Condicionado' else 'N/A'}"
                             for dev in self.devices.values()]
                        )
                    client_socket.sendall(devices_list.encode())

                else:
                    # Recebe comandos de controle de dispositivos
                    device_control = system_pb2.DeviceControl()
                    device_control.ParseFromString(data)
                    device_id = device_control.device_id
                    action = device_control.action
                    temperature = device_control.temperature

                    with self.lock:
                        if device_id in self.devices:
                            device = self.devices[device_id]
                            if action == "ligar":
                                device.state = "on"
                            elif action == "desligar":
                                device.state = "off"

                            # Controle de temperatura para dispositivos de ar-condicionado
                            if device.device_type == "Ar-Condicionado" and action == "ligar":
                                if 16 <= temperature <= 30:
                                    device.temperature = temperature
                                    client_socket.sendall(
                                        f"Ar-condicionado {device_id} ligado com temperatura {temperature}°C.".encode())
                                else:
                                    client_socket.sendall(
                                        f"Temperatura {temperature}°C inválida. Intervalo permitido: 16°C a 30°C.".encode())
                            else:
                                client_socket.sendall(f"Dispositivo {device_id} {action} com sucesso.".encode())
                        else:
                            client_socket.sendall(f"Dispositivo {device_id} não encontrado.".encode())
        except Exception as e:
            print(f"Erro no processamento do cliente: {e}")
        finally:
            client_socket.close()

    def start(self):
        # Etapa de descoberta de dispositivos

        self.send_multicast_discovery()
        self.listen_for_device_responses()

        # Inicia o servidor TCP para interagir com o cliente
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(5)
        print(f"Gateway iniciado em {self.ip}:{self.port}")

        with ThreadPoolExecutor() as executor:
            while True:
                client_socket, addr = server_socket.accept()
                print(f"Cliente conectado de {addr}")
                executor.submit(self.handle_client, client_socket)


if __name__ == "__main__":
    gateway = Gateway(ip='172.31.103.163', port=5000, multicast_group="224.0.0.1", multicast_port=10001)
    gateway.start()
