from dispositivos import SmartDevice
import threading

air_conditioner = SmartDevice('Ar-Condicionado', '172.24.145.231', 6002, 25)
print(air_conditioner.device_id)
air_conditioner_thread = threading.Thread(target=air_conditioner.listen_for_multicast)
air_conditioner_thread.start()