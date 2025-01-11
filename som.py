from dispositivos import SmartDevice
import threading

som = SmartDevice('Som', '172.31.103.163', 6003)
som_thread = threading.Thread(target=som.listen_for_multicast)
som_thread.start()