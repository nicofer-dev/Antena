document.addEventListener("DOMContentLoaded", async () => {
    try {
        // Obtener datos del backend
        const response = await fetch("/api/analisis");
        const data = await response.json();

        console.log("Datos recibidos:", data); // 👀 para depurar

        const paginas = data.paginas;
        const existentes = data.existentes;
        const nuevas = data.nuevas;

        // =====================
        // Gráfico 1 - Convocatorias existentes
        // =====================
        const ctx1 = document.getElementById("graficoExistentes").getContext("2d");
        new Chart(ctx1, {
            type: "bar",
            data: {
                labels: paginas,
                datasets: [{
                    label: "Convocatorias Existentes",
                    data: existentes,
                    backgroundColor: "rgba(54, 162, 235, 0.6)",
                    borderColor: "rgba(54, 162, 235, 1)",
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: "top" },
                    title: { display: true, text: "Convocatorias Existentes" }
                }
            }
        });

        // =====================
        // Gráfico 2 - Convocatorias nuevas
        // =====================
        const ctx2 = document.getElementById("graficoNuevas").getContext("2d");
        new Chart(ctx2, {
            type: "bar",
            data: {
                labels: paginas,
                datasets: [{
                    label: "Convocatorias Nuevas",
                    data: nuevas,
                    backgroundColor: "rgba(255, 99, 132, 0.6)",
                    borderColor: "rgba(255, 99, 132, 1)",
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: "top" },
                    title: { display: true, text: "Convocatorias Nuevas" }
                }
            }
        });

    } catch (error) {
        console.error("❌ Error cargando datos para análisis:", error);
    }
});


