from dispositivos1 import SmartDevice
import threading

som = SmartDevice('Som', '192.168.212.93', 7000)
som_thread = threading.Thread(target=som.listen_and_respond)
som_thread.start()
