(function () {
  function intVal(el) {
    return parseInt(el?.value, 10) || 0;
  }

  function capInput(block) {
    return block.querySelector("tr[data-capolista='1'] .pref-input");
  }

  function sumConsiglieri(block) {
    let s = 0;
    block.querySelectorAll("tr[data-capolista='0'] .pref-input").forEach((inp) => {
      s += intVal(inp);
    });
    return s;
  }

  function aggiornaLista(block) {
    const cons = sumConsiglieri(block);
    const cap = intVal(capInput(block));
    const tot = cons + cap;
    const outCons = block.querySelector(".lista-sub-consiglieri");
    const outCap = block.querySelector(".lista-sub-capolista");
    const outTot = block.querySelector(".lista-totale-pref");
    if (outCons) outCons.textContent = cons.toLocaleString("it-IT");
    if (outCap) outCap.textContent = cap.toLocaleString("it-IT");
    if (outTot) outTot.textContent = tot.toLocaleString("it-IT");

    const verbaleInp = block.querySelector(".lista-verbale-input");
    const diffRow = block.querySelector(".lista-verbale-diff-row");
    const diffCell = block.querySelector(".lista-verbale-diff");
    const verbale = intVal(verbaleInp);
    if (diffRow && diffCell) {
      if (verbale > 0) {
        const delta = tot - verbale;
        diffRow.classList.remove("hidden");
        diffCell.textContent =
          (delta === 0 ? "OK" : (delta > 0 ? "+" : "") + delta.toLocaleString("it-IT"));
        diffCell.classList.toggle("pref-warn", delta !== 0);
        diffCell.classList.toggle("pref-ok", delta === 0);
      } else {
        diffRow.classList.add("hidden");
      }
    }
    return { nome: block.dataset.lista || "", tot };
  }

  function impostaCapDaVerbale(block) {
    const verbaleInp = block.querySelector(".lista-verbale-input");
    const cap = capInput(block);
    if (!verbaleInp || !cap) return;
    const target = intVal(verbaleInp);
    const cons = sumConsiglieri(block);
    cap.value = Math.max(0, target - cons);
    cap.dispatchEvent(new Event("input", { bubbles: true }));
  }

  function bindForm(form) {
    const validiEl = form.querySelector('[name="voti_validi"]');
    const prefInputs = form.querySelectorAll(".pref-input");
    if (!prefInputs.length) return;

    const globTot = form.querySelector(".pref-totale-globale");
    const globVal = form.querySelector(".pref-voti-validi");
    const globRem = form.querySelector(".pref-rimanenti");
    const bilancioLabel = form.querySelector(".pref-bilancio-label");
    const bilancioHint = form.querySelector(".pref-bilancio-hint");
    const summaryListe = form.querySelector(".pref-summary-liste");

    function refresh() {
      const validi = intVal(validiEl);
      let tot = 0;
      const parti = [];
      form.querySelectorAll(".lista-pref-block").forEach((block) => {
        const info = aggiornaLista(block);
        tot += info.tot;
        if (info.nome) {
          parti.push(info.nome + ": " + info.tot.toLocaleString("it-IT"));
        }
      });
      const rim = validi - tot;
      if (globTot) globTot.textContent = tot.toLocaleString("it-IT");
      if (globVal) globVal.textContent = validi.toLocaleString("it-IT");
      if (globRem) {
        if (rim > 0) {
          globRem.textContent = rim.toLocaleString("it-IT");
          globRem.classList.add("pref-warn");
          globRem.classList.remove("pref-ok", "pref-over");
          if (bilancioLabel) bilancioLabel.textContent = "Mancano voti di lista";
          if (bilancioHint) {
            bilancioHint.textContent =
              "Ogni votante sceglie una lista: aggiungi preferenze o metti il residuo sul capolista ★ (senza pref.).";
          }
        } else if (rim < 0) {
          globRem.textContent = Math.abs(rim).toLocaleString("it-IT");
          globRem.classList.add("pref-over");
          globRem.classList.remove("pref-warn", "pref-ok");
          if (bilancioLabel) bilancioLabel.textContent = "Eccedenza";
          if (bilancioHint) {
            bilancioHint.textContent =
              "La somma delle liste supera i voti validi: correggi i numeri o il verbale.";
          }
        } else {
          globRem.textContent = "0";
          globRem.classList.add("pref-ok");
          globRem.classList.remove("pref-warn", "pref-over");
          if (bilancioLabel) bilancioLabel.textContent = "Bilancio OK";
          if (bilancioHint) bilancioHint.textContent = "Lista 1 + Lista 2 = voti validi.";
        }
      }
      if (summaryListe) {
        summaryListe.textContent = parti.length ? " · " + parti.join(" · ") : "";
      }
    }

    prefInputs.forEach((inp) => inp.addEventListener("input", refresh));
    form.querySelectorAll(".lista-verbale-input").forEach((inp) => {
      inp.addEventListener("input", refresh);
    });
    form.querySelectorAll(".btn-cap-da-verbale").forEach((btn) => {
      btn.addEventListener("click", () => {
        const block = btn.closest(".lista-pref-block");
        if (block) impostaCapDaVerbale(block);
      });
    });
    if (validiEl) validiEl.addEventListener("input", refresh);
    refresh();
  }

  document.querySelectorAll(".spoglio-form-liste").forEach(bindForm);
})();
