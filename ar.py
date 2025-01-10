from base_device import SmartDevice

if __name__ == "__main__":
    air_conditioner = SmartDevice('Ar-Condicionado', 'localhost', 6002, initial_temperature=25)
    try:
        air_conditioner.start()
    except KeyboardInterrupt:
        air_conditioner.stop()
