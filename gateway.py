import socket
import system_pb2
import threading
import time

class Gateway:
    def __init__(self, ip, port, multicast_group, multicast_port):
        self.ip = ip
        self.port = port
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.devices = {}  # Dicionário para armazenar dispositivos
        self.lock = threading.Lock()  # Para garantir acesso seguro à lista de dispositivos

    def send_multicast_discovery(self):
        """Envia uma mensagem multicast para descobrir novos dispositivos."""
        multicast_message = "DISCOVER_DEVICES".encode()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as multicast_socket:
            multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            multicast_socket.sendto(multicast_message, (self.multicast_group, self.multicast_port))
        print("Mensagem multicast de descoberta enviada.")

    def listen_for_device_responses(self):
        """Escuta as respostas dos dispositivos após o multicast de descoberta."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind((self.ip, self.multicast_port))
            print(f"Aguardando respostas dos dispositivos em {self.ip}...")

            # Adiciona o socket ao grupo multicast
            group = socket.inet_aton(self.multicast_group)
            mreq = group + socket.inet_aton('0.0.0.0')  # Escuta em todas as interfaces
            udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            while True:
                try:
                    data, addr = udp_socket.recvfrom(1024)
                    device_info = system_pb2.DeviceInfo()
                    device_info.ParseFromString(data)

                    with self.lock:
                        if device_info.device_id not in self.devices:
                            self.devices[device_info.device_id] = device_info
                            print(f"Dispositivo identificado: ID={device_info.device_id}, Tipo={device_info.device_type}")
                        else:
                            print(f"Dispositivo {device_info.device_id} já registrado.")

                except socket.timeout:
                    continue

    def handle_client(self, client_socket):
        """Handle the client connection and respond with device list or control commands."""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                if data == b"LIST_DEVICES":
                    # Envia lista de dispositivos conectados
                    with self.lock:
                        devices_list = "\n".join(
                            [f"ID: {dev.device_id}, Tipo: {dev.device_type}, Estado: {dev.state}"
                             for dev in self.devices.values()]
                        )
                    client_socket.sendall(devices_list.encode())

                else:
                    # Comando de controle de dispositivo
                    device_control = system_pb2.DeviceControl()
                    device_control.ParseFromString(data)
                    device_id = device_control.device_id
                    action = device_control.action

                    with self.lock:
                        if device_id in self.devices:
                            device = self.devices[device_id]
                            if action == "ligar":
                                device.state = "on"
                            elif action == "desligar":
                                device.state = "off"

                            client_socket.sendall(f"Comando {action} para {device_id} executado com sucesso.".encode())
                        else:
                            client_socket.sendall(f"Dispositivo {device_id} não encontrado.".encode())

        except Exception as e:
            print(f"Erro no cliente: {e}")
        finally:
            client_socket.close()

    def start(self):
        """Inicia o Gateway."""
        # O Gateway deve enviar periodicamente mensagens multicast
        threading.Thread(target=self.listen_for_device_responses, daemon=True).start()

        while True:
            self.send_multicast_discovery()
            time.sleep(10)  # Envia uma nova solicitação de descoberta a cada 10 segundos

        # Inicia o servidor TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(5)
        print(f"Gateway iniciado em {self.ip}:{self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Cliente conectado de {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    gateway = Gateway(ip='172.24.145.231', port=5000, multicast_group="224.0.0.1", multicast_port=10001)
    gateway.start()
