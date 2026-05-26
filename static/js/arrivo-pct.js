(function (global) {
  function formatPct(schede, elettori) {
    if (!elettori) return "0,0";
    const p = (Math.max(0, schede) / elettori) * 100;
    return p.toLocaleString("it-IT", {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    });
  }

  function refresh(form) {
    const elett = parseInt(form.dataset.elettori, 10) || 0;
    const input = form.querySelector('[name="schede_scrutinate"]');
    const out = form.querySelector(".pct-votanti-val");
    if (!input || !out) return;
    const schede = parseInt(input.value, 10) || 0;
    out.textContent = formatPct(schede, elett);
  }

  function init() {
    document.querySelectorAll(".arrivo-form").forEach((form) => {
      const input = form.querySelector('[name="schede_scrutinate"]');
      if (!input) return;
      input.addEventListener("input", () => refresh(form));
      refresh(form);
    });
  }

  global.ArrivoPct = { refresh, init };
  init();
})(window);
