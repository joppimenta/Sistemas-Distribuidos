const API_URL = "http://localhost:5000/";

async function consultarEstado() {
    const nome = document.getElementById("device_name").value;
    const response = await fetch(`${API_URL}/${nome}`);
    document.getElementById("response").innerText = await response.text();
}

async function ligarDispositivo() {
    const nome = document.getElementById("device_name").value;
    const response = await fetch(`${API_URL}/${nome}/ligar`, { method: "POST" });
    document.getElementById("response").innerText = await response.text();
}

async function desligarDispositivo() {
    const nome = document.getElementById("device_name").value;
    const response = await fetch(`${API_URL}/${nome}/desligar`, { method: "POST" });
    document.getElementById("response").innerText = await response.text();
}

async function configurarDispositivo() {
    const nome = document.getElementById("device_name").value;
    const config = document.getElementById("config").value;
    const response = await fetch(`${API_URL}/${nome}/configurar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ config })
    });
    document.getElementById("response").innerText = await response.text();
}
