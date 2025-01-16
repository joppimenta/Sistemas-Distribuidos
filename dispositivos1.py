import socket
import system_pb2


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
        self.gateway_ip = '172.24.145.231'  # IP do Gateway
        self.gateway_port = 7000  # Porta do Gateway
        self.multicast_group = '224.0.0.1'
        self.multicast_port = 10001
        self.running = True
        self.temperature = initial_temperature if initial_temperature is not None else 20
        self.state = "off"

    def send_device_info(self):
        """Sends the device's current state to the gateway."""
        device_info = system_pb2.DeviceInfo(
            device_id=self.device_id,
            device_type=self.device_type,
            ip=self.ip,
            port=self.port,
            state=self.state,
            temperature=self.temperature,
        )

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(device_info.SerializeToString(), (self.gateway_ip, self.gateway_port))
            print(f"{self.device_type} sent updated state to Gateway.")

    def listen_and_respond(self):
        """Handles multicast messages for discovery and commands."""
        print(f"{self.device_type.capitalize()} is listening for messages...")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", self.multicast_port))  # Listen on all interfaces

        # Join the multicast group
        group = socket.inet_aton(self.multicast_group)
        mreq = group + socket.inet_aton("0.0.0.0")
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                print(f"{self.device_type} received a message from {addr}.")

                if data == b"DISCOVER_DEVICES":
                    print(f"{self.device_type} responding to discovery request.")
                    self.send_device_info()
                elif data.startswith(b"COMMAND_MESSAGE"):
                    command_message = system_pb2.DeviceControl()
                    command_message.ParseFromString(data[len("COMMAND_MESSAGE"):])

                    if command_message.device_id == self.device_id:
                        self.handle_command(command_message)

            except Exception as e:
                print(f"Error on {self.device_type}: {e}")

        sock.close()

    def handle_command(self, command_message):
        """Processes a command message."""
        print(f"{self.device_type} received a command: {command_message.action}")

        if command_message.action == "ligar":
            self.state = "on"
            print(f"Estado do aparelho alterado para 'ligado'.")
        elif command_message.action == "desligar":
            self.state = "off"
            print(f"Estado do aparelho alterado para 'desligado'.")

        if self.device_type == "Ar-Condicionado" and self.state == "on":
            if 16 <= command_message.temperature <= 30:
                self.temperature = command_message.temperature
                print(f"Temperature set to {self.temperature}°C.")
            else:
                print("Invalid temperature range. Ignored.")

        self.send_device_info()  # Send updated state back to the gateway

    def stop(self):
        """Stops the device."""
        self.running = False

