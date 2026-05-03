let jobId = null;
let fetchTimeout = null;

function debounceFetchInfo() {
    clearTimeout(fetchTimeout);

    const url = document.getElementById("url").value;
    if (!url) {
        document.getElementById("resolution").style.display = "none";
        document.getElementById("btn-download").style.display = "none";
        document.getElementById("info").innerText = "Aguardando...";
        return;
    }

    fetchTimeout = setTimeout(() => {
        fetchInfo();
    }, 800);
}

async function fetchInfo() {
    const url = document.getElementById("url").value;
    if (!url) return;

    document.getElementById("info").innerText = "Buscando resoluções...";

    try {
        const res = await fetch("/api/info", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });
        const data = await res.json();

        if (data.error) {
            document.getElementById("info").innerText = "Erro ao buscar vídeo.";
            return;
        }

        const select = document.getElementById("resolution");
        select.innerHTML = '<option value="best">Melhor qualidade</option>';
        data.resolutions.forEach(res => {
            select.innerHTML += `<option value="${res}">${res}p</option>`;
        });

        select.style.display = "block";
        document.getElementById("btn-download").style.display = "block";
        document.getElementById("info").innerText = "Selecione a resolução e clique em Baixar.";
    } catch (e) {
        document.getElementById("info").innerText = "Erro ao buscar vídeo.";
    }
}

async function startDownload() {
    const url = document.getElementById("url").value;
    const resolution = document.getElementById("resolution").value;

    if (!url) {
        alert("Cole uma URL primeiro 😅");
        return;
    }

    document.getElementById("info").innerText = "Enviando...";
    document.getElementById("bar").style.width = "0%";
    document.getElementById("download").style.display = "none";

    const res = await fetch("/api/download", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ url, resolution })
    });

    const data = await res.json();
    jobId = data.job_id;

    pollProgress();
}

async function pollProgress() {
    const interval = setInterval(async () => {
        const res = await fetch(`/api/status/${jobId}`);
        const data = await res.json();

        if (data.progress) {
            document.getElementById("bar").style.width = data.progress;
        }

        document.getElementById("info").innerText =
            `${data.status} ${data.speed || ""} ${data.eta || ""}`;

        if (data.status === "finished") {
            clearInterval(interval);
            document.getElementById("bar").style.width = "100%";

            const file = data.result.file;
            const link = document.getElementById("fileLink");

            link.href = `/api/file/${file}`;
            document.getElementById("download").style.display = "block";

            document.getElementById("info").innerText = "Pronto!";
        }

        if (data.status === "error") {
            clearInterval(interval);
            document.getElementById("info").innerText = "Erro 😢";
        }

    }, 500);
}
