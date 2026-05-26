(function () {
  const container = document.getElementById("candidati-edit-container");
  const form = document.getElementById("candidati-form");
  if (!container) return;

  function sortDirectCandidati() {
    const rows = Array.from(container.querySelectorAll(".candidato-row"));
    rows.sort((a, b) => {
      const na =
        a.querySelector('input[name="candidato_nome[]"]')?.value.trim() || "";
      const nb =
        b.querySelector('input[name="candidato_nome[]"]')?.value.trim() || "";
      return na.localeCompare(nb, "it", { sensitivity: "base" });
    });
    rows.forEach((row) => container.appendChild(row));
  }

  document.getElementById("add-cand-edit")?.addEventListener("click", () => {
    const row = document.createElement("div");
    row.className = "candidato-row grid-2";
    row.innerHTML =
      '<input type="hidden" name="candidato_id[]" value="">' +
      '<input type="hidden" name="candidato_lista[]" value="">' +
      '<div><label>Nome</label><input type="text" name="candidato_nome[]" required></div>';
    container.appendChild(row);
    sortDirectCandidati();
  });

  form?.addEventListener("submit", sortDirectCandidati);
})();
