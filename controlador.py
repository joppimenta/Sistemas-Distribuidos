from gateway import Gateway

class Controlador:
    def __init__(self):
        self.gateway = Gateway()

    def listar_atuadores(self):
        """Lista os tipos de atuadores disponíveis no Gateway."""
        atuadores = self.gateway.listar_atuadores()
        print("\n=== Selecione o Tipo de Dispositivo ===")
        for key, dispositivo in atuadores.items():
            print(f"{key} - {dispositivo}")

        escolha = input("Escolha um número: ").strip()
        return atuadores.get(escolha, None)

    def enviar_comando(self, acao, valor=0):
        """Solicita ao usuário um tipo de dispositivo e envia um comando."""
        dispositivo = self.listar_atuadores()
        if not dispositivo:
            print("[ERRO] Escolha inválida!")
            return

        print(f"[CONTROLADOR] Enviando comando: {acao.upper()} para {dispositivo}")
        self.gateway.enviar_comando(dispositivo, acao, valor)
        print("[CONTROLADOR] Comando enviado com sucesso!")

    def menu(self):
        """Interface de entrada de comandos."""
        while True:
            print("\n===== CONTROLADOR DE ATUADORES =====")
            print("1 - Ligar Atuador")
            print("2 - Desligar Atuador")
            print("3 - Ajustar Atuador (com valor)")
            print("4 - Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                self.enviar_comando("ligar")
            elif opcao == "2":
                self.enviar_comando("desligar")
            elif opcao == "3":
                valor = int(input("Valor do ajuste (ex: velocidade 0-100): ").strip())
                self.enviar_comando("ajustar", valor)
            elif opcao == "4":
                print("[CONTROLADOR] Encerrando...")
                break
            else:
                print("[ERRO] Opção inválida! Escolha 1, 2, 3 ou 4.")

if __name__ == "__main__":
    controlador = Controlador()
    controlador.menu()
