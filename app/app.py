from flask import Flask, render_template, jsonify, request
import requests
from flask_cors import CORS  # Importa CORS

app = Flask(__name__)
CORS(app)  # Ativa CORS para todas as rotas

GATEWAY_URL = "http://localhost:5001"

@app.route("/")
def home():
    """Renderiza a página principal."""
    return render_template("index.html")

@app.route("/dispositivos", methods=["GET"])
def listar_dispositivos():
    """Obtém os valores dos sensores do gateway."""
    try:
        response = requests.get(f"{GATEWAY_URL}/dispositivos", timeout=5)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao conectar ao gateway: {e}")
        return jsonify({"erro": "Falha ao conectar ao gateway"}), 500

@app.route("/dispositivos/<string:nome>/ligar", methods=["POST"])
def ligar_dispositivo(nome):
    """Liga um dispositivo."""
    try:
        response = requests.post(f"{GATEWAY_URL}/dispositivos/{nome}/ligar", timeout=5)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao conectar ao gateway: {e}")
        return jsonify({"erro": "Falha ao conectar ao gateway"}), 500

@app.route("/dispositivos/<string:nome>/desligar", methods=["POST"])
def desligar_dispositivo(nome):
    """Desliga um dispositivo."""
    try:
        response = requests.post(f"{GATEWAY_URL}/dispositivos/{nome}/desligar", timeout=5)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao conectar ao gateway: {e}")
        return jsonify({"erro": "Falha ao conectar ao gateway"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
