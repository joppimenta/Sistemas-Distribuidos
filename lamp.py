from dispositivos import SmartDevice
import threading
lamp = SmartDevice('Lampada', '192.168.3.120', 7000)
lamp_thread = threading.Thread(target=lamp.listen_for_multicast)
lamp_thread.start()
