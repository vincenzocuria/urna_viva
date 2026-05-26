(function () {

  function intVal(el) {

    return parseInt(el.value, 10) || 0;

  }



  function setVal(el, n) {

    if (!el) return;

    el.value = Math.max(0, n);

  }



  function formatPct(somma, votiValidi) {

    if (!votiValidi) return "0,0";

    const pct = Math.min(100, (somma / votiValidi) * 100);

    return pct.toLocaleString("it-IT", {

      minimumFractionDigits: 1,

      maximumFractionDigits: 1,

    });

  }



  function getInputs(form) {

    return {

      scrutinate: parseInt(form.dataset.schede, 10) || 0,

      validi: form.querySelector('[name="voti_validi"]'),

      nulli: form.querySelector('[name="nulli"]'),

      contestati: form.querySelector('[name="contestati"]'),

      bianche: form.querySelector('[name="bianche"]'),

      votiCandidati: form.querySelectorAll('[name^="voto_"]'),

      prefInputs: form.querySelectorAll(".pref-input"),

      riepilogo: form.querySelector(".sync-riepilogo"),

      pctVal: form.querySelector(".spoglio-pct-val"),

      pctBar: form.querySelector(".spoglio-pct-bar"),

      progressBox: form.querySelector(".spoglio-sezione-progress"),

    };

  }



  function sommaAltri(f) {

    return intVal(f.nulli) + intVal(f.contestati) + intVal(f.bianche);

  }



  function sommaVotiCandidati(f) {

    let s = 0;

    if (f.prefInputs.length) {

      f.prefInputs.forEach((inp) => {

        s += intVal(inp);

      });

      return s;

    }

    f.votiCandidati.forEach((inp) => {

      s += intVal(inp);

    });

    return s;

  }



  function aggiornaValidi(f) {

    setVal(f.validi, Math.max(0, f.scrutinate - sommaAltri(f)));

    if (f.validi) f.validi.dispatchEvent(new Event("input"));

  }



  function aggiornaProgressoForm(form, f, vv, cand) {

    if (!f.progressBox && !f.pctVal && !f.pctBar) return;

    const visible = vv > 0;

    if (f.progressBox) f.progressBox.hidden = !visible;

    if (!visible) return;

    const pctNum = Math.min(100, (cand / vv) * 100);

    const pctText = formatPct(cand, vv);

    if (f.pctVal) f.pctVal.textContent = pctText;

    if (f.pctBar) f.pctBar.style.width = pctNum + "%";

  }



  function aggiornaTotaleSpoglio() {

    const box = document.getElementById("spoglio-totale");

    if (!box) return;

    let totVv = 0;

    let totSomma = 0;

    document.querySelectorAll(".spoglio-form, .spoglio-form-liste").forEach((form) => {

      const f = getInputs(form);

      const vv = intVal(f.validi);

      if (vv <= 0) return;

      totVv += vv;

      totSomma += sommaVotiCandidati(f);

    });

    box.hidden = totVv <= 0;

    if (totVv <= 0) return;

    const pctNum = Math.min(100, (totSomma / totVv) * 100);

    const pctVal = box.querySelector(".spoglio-totale-pct");

    const pctBar = box.querySelector(".spoglio-totale-bar");

    if (pctVal) pctVal.textContent = formatPct(totSomma, totVv);

    if (pctBar) pctBar.style.width = pctNum + "%";

  }



  function aggiornaRiepilogo(form, f) {

    const vv = intVal(f.validi);

    const altri = sommaAltri(f);

    const cand = sommaVotiCandidati(f);

    aggiornaProgressoForm(form, f, vv, cand);

    aggiornaTotaleSpoglio();



    if (!f.riepilogo) return;

    const scr = f.scrutinate;

    const superaSchede = altri > scr;

    const isListe = f.prefInputs.length > 0;

    const candidatiFuori = (f.votiCandidati.length || f.prefInputs.length) && cand > vv;

    const mancano = vv > 0 ? Math.max(0, vv - cand) : 0;

    const spoglioIncompleto = !isListe && mancano > 0;

    const eccedenza = isListe && vv > 0 && cand > vv ? cand - vv : 0;



    if (superaSchede) {

      f.riepilogo.textContent =

        "Errore: nulli + contestati + bianche (" +

        altri +

        ") superano le schede votate (" +

        scr +

        "). Riduci i valori prima di salvare.";

    } else if (eccedenza > 0) {

      f.riepilogo.textContent =

        "Eccedenza di " +

        eccedenza +

        " voti — la somma dei totali lista supera i voti validi";

    } else if (candidatiFuori) {

      f.riepilogo.textContent =

        "Attenzione: somma candidati supera i voti validi";

    } else if (spoglioIncompleto) {

      f.riepilogo.textContent = "Mancano " + mancano + " voti";

    } else {

      f.riepilogo.textContent = "";

    }



    f.riepilogo.classList.toggle(

      "sync-warn",

      superaSchede || eccedenza > 0 || candidatiFuori || spoglioIncompleto

    );

    const submit = form.querySelector('[type="submit"]');

    if (submit) submit.disabled = superaSchede;

  }



  function bindForm(form) {

    const f = getInputs(form);

    if (!f.validi) return;



    function refresh() {

      aggiornaValidi(f);

      aggiornaRiepilogo(form, f);

    }



    [f.nulli, f.contestati, f.bianche].forEach((el) => {

      if (!el) return;

      el.addEventListener("input", refresh);

    });



    f.votiCandidati.forEach((el) => {

      el.addEventListener("input", refresh);

    });



    f.prefInputs.forEach((el) => {

      el.addEventListener("input", refresh);

    });



    refresh();

  }



  document.querySelectorAll(".spoglio-form, .spoglio-form-liste").forEach(bindForm);

})();

