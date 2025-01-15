from dispositivos1 import SmartDevice
import threading
lamp = SmartDevice('Lampada', '192.168.0.16', 7000)
lamp_thread = threading.Thread(target=lamp.listen_and_respond)
lamp_thread.start()
