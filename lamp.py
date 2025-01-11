from dispositivos import SmartDevice
import threading
lamp = SmartDevice('Lampada', '172.31.103.163', 6000)
lamp_thread = threading.Thread(target=lamp.listen_for_multicast)
lamp_thread.start()