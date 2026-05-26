(function () {
  const container = document.getElementById("liste-container");
  const form = document.getElementById("candidati-form");
  if (!container || !form) return;

  function syncListaNames() {
    container.querySelectorAll(".lista-block").forEach((block, idx) => {
      block.dataset.listaIdx = String(idx);
      const nome =
        block.querySelector(".lista-nome-input")?.value.trim() || "Lista";
      block.querySelectorAll(".candidato-lista-hidden").forEach((h) => {
        h.value = nome;
      });
      block.querySelectorAll('input[type="radio"]').forEach((r) => {
        r.name = "capolista_lista__" + idx;
      });
    });
  }

  function sortCandidatiBody(body) {
    const rows = Array.from(body.querySelectorAll("tr"));
    rows.sort((a, b) => {
      const na =
        a.querySelector('input[name="candidato_nome[]"]')?.value.trim() || "";
      const nb =
        b.querySelector('input[name="candidato_nome[]"]')?.value.trim() || "";
      return na.localeCompare(nb, "it", { sensitivity: "base" });
    });
    rows.forEach((tr) => body.appendChild(tr));
  }

  function newCandRow(listaNome, listaIdx, capolista) {
    const tr = document.createElement("tr");
    tr.className = "candidato-row-liste";
    tr.innerHTML =
      '<td><input type="hidden" name="candidato_id[]" value="">' +
      '<input type="hidden" name="candidato_lista[]" value="' +
      escapeAttr(listaNome) +
      '" class="candidato-lista-hidden">' +
      '<input type="text" name="candidato_nome[]" required maxlength="120"></td>' +
      '<td class="capolista-cell"><input type="radio" name="capolista_lista__' +
      listaIdx +
      '" value=""' +
      (capolista ? " checked" : "") +
      "></td>" +
      '<td><button type="button" class="btn btn-small btn-danger btn-rm-cand">✕</button></td>';
    return tr;
  }

  function escapeAttr(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;");
  }

  function addListaBlock(nome) {
    const idx = container.querySelectorAll(".lista-block").length;
    const block = document.createElement("div");
    block.className = "lista-block card";
    block.dataset.listaIdx = String(idx);
    block.innerHTML =
      '<div class="lista-head"><label>Nome lista</label>' +
      '<input type="text" class="lista-nome-input" name="lista_nome_display[]" value="' +
      escapeAttr(nome) +
      '" required maxlength="80"></div>' +
      '<table class="pref-table"><thead><tr><th>Candidato</th><th>Capolista</th><th></th></tr></thead>' +
      '<tbody class="lista-candidati-body"></tbody></table>' +
      '<p class="lista-actions"><button type="button" class="btn btn-secondary btn-small btn-add-cand-lista">+ Candidato</button></p>' +
      '<details class="bulk-import"><summary>Carica nomi da elenco</summary>' +
      '<p class="muted">Un nome per riga (es. dal verbale di seggio).</p>' +
      '<textarea class="bulk-nomi" rows="6" placeholder="ROSSI MARIO"></textarea>' +
      '<button type="button" class="btn btn-secondary btn-small btn-bulk-import">Aggiungi all\'elenco</button></details>';
    container.appendChild(block);
    const body = block.querySelector(".lista-candidati-body");
    body.appendChild(newCandRow(nome, idx, true));
    assignRadioIds(body);
  }

  function assignRadioIds(tbody) {
    tbody.querySelectorAll("tr").forEach((tr) => {
      const radio = tr.querySelector('input[type="radio"]');
      if (!radio) return;
      const id = "new_" + Math.random().toString(36).slice(2, 9);
      radio.value = id;
    });
  }

  container.addEventListener("click", (e) => {
    const t = e.target;
    if (t.classList.contains("btn-add-cand-lista")) {
      const block = t.closest(".lista-block");
      const nome = block.querySelector(".lista-nome-input").value.trim() || "Lista";
      const idx = block.dataset.listaIdx;
      const body = block.querySelector(".lista-candidati-body");
      body.appendChild(newCandRow(nome, idx, false));
      assignRadioIds(body);
      sortCandidatiBody(body);
    }
    if (t.classList.contains("btn-rm-cand")) {
      const row = t.closest("tr");
      const body = row?.closest("tbody");
      if (row && body && body.querySelectorAll("tr").length > 1) {
        row.remove();
        sortCandidatiBody(body);
      }
    }
    if (t.classList.contains("btn-bulk-import")) {
      const block = t.closest(".lista-block");
      const ta = block.querySelector(".bulk-nomi");
      const nome = block.querySelector(".lista-nome-input").value.trim() || "Lista";
      const idx = block.dataset.listaIdx;
      const body = block.querySelector(".lista-candidati-body");
      const lines = (ta.value || "")
        .split(/\r?\n/)
        .map((s) => s.trim())
        .filter(Boolean);
      lines.forEach((line, i) => {
        const tr = newCandRow(nome, idx, i === 0 && body.children.length === 0);
        tr.querySelector('input[type="text"]').value = line;
        body.appendChild(tr);
      });
      assignRadioIds(body);
      sortCandidatiBody(body);
      ta.value = "";
    }
  });

  document.getElementById("add-lista")?.addEventListener("click", () => {
    const n = container.querySelectorAll(".lista-block").length + 1;
    addListaBlock("Lista " + n);
    syncListaNames();
  });

  form.addEventListener("submit", () => {
    syncListaNames();
    container.querySelectorAll(".lista-candidati-body").forEach((body) => {
      sortCandidatiBody(body);
      const rows = body.querySelectorAll("tr");
      rows.forEach((tr, i) => {
        const radio = tr.querySelector('input[type="radio"]');
        const hid = tr.querySelector('input[name="candidato_id[]"]');
        if (radio && hid && !hid.value) {
          const nid = "n_" + Date.now() + "_" + i;
          hid.value = nid;
          radio.value = nid;
        }
      });
    });
  });

  if (!container.querySelector(".lista-block")) {
    addListaBlock("Lista 1");
  }
})();
