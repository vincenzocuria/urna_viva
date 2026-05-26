(function () {
  const form = document.getElementById("modifica-form");
  if (!form) return;

  let initialState = [];
  try {
    initialState = JSON.parse(form.dataset.initialSezioni || "[]");
  } catch (_e) {
    initialState = [];
  }

  SezioniEditor.init({
    nSezInput: document.getElementById("n_sezioni"),
    container: document.getElementById("sezioni-container"),
    totaleEl: document.getElementById("totale-elettori"),
    defElettVal: () => parseInt(form.dataset.elettoriDefault, 10) || 500,
    includeIds: true,
    _initialState: initialState.map((s) => ({
      id: s.id || "",
      nome: s.nome || "",
      zona: s.zona || "",
      elettori: String(s.elettori || form.dataset.elettoriDefault || 500),
    })),
  });
})();
