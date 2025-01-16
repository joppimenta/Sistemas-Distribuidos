import socket
import tkinter as tk
from tkinter import ttk, messagebox
import system_pb2
import threading
import time


class ClientApp:
    def __init__(self, master, gateway_ip, gateway_port):
        self.master = master
        self.gateway_ip = gateway_ip
        self.gateway_port = gateway_port
        self.socket = None
        self.devices = {}
        self.connected = False
        self.reconnect_thread = None

        self.master.title("Controle de Dispositivos")
        self.master.geometry("600x400")

        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.status_label = tk.Label(self.main_frame, text="Status: Tentando conectar ao Gateway...", fg="red")
        self.status_label.pack(anchor=tk.W, pady=5)

        self.device_list_label = tk.Label(self.main_frame, text="Dispositivos Conectados:")
        self.device_list_label.pack(anchor=tk.W)
        self.device_listbox = tk.Listbox(self.main_frame, height=10)
        self.device_listbox.pack(fill=tk.BOTH, expand=True)

        self.list_devices_button = tk.Button(self.main_frame, text="Listar Dispositivos", command=self.list_devices,
                                             state=tk.DISABLED)
        self.list_devices_button.pack(pady=5)

        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=10)

        self.device_type_label = tk.Label(self.control_frame, text="Tipo de Dispositivo:")
        self.device_type_label.grid(row=0, column=0, padx=5)
        self.device_type_combobox = ttk.Combobox(
            self.control_frame, values=["Lâmpada", "Torneira", "Ar-Condicionado", "Som"], state="readonly"
        )
        self.device_type_combobox.grid(row=0, column=1, padx=5)
        self.device_type_combobox.bind("<<ComboboxSelected>>", self.update_temperature_field)

        self.action_label = tk.Label(self.control_frame, text="Ação:")
        self.action_label.grid(row=1, column=0, padx=5)
        self.action_combobox = ttk.Combobox(self.control_frame, values=["Ligar", "Desligar"], state="readonly")
        self.action_combobox.grid(row=1, column=1, padx=5)

        self.temperature_label = tk.Label(self.control_frame, text="Temperatura (16°C - 30°C):")
        self.temperature_entry = tk.Entry(self.control_frame)

        self.control_button = tk.Button(self.main_frame, text="Enviar Comando", command=self.control_device,
                                        state=tk.DISABLED)
        self.control_button.pack(pady=5)

        self.start_reconnection_loop()

    def connect_to_gateway(self):
        try:
            if self.socket:
                self.socket.close()  # Fecha o socket antigo, se existir
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)  # Set a timeout for socket operations
            self.socket.connect((self.gateway_ip, self.gateway_port))
            self.connected = True
            self.status_label.config(text="Status: Conectado ao Gateway", fg="green")
            self.list_devices_button.config(state=tk.NORMAL)
            self.control_button.config(state=tk.NORMAL)
            self.list_devices()  # Listar dispositivos ao conectar
        except (socket.timeout, socket.error) as e:
            self.connected = False
            messagebox.showerror("Erro", f"Não foi possível conectar ao Gateway: {e}")

    def list_devices(self):
        if not self.connected:
            messagebox.showwarning("Aviso", "Conexão com o Gateway perdida. Tentando reconectar...")
            return
        try:
            self.socket.sendall(b"LIST_DEVICES")
            data = self.socket.recv(4096)
            if not data:  # Se não receber dados, considerar como desconectado
                raise ConnectionError("Conexão perdida com o Gateway.")

            devices = data.decode().split("\n")

            self.device_listbox.delete(0, tk.END)
            connected_devices = []
            self.devices.clear()

            for device in devices:
                if device:
                    self.device_listbox.insert(tk.END, device)
                    partes = device.split(", ")
                    tipo = partes[1].split(": ")[1]
                    device_id = partes[0].split(": ")[1]
                    self.devices[tipo.lower()] = device_id
                    connected_devices.append(tipo)

            self.device_type_combobox["values"] = connected_devices
            if connected_devices:
                self.device_type_combobox.current(0)
            else:
                self.device_type_combobox.set("")
        except (ConnectionError, socket.timeout) as e:
            self.connected = False
            messagebox.showerror("Erro", f"Erro ao listar dispositivos: {e}")

    def start_reconnection_loop(self):
        def reconnect():
            while True:
                if not self.connected:
                    self.status_label.config(text="Status: Tentando conectar ao Gateway...", fg="red")
                    self.connect_to_gateway()
                time.sleep(5)  # Tenta reconectar a cada 5 segundos

        self.reconnect_thread = threading.Thread(target=reconnect, daemon=True)
        self.reconnect_thread.start()

    def control_device(self):
        if not self.connected:
            messagebox.showwarning("Aviso", "Conexão com o Gateway perdida. Tentando reconectar...")
            return

        if not self.devices:
            messagebox.showwarning("Aviso", "Nenhum dispositivo conectado. Não é possível enviar comandos.")
            return

        device_type = self.device_type_combobox.get().lower()
        action = self.action_combobox.get().lower()
        temperature = self.temperature_entry.get() if self.temperature_entry.get() else None

        if not device_type or not action:
            messagebox.showwarning("Aviso", "Selecione um tipo de dispositivo e uma ação.")
            return

        try:
            device_id = self.devices.get(device_type)

            if not device_id:
                raise ValueError("Dispositivo não encontrado.")

            control_message = system_pb2.DeviceControl(
                device_id=device_id,
                action=action,
                temperature=float(temperature) if temperature else 0.0
            )
            self.socket.sendall(control_message.SerializeToString())
            print("Command sent to Gateway, waiting for response...")

            response = self.socket.recv(1024)
            if not response:
                raise ConnectionError("Conexão perdida com o Gateway.")

            print("Response received from Gateway.")
            messagebox.showinfo("Resposta do Gateway", response.decode())
            self.list_devices()
        except (socket.timeout, ConnectionError) as e:
            self.connected = False
            messagebox.showerror("Erro", f"Erro de conexão: {e}")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def update_temperature_field(self, event):
        selected_device = self.device_type_combobox.get()
        if selected_device == "Ar-Condicionado":
            self.temperature_label.grid(row=2, column=0, padx=5)
            self.temperature_entry.grid(row=2, column=1, padx=5)
        else:
            self.temperature_label.grid_remove()
            self.temperature_entry.grid_remove()

    def on_closing(self):
        if self.socket:
            self.socket.close()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root, '172.24.145.231', 5000)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

