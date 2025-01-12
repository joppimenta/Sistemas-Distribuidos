from dispositivos import SmartDevice
import threading

air_conditioner = SmartDevice('Ar-Condicionado', '192.168.18.45', 6002, 25)
air_conditioner_thread = threading.Thread(target=air_conditioner.listen_for_multicast)
air_conditioner_thread.start()