import socket
import system_pb2  # Arquivo gerado a partir de system.proto


class SmartDevice:
    device_ids = {"Torneira": "1", "Som": "2", "Lampada": "3", "Ar-Condicionado": "4"}

    def __init__(self, device_type, ip, port, initial_temperature=None):
        if device_type in SmartDevice.device_ids:
            self.device_id = SmartDevice.device_ids[device_type]
        else:
            raise ValueError(f"Dispositivo {device_type} não reconhecido!")

        self.device_type = device_type
        self.ip = ip
        self.port = port
        self.gateway_ip = '192.168.18.45'  # IP do Gateway
        self.gateway_port = 5000  # Porta do Gateway
        self.multicast_group = '224.0.0.1'
        self.multicast_port = 10001
        self.running = True
        self.temperature = initial_temperature if initial_temperature is not None else 20

    def send_device_info(self):
        """Envia as informações do dispositivo para o Gateway via multicast."""
        device_info = system_pb2.DeviceInfo(
            device_id=self.device_id,
            device_type=self.device_type,
            ip=self.ip,
            port=self.port,
            state="on",
            temperature=self.temperature
        )

        # Envia via UDP para o Gateway (multicast)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(device_info.SerializeToString(), (self.gateway_ip, 7000))
            print(f"Dispositivo {self.device_type} enviando dados para o Gateway.")

    def listen_for_multicast(self):
        """Escuta mensagens multicast do Gateway."""
        print(f"{self.device_type.capitalize()} está escutando mensagens multicast...\n")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.multicast_port))  # Escuta todas as interfaces

        # Adiciona o socket ao grupo multicast
        group = socket.inet_aton(self.multicast_group)
        mreq = group + socket.inet_aton('0.0.0.0')  # Escuta em todas as interfaces
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                print(f"Dispositivo {self.device_type} recebeu multicast do Gateway.")

                if data == b"DISCOVER_DEVICES":
                    print(f"Dispositivo {self.device_type} respondendo ao Gateway...")
                    self.send_device_info()

            except Exception as e:
                print(f"Erro no dispositivo {self.device_type}: {e}")

        sock.close()

    def stop(self):
        """Método para parar o dispositivo de escutar."""
        self.running = False
