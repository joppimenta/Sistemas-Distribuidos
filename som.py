from base_device import SmartDevice # type: ignore

if __name__ == "__main__":
    som = SmartDevice('Som', 'localhost', 6003)
    try:
        som.start()
    except KeyboardInterrupt:
        print("Som encerrado.")
        som.stop()
