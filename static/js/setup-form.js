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

  SezioniEditor.init({
    nSezInput: nSez,
    container: container,
    totaleEl: totaleEl,
    defElettVal: defElettVal,
    includeIds: false,
  });

  document.getElementById("add-candidato").onclick = function () {
    const row = document.createElement("div");
    row.className = "candidato-row grid-2";
    row.innerHTML = document.querySelector(".candidato-row").innerHTML;
    row.querySelectorAll("input").forEach((i) => (i.value = ""));
    document.getElementById("candidati-container").appendChild(row);
    toggleListe();
  };
})();
