document.addEventListener("DOMContentLoaded", function () {
    setInterval(atualizarSensores, 3000); // Atualiza os sensores a cada 3 segundos
});

function atualizarSensores() {
    fetch("http://localhost:5000/dispositivos")
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Dados recebidos:", data);
            atualizarValor("sensor-temperatura", data["temp_01"], "Temperatura");
            atualizarValor("sensor-luminosidade", data["ldr_01"], "Luminosidade");
        })
        .catch(error => {
            console.error("Erro ao buscar dados dos sensores:", error);
            document.getElementById("sensor-temperatura").innerText = "Erro ao carregar.";
            document.getElementById("sensor-luminosidade").innerText = "Erro ao carregar.";
        });
}

function atualizarValor(elementoId, sensorData, nomeExibicao) {
    let elemento = document.getElementById(elementoId);
    
    if (!sensorData) {
        elemento.innerText = `${nomeExibicao}: Aguardando dados...`;
        return;
    }

    let valor = parseFloat(sensorData.valor).toFixed(2); // Arredonda para 2 casas decimais
    let unidade = sensorData.unidade || "";
    
    // Formatar timestamp para HH:MM:SS
    let timestamp = new Date(sensorData.timestamp * 1000);
    let horaFormatada = timestamp.toLocaleTimeString("pt-BR", { hour12: false });

    elemento.innerHTML = `<strong>${nomeExibicao}</strong>: ${valor} ${unidade} <br>`;
}

function controlarAtuador(dispositivo, acao) {
    fetch(`http://localhost:5000/dispositivos/${dispositivo}/${acao}`, { method: "POST" })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            alert(`${dispositivo.charAt(0).toUpperCase() + dispositivo.slice(1)}: ${data.status}`);
        })
        .catch(error => {
            console.error("Erro ao controlar atuador:", error);
            alert(`Erro ao enviar comando para ${dispositivo}.`);
        });
}
