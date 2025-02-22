from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

GATEWAY_URL = "http://localhost:5001"  # URL do gateway

@app.route("/")
def home():
    """Renderiza o index.html"""
    return render_template("index.html")

@app.route("/dispositivos", methods=["GET"])
def listar_dispositivos():
    """Retorna a lista de dispositivos disponíveis."""
    response = requests.get(f"{GATEWAY_URL}/dispositivos")
    return jsonify(response.json()), response.status_code

@app.route("/dispositivos/<string:nome>", methods=["GET"])
def consultar_estado(nome):
    """Consulta o estado de um dispositivo"""
    response = requests.get(f"{GATEWAY_URL}/dispositivos/{nome}")
    return jsonify(response.json()), response.status_code

@app.route("/dispositivos/<string:nome>/ligar", methods=["POST"])
def ligar_dispositivo(nome):
    """Liga um dispositivo"""
    response = requests.post(f"{GATEWAY_URL}/dispositivos/{nome}/ligar")
    return jsonify(response.json()), response.status_code

@app.route("/dispositivos/<string:nome>/desligar", methods=["POST"])
def desligar_dispositivo(nome):
    """Desliga um dispositivo"""
    response = requests.post(f"{GATEWAY_URL}/dispositivos/{nome}/desligar")
    return jsonify(response.json()), response.status_code

@app.route("/dispositivos/<string:nome>/configurar", methods=["POST"])
def configurar_dispositivo(nome):
    """Ajusta a configuração de um dispositivo"""
    dados = request.json
    response = requests.post(f"{GATEWAY_URL}/dispositivos/{nome}/configurar", json=dados)
    return jsonify(response.json()), response.status_code

if __name__ == "__main__":
    app.run(debug=True, port=5000)
