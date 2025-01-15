from dispositivos1 import SmartDevice
import threading

som = SmartDevice('Som', '172.31.40.12', 6003)
som_thread = threading.Thread(target=som.listen_and_respond)
som_thread.start()