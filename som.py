from dispositivos1 import SmartDevice
import threading

som = SmartDevice('Som', '172.24.145.231', 6003)
som_thread = threading.Thread(target=som.listen_and_respond)
som_thread.start()