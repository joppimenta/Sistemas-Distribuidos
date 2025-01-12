from dispositivos import SmartDevice
import threading
lamp = SmartDevice('Lampada', '192.168.18.45', 6000)
lamp_thread = threading.Thread(target=lamp.listen_for_multicast)
lamp_thread.start()