from dispositivos1 import SmartDevice
import threading

air_conditioner = SmartDevice('Ar-Condicionado', '172.31.40.12', 6002, 25)
air_conditioner_thread = threading.Thread(target=air_conditioner.listen_and_respond)
air_conditioner_thread.start()