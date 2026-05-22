(function () {
  function intVal(el) {
    return parseInt(el.value, 10) || 0;
  }

  function setVal(el, n) {
    if (!el) return;
    el.value = Math.max(0, n);
  }

  function getInputs(form) {
    return {
      scrutinate: form.querySelector('[name="schede_scrutinate"]'),
      validi: form.querySelector('[name="voti_validi"]'),
      nulli: form.querySelector('[name="nulli"]'),
      contestati: form.querySelector('[name="contestati"]'),
      bianche: form.querySelector('[name="bianche"]'),
      votiCandidati: form.querySelectorAll('[name^="voto_"]'),
      riepilogo: form.querySelector(".sync-riepilogo"),
    };
  }

  function sommaAltri(f) {
    return intVal(f.nulli) + intVal(f.contestati) + intVal(f.bianche);
  }

  function sommaVotiCandidati(f) {
    let s = 0;
    f.votiCandidati.forEach((inp) => {
      s += intVal(inp);
    });
    return s;
  }

  function aggiornaRiepilogo(form, f) {
    if (!f.riepilogo) return;
    const scr = intVal(f.scrutinate);
    const vv = intVal(f.validi);
    const altri = sommaAltri(f);
    const cand = sommaVotiCandidati(f);
    f.riepilogo.textContent =
      "Scrutinate: " +
      scr +
      " = Validi " +
      vv +
      " + Nulli/contestati/bianche " +
      altri +
      (f.votiCandidati.length
        ? " · Somma candidati: " + cand
        : "");
    f.riepilogo.classList.toggle(
      "sync-warn",
      f.votiCandidati.length && Math.abs(cand - vv) > 2
    );
  }

  function ricalcolaScrutinate(f) {
    setVal(f.scrutinate, intVal(f.validi) + sommaAltri(f));
  }

  function daScrutinate(f) {
    const scr = intVal(f.scrutinate);
    const altri = sommaAltri(f);
    setVal(f.validi, Math.max(0, scr - altri));
  }

  function daVotiCandidati(form, f) {
    const sum = sommaVotiCandidati(f);
    if (sum > 0) {
      setVal(f.validi, sum);
      ricalcolaScrutinate(f);
    }
    aggiornaRiepilogo(form, f);
  }

  function bindForm(form) {
    const f = getInputs(form);
    if (!f.scrutinate || !f.validi) return;

    let lock = false;
    function run(fn) {
      if (lock) return;
      lock = true;
      fn();
      aggiornaRiepilogo(form, f);
      lock = false;
    }

    f.scrutinate.addEventListener("input", () =>
      run(() => daScrutinate(f))
    );

    [f.nulli, f.contestati, f.bianche].forEach((el) => {
      if (!el) return;
      el.addEventListener("input", () => run(() => ricalcolaScrutinate(f)));
    });

    f.validi.addEventListener("input", () =>
      run(() => ricalcolaScrutinate(f))
    );

    f.votiCandidati.forEach((el) => {
      el.addEventListener("input", () =>
        run(() => daVotiCandidati(form, f))
      );
    });

    aggiornaRiepilogo(form, f);
  }

  document.querySelectorAll(".inserimento-form").forEach(bindForm);
})();
