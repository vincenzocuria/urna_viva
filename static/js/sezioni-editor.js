(function (global) {
  function escapeAttr(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;");
  }

  function readSezioniState(container, defElettVal, includeIds) {
    const ids = includeIds
      ? container.querySelectorAll('input[name="sezione_id[]"]')
      : [];
    const nomi = container.querySelectorAll('input[name="sezione_nome[]"]');
    const zone = container.querySelectorAll('input[name="sezione_zona[]"]');
    const elettori = container.querySelectorAll(
      'input[name="sezione_elettori[]"]'
    );
    const state = [];
    nomi.forEach((nomeInput, i) => {
      state.push({
        id: ids[i] ? ids[i].value : "",
        nome: nomeInput.value,
        zona: zone[i] ? zone[i].value : "",
        elettori: elettori[i] ? elettori[i].value : String(defElettVal()),
      });
    });
    return state;
  }

  function updateTotale(container, totaleEl) {
    if (!totaleEl) return;
    const inputs = container.querySelectorAll(
      'input[name="sezione_elettori[]"]'
    );
    let sum = 0;
    inputs.forEach((inp) => {
      sum += parseInt(inp.value, 10) || 0;
    });
    totaleEl.textContent = sum.toLocaleString("it-IT");
  }

  function renderSezioni(opts) {
    const container = opts.container;
    const n = parseInt(opts.nSezInput.value, 10) || 1;
    const def = opts.defElettVal();
    const includeIds = !!opts.includeIds;
    const prev =
      opts._initialState && !opts._initialized
        ? opts._initialState
        : readSezioniState(container, def, includeIds);
    opts._initialized = true;
    container.innerHTML = "";
    for (let i = 0; i < n; i++) {
      const saved = prev[i];
      const nome = saved ? saved.nome : "Sezione " + (i + 1);
      const zona = saved ? saved.zona : "";
      const elettori = saved ? saved.elettori : def;
      const sid = saved && saved.id ? saved.id : "";
      const row = document.createElement("div");
      row.className = "sezione-row grid-3";
      let html = "";
      if (includeIds) {
        html +=
          '<input type="hidden" name="sezione_id[]" value="' +
          escapeAttr(sid) +
          '">';
      }
      html +=
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
      row.innerHTML = html;
      container.appendChild(row);
    }
    container.querySelectorAll(".elettori-input").forEach((inp) => {
      inp.addEventListener("input", () => updateTotale(container, opts.totaleEl));
    });
    updateTotale(container, opts.totaleEl);
  }

  function init(opts) {
    opts._initialized = false;
    opts.nSezInput.addEventListener("input", () => renderSezioni(opts));
    renderSezioni(opts);
  }

  global.SezioniEditor = { init: init };
})(window);
