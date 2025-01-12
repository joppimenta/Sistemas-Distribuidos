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
        self.device_timeout = 20  # Tempo em segundos para verificar se o dispositivo está ativo

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
            udp_socket.bind((self.ip, 7000))
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
                        self.devices[device_info.device_id] = {
                            "info": device_info,
                            "last_seen": time.time()  # Armazena o tempo da última resposta
                        }
                        print(f"Dispositivo identificado: ID={device_info.device_id}, Tipo={device_info.device_type}")

                except socket.timeout:
                    continue

    def check_device_timeout(self):
        """Verifica periodicamente se algum dispositivo está inativo e remove os inativos."""
        while True:
            time.sleep(10)  # Verifica a cada 10 segundos
            current_time = time.time()
            with self.lock:
                for device_id in list(self.devices.keys()):  # Usamos list() para evitar erro durante iteração
                    last_seen = self.devices[device_id]["last_seen"]
                    if current_time - last_seen > self.device_timeout:
                        print(f"Dispositivo {device_id} removido por inatividade.")
                        del self.devices[device_id]  # Remove o dispositivo inativo

    def handle_client(self, client_socket):
        """Lida com a conexão do cliente e responde com a lista de dispositivos ou comandos de controle."""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                if data == b"LIST_DEVICES":
                    # Envia lista de dispositivos conectados
                    with self.lock:
                        devices_list = "\n".join(
                            [f"ID: {dev['info'].device_id}, Tipo: {dev['info'].device_type}, Estado: {dev['info'].state}, "
                             f"Temperatura: {dev['info'].temperature if dev['info'].device_type == 'Ar-Condicionado' else 'N/A'}"
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
                            device = self.devices[device_id]['info']
                            if action == "ligar":
                                self.devices[device_id]['info'].state = "on"
                            elif action == "desligar":
                                self.devices[device_id]['info'].state = "off"

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

        except Exception as e:
            print(f"Erro no cliente: {e}")
        finally:
            client_socket.close()

    def start(self):
        """Inicia o Gateway."""
        # O Gateway deve enviar periodicamente mensagens multicast
        threading.Thread(target=self.listen_for_device_responses, daemon=True).start()

        # Envio periódico de mensagens multicast para descobrir novos dispositivos
        def send_discovery_periodically():
            while True:
                self.send_multicast_discovery()
                time.sleep(10)  # Envia a solicitação de descoberta a cada 10 segundos

        threading.Thread(target=send_discovery_periodically, daemon=True).start()

        # Verifica periodicamente os dispositivos inativos
        threading.Thread(target=self.check_device_timeout, daemon=True).start()

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
    gateway = Gateway(ip='172.31.40.12', port=5000, multicast_group="224.0.0.1", multicast_port=10001)
    gateway.start()
