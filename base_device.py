import socket
import system_pb2
import threading


class SmartDevice:
    device_counter = 0  # Variável de classe para IDs automáticos

    def __init__(self, device_type, ip, port, initial_temperature=None):
        self.device_id = str(SmartDevice.device_counter + 1)
        SmartDevice.device_counter += 1

        self.device_type = device_type
        self.ip = ip
        self.port = port
        self.gateway_ip = '192.168.18.45'
        self.gateway_port = 5000
        self.multicast_group = '224.0.0.1'
        self.multicast_port = 10001
        self.running = True
        self.temperature = initial_temperature if initial_temperature is not None else 20

    def send_device_info(self, addr):
        """Envia informações do dispositivo ao Gateway."""
        device_info = system_pb2.DeviceInfo(
            device_id=self.device_id,
            device_type=self.device_type,
            ip=self.ip,
            port=self.port,
            state="on",
            temperature=self.temperature
        )

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(device_info.SerializeToString(), (self.gateway_ip, self.multicast_port))

    def listen_for_multicast(self):
        """Escuta mensagens multicast."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.multicast_port))

        group = socket.inet_aton(self.multicast_group)
        mreq = group + socket.inet_aton('0.0.0.0')
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                if data == b"DISCOVER_DEVICES":
                    self.send_device_info(addr)
            except Exception as e:
                print(f"Erro no dispositivo {self.device_type}: {e}")
        sock.close()

    def start(self):
        """Inicia o dispositivo em uma nova thread."""
        self.thread = threading.Thread(target=self.listen_for_multicast)
        self.thread.start()
        print(f"{self.device_type} iniciado.")

    def stop(self):
        """Finaliza a execução do dispositivo."""
        self.running = False
        self.thread.join()
        print(f"{self.device_type} encerrado.")
