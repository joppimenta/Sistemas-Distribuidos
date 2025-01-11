import socket
import system_pb2  # Arquivo gerado a partir de system.proto


class SmartDevice:
    # Variável de classe para controlar o ID do dispositivo
    device_counter = 0

    def __init__(self, device_type, ip, port, initial_temperature=None):
        # Gera o ID automaticamente
        self.device_id = str(SmartDevice.device_counter + 1)
        SmartDevice.device_counter += 1  # Incrementa o contador para o próximo dispositivo

        self.device_type = device_type
        self.ip = ip
        self.port = port
        self.gateway_ip = '172.31.103.163'  # Pode ser alterado para o IP real do Gateway
        self.gateway_port = 5000
        self.multicast_group = '224.0.0.1'
        self.multicast_port = 10001
        self.running = True
        self.temperature = initial_temperature if initial_temperature is not None else 20

    def send_device_info(self, addr):
        """Envia as informações do dispositivo para o Gateway."""
        device_info = system_pb2.DeviceInfo(
            device_id=self.device_id,
            device_type=self.device_type,
            ip=self.ip,
            port=self.port,
            state="on",
            temperature=self.temperature
        )

        print(f"Enviando dados para : {addr}")

        # Envia via UDP para o Gateway
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(device_info.SerializeToString(), (self.gateway_ip, self.multicast_port))  # Envia para o gateway

    def listen_for_multicast(self):
        """Escuta mensagens multicast do Gateway."""
        print(f"{self.device_type.capitalize()} está escutando mensagens multicast...\n")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.multicast_port))  # Ouve em todas as interfaces

        # Adiciona o socket ao grupo multicast
        group = socket.inet_aton(self.multicast_group)
        mreq = group + socket.inet_aton('0.0.0.0')  # Escuta em todas as interfaces
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while self.running:
            print(f"{self.device_type.capitalize()} aguardando mensagens multicast...\n")
            try:
                data, addr = sock.recvfrom(1024)
                print(f"Recebido multicast do Gateway de {addr}: {data}\n")
                print(addr)
                if data == b"DISCOVER_DEVICES":
                    print(f"Dispositivo {self.device_type} respondendo ao Gateway...")

                    self.send_device_info(addr)
            except Exception as e:
                print(f"Erro no dispositivo {self.device_type}: {e}")
        sock.close()

    def stop(self):
        """Método para parar o dispositivo de escutar."""
        self.running = False



