from dispositivos1 import SmartDevice
import threading
lamp = SmartDevice('Lampada', '172.24.145.231', 7000)
lamp_thread = threading.Thread(target=lamp.listen_and_respond)
lamp_thread.start()
