from dispositivos import SmartDevice
import threading

sensor = SmartDevice('Torneira', '172.24.145.231', 6001)
sensor_thread = threading.Thread(target=sensor.listen_for_multicast)
sensor_thread.start()
