import socket
import tkinter as tk
from tkinter import ttk, messagebox
import system_pb2


class ClientApp:
    def __init__(self, master, gateway_ip, gateway_port):
        self.master = master
        self.gateway_ip = gateway_ip
        self.gateway_port = gateway_port
        self.socket = None
        self.devices = {}

        self.master.title("Controle de Dispositivos")
        self.master.geometry("600x400")

        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Lista de dispositivos
        self.device_list_label = tk.Label(self.main_frame, text="Dispositivos Conectados:")
        self.device_list_label.pack(anchor=tk.W)
        self.device_listbox = tk.Listbox(self.main_frame, height=10)
        self.device_listbox.pack(fill=tk.BOTH, expand=True)

        # Botão para listar dispositivos
        self.list_devices_button = tk.Button(self.main_frame, text="Listar Dispositivos", command=self.list_devices)
        self.list_devices_button.pack(pady=5)

        # Seleção de dispositivo e ações
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=10)

        self.device_type_label = tk.Label(self.control_frame, text="Tipo de Dispositivo:")
        self.device_type_label.grid(row=0, column=0, padx=5)
        self.device_type_combobox = ttk.Combobox(
            self.control_frame, values=["Lâmpada", "Sensor", "Ar-Condicionado"], state="readonly"
        )
        self.device_type_combobox.grid(row=0, column=1, padx=5)
        self.device_type_combobox.bind("<<ComboboxSelected>>", self.update_temperature_field)

        self.action_label = tk.Label(self.control_frame, text="Ação:")
        self.action_label.grid(row=1, column=0, padx=5)
        self.action_combobox = ttk.Combobox(self.control_frame, values=["Ligar", "Desligar"], state="readonly")
        self.action_combobox.grid(row=1, column=1, padx=5)

        # Campo de temperatura
        self.temperature_label = tk.Label(self.control_frame, text="Temperatura (16°C - 30°C):")
        self.temperature_entry = tk.Entry(self.control_frame)

        # Botão para enviar comando
        self.control_button = tk.Button(self.main_frame, text="Enviar Comando", command=self.control_device)
        self.control_button.pack(pady=5)

        # Conecta ao Gateway
        self.connect_to_gateway()

        # Atualiza a lista de dispositivos automaticamente a cada minuto
        self.schedule_device_list_update()

    def connect_to_gateway(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.gateway_ip, self.gateway_port))
            messagebox.showinfo("Conexão", "Conectado ao Gateway com sucesso!")
            self.list_devices()  # Listar dispositivos ao conectar
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao Gateway: {e}")
            self.master.destroy()

    def list_devices(self):
        try:
            self.socket.sendall(b"LIST_DEVICES")
            data = self.socket.recv(4096)  # Ajustar tamanho do buffer conforme necessário
            devices = data.decode().split("\n")

            self.device_listbox.delete(0, tk.END)  # Limpa a lista
            connected_devices = []
            self.devices.clear()  # Limpa o dicionário de dispositivos

            for device in devices:
                if device:
                    self.device_listbox.insert(tk.END, device)
                    partes = device.split(", ")
                    tipo = partes[1].split(": ")[1]
                    device_id = partes[0].split(": ")[1]
                    self.devices[tipo.lower()] = device_id  # Adiciona o dispositivo e seu ID no dicionário
                    connected_devices.append(tipo)

            # Atualiza o dropdown de tipo de dispositivo com os nomes dos dispositivos conectados
            self.device_type_combobox["values"] = connected_devices
            if connected_devices:
                self.device_type_combobox.current(0)  # Seleciona o primeiro dispositivo por padrão
            else:
                self.device_type_combobox.set("")  # Reseta o valor caso não haja dispositivos conectados
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar dispositivos: {e}")

    def schedule_device_list_update(self):
        self.list_devices()  # Atualiza a lista de dispositivos
        self.master.after(60000, self.schedule_device_list_update)  # Agenda nova atualização em 60 segundos

    def control_device(self):
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

            # Recebe a resposta do Gateway
            response = self.socket.recv(1024)
            messagebox.showinfo("Resposta do Gateway", response.decode())

            # Atualiza a lista de dispositivos
            self.list_devices()

        except ValueError:
            messagebox.showerror("Erro", "Temperatura inválida. Insira um número entre 16°C e 30°C.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar comando: {e}")

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
    app = ClientApp(root, "192.168.18.45", 5000)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
