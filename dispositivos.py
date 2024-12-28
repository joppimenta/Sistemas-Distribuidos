import socket
import system_pb2  # Arquivo gerado a partir de system.proto


class SmartDevice:
    def __init__(self, device_type, ip, port):
        self.device_type = device_type
        self.ip = ip
        self.port = port
        self.gateway_ip = 'localhost'
        self.gateway_port = 5000
        self.multicast_group = '224.0.0.1'
        self.multicast_port = 10001

    def send_device_info(self):
        # Cria e envia informações do dispositivo para o Gateway
        device_info = system_pb2.DeviceInfo(
            device_type=self.device_type,
            ip=self.ip,
            port=self.port,
            state="on"  # Exemplo de estado do dispositivo
        )

        # Envia via UDP multicast para o Gateway
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
            sock.sendto(device_info.SerializeToString(), (self.multicast_group, self.multicast_port))

    def listen_for_multicast(self):
        # Escuta por mensagens multicast do Gateway
        print("Listening for multicast messages...\n")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.multicast_port))  # Ouve em todas as interfaces

        # Adiciona o socket ao grupo multicast
        group = socket.inet_aton(self.multicast_group)
        mreq = group + socket.inet_aton('0.0.0.0')  # Escuta em todas as interfaces
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            print("Waiting for multicast messages...\n")
            data, addr = sock.recvfrom(1024)
            print(f"Recebido multicast do Gateway: {data}")
            if data == b"DISCOVER":
                print(f"Dispositivo {self.device_type} respondendo ao Gateway...")
                self.send_device_info()
            else:
                # Deserializa os dados recebidos
                device_info = system_pb2.DeviceInfo()
                try:
                    device_info.ParseFromString(data)
                    print(f"Dispositivo recebido - Tipo: {device_info.device_type}, IP: {device_info.ip}, Porta: {device_info.port}, Estado: {device_info.state}")
                except Exception as e:
                    print(f"Erro ao deserializar dados: {e}")


# Exemplo de dispositivos inteligentes
lamp = SmartDevice('lamp', 'localhost', 6000)
sensor = SmartDevice('sensor', 'localhost', 6001)

# Inicia a escuta de multicast (em threads separadas para permitir que ambos os dispositivos respondam)
import threading
lamp_thread = threading.Thread(target=lamp.listen_for_multicast)
sensor_thread = threading.Thread(target=sensor.listen_for_multicast)

lamp_thread.start()
sensor_thread.start()
