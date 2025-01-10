from base_device import SmartDevice

if __name__ == "__main__":
    lamp = SmartDevice('Lampada', 'localhost', 6000)
    try:
        lamp.start()
    except KeyboardInterrupt:
        lamp.stop()
