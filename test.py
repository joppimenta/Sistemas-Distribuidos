import socket
import system_pb2

# Create a UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Prepare a DeviceInfo message
device_info = system_pb2.DeviceInfo()
device_info.device_id = "device123"
device_info.device_type = "Sensor"
device_info.ip = "192.168.0.10"
device_info.port = 8080
device_info.state = "on"
device_info.temperature = 25.0

# Serialize and send the message
udp_socket.sendto(device_info.SerializeToString(), ("192.168.80.93", 7000))
udp_socket.close()

