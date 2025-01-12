from dispositivos import SmartDevice
import threading

som = SmartDevice('Som', '192.168.18.45', 6003)
som_thread = threading.Thread(target=som.listen_for_multicast)
som_thread.start()