(function () {
  const form = document.getElementById("setup-form");
  const nSez = document.getElementById("n_sezioni");
  const container = document.getElementById("sezioni-container");
  const totaleEl = document.getElementById("totale-elettori");
  const defElettVal = () =>
    parseInt(form?.dataset.elettoriDefault, 10) || 500;
  const tipo = document.getElementById("tipo");
  const listaFields = () => document.querySelectorAll(".lista-field");

  function toggleListe() {
    const show = tipo.value === "liste";
    listaFields().forEach((el) => (el.style.display = show ? "block" : "none"));
  }
  tipo.addEventListener("change", toggleListe);
  toggleListe();

  function readSezioniState() {
    const nomi = container.querySelectorAll('input[name="sezione_nome[]"]');
    const zone = container.querySelectorAll('input[name="sezione_zona[]"]');
    const elettori = container.querySelectorAll('input[name="sezione_elettori[]"]');
    const state = [];
    nomi.forEach((nomeInput, i) => {
      state.push({
        nome: nomeInput.value,
        zona: zone[i] ? zone[i].value : "",
        elettori: elettori[i] ? elettori[i].value : String(defElettVal()),
      });
    });
    return state;
  }

  function updateTotale() {
    const inputs = container.querySelectorAll('input[name="sezione_elettori[]"]');
    let sum = 0;
    inputs.forEach((inp) => {
      sum += parseInt(inp.value, 10) || 0;
    });
    if (totaleEl) totaleEl.textContent = sum.toLocaleString("it-IT");
  }

  function renderSezioni() {
    const n = parseInt(nSez.value, 10) || 1;
    const def = defElettVal();
    const prev = readSezioniState();
    container.innerHTML = "";
    for (let i = 0; i < n; i++) {
      const saved = prev[i];
      const nome = saved ? saved.nome : "Sezione " + (i + 1);
      const zona = saved ? saved.zona : "";
      const elettori = saved ? saved.elettori : def;
      const row = document.createElement("div");
      row.className = "sezione-row grid-3";
      row.innerHTML =
        '<div><label>Nome sezione</label>' +
        '<input type="text" name="sezione_nome[]" value="' +
        escapeAttr(nome) +
        '" required maxlength="80">' +
        "</div>" +
        '<div><label>Zona</label>' +
        '<input type="text" name="sezione_zona[]" value="' +
        escapeAttr(zona) +
        '" maxlength="40" placeholder="Centro, Nord…">' +
        "</div>" +
        '<div><label>Elettori</label>' +
        '<input type="number" name="sezione_elettori[]" value="' +
        escapeAttr(String(elettori)) +
        '" min="1" class="elettori-input"></div>';
      container.appendChild(row);
    }
    container.querySelectorAll(".elettori-input").forEach((inp) => {
      inp.addEventListener("input", updateTotale);
    });
    updateTotale();
  }

  function escapeAttr(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;");
  }

  nSez.addEventListener("input", renderSezioni);
  renderSezioni();

  document.getElementById("add-candidato").onclick = function () {
    const row = document.createElement("div");
    row.className = "candidato-row grid-2";
    row.innerHTML = document.querySelector(".candidato-row").innerHTML;
    row.querySelectorAll("input").forEach((i) => (i.value = ""));
    document.getElementById("candidati-container").appendChild(row);
    toggleListe();
  };
})();
