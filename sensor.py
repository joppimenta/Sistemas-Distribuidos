from base_device import SmartDevice

if __name__ == "__main__":
    sensor = SmartDevice('Sensor', 'localhost', 6001)
    try:
        sensor.start()
    except KeyboardInterrupt:
        sensor.stop()
