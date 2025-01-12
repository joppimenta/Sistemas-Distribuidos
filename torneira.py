from dispositivos import SmartDevice
import threading

sensor = SmartDevice('Torneira', '192.168.18.45', 6001)
sensor_thread = threading.Thread(target=sensor.listen_for_multicast)
sensor_thread.start()
