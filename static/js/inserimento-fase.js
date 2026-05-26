(function () {
  document.querySelectorAll(".btn-unlock-schede").forEach((btn) => {
    btn.addEventListener("click", () => {
      const msg =
        "Modificare il totale delle schede votate?\n\n" +
        "Usa questa opzione solo se il dato precedente era errato. " +
        "Verifica che lo spoglio resti coerente.";
      if (!confirm(msg)) return;
      const form = btn.closest(".arrivo-form");
      const input = form.querySelector('[name="schede_scrutinate"]');
      const conferma = form.querySelector('[name="conferma_modifica"]');
      const submit = form.querySelector(".btn-arrivo-submit");
      input.removeAttribute("readonly");
      input.classList.remove("locked-field");
      if (conferma) conferma.value = "1";
      if (submit) submit.textContent = "Salva nuovo totale";
      btn.style.display = "none";
      input.focus();
      input.select();
      if (window.ArrivoPct) ArrivoPct.refresh(form);
    });
  });
})();
