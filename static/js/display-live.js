(function () {
  const body = document.body;
  const sessionId = body.dataset.session;
  const pollMs = parseInt(body.dataset.poll, 10) || 2500;
  const previewLimit =
    parseInt(body.dataset.sezioniPreview, 10) || 6;
  let lastRevision = null;
  const RING_LEN = 327;

  const els = {
    comuneName: document.getElementById("comune-name"),
    tipoLabel: document.getElementById("tipo-label"),
    logo: document.getElementById("comune-logo"),
    logoPh: document.getElementById("logo-placeholder"),
    avanzamentoPct: document.getElementById("avanzamento-pct"),
    ringFg: document.getElementById("ring-fg"),
    progressFill: document.getElementById("progress-fill"),
    schedeScr: document.getElementById("schede-scrutinate"),
    schedeTot: document.getElementById("schede-totali"),
    updatedAt: document.getElementById("updated-at"),
    esitoBadge: document.getElementById("esito-badge"),
    ballottaggioBox: document.getElementById("ballottaggio-box"),
    candidatiList: document.getElementById("candidati-list"),
    sezioniPreview: document.getElementById("sezioni-preview"),
    sezioniCount: document.getElementById("sezioni-count"),
    btnSezioniTutte: document.getElementById("btn-sezioni-tutte"),
    sezioniOverlay: document.getElementById("sezioni-overlay"),
    sezioniOverlayGrid: document.getElementById("sezioni-overlay-grid"),
    btnOverlayChiudi: document.getElementById("btn-overlay-chiudi"),
    sezioniOverlayClose: document.getElementById("sezioni-overlay-close"),
  };

  function setRing(pct) {
    const offset = RING_LEN - (RING_LEN * Math.min(100, pct)) / 100;
    els.ringFg.style.strokeDashoffset = offset;
  }

  function esitoClass(stato) {
    if (stato === "vittoria_primo_turno") return "esito-vittoria";
    if (stato === "ballottaggio") return "esito-ballottaggio";
    return "esito-incerto";
  }

  function formatTime(iso) {
    if (!iso) return "—";
    try {
      const d = new Date(iso);
      return d.toLocaleTimeString("it-IT", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return iso;
    }
  }

  function sezItemHtml(s, compact) {
    const cls = [
      "sez-item",
      s.ha_dati ? (s.avanzamento_pct >= 99 ? "completa" : "") : "inattiva",
    ]
      .filter(Boolean)
      .join(" ");
    const cardCls = cls.replace("sez-item", "sez-card");
    const leader = s.leader_nome
      ? `${escapeHtml(s.leader_nome)} (${s.leader_pct}%)`
      : s.ha_dati
        ? "—"
        : "In attesa";
    if (compact) {
      return `<div class="${cls}">
        <span class="sez-nome">${escapeHtml(s.nome)}</span>
        <span class="sez-pct">${s.avanzamento_pct}%</span>
        <span class="sez-meta">${s.schede_scrutinate}/${s.elettori}</span>
        <span class="sez-leader">${leader}</span>
        <div class="sez-bar"><div class="sez-bar-fill" style="width:${s.avanzamento_pct}%"></div></div>
      </div>`;
    }
    return `<div class="${cardCls}">
      <h3>${escapeHtml(s.nome)}</h3>
      <div class="sez-stats">${s.schede_scrutinate.toLocaleString("it-IT")} / ${s.elettori.toLocaleString("it-IT")} schede · ${s.avanzamento_pct}%</div>
      <div class="sez-leader-full">${leader}</div>
      <div class="sez-bar"><div class="sez-bar-fill" style="width:${s.avanzamento_pct}%"></div></div>
    </div>`;
  }

  function renderSezioni(sezioni, total) {
    if (!els.sezioniPreview) return;
    const list = sezioni || [];
    const n = total != null ? total : list.length;
    if (els.sezioniCount) els.sezioniCount.textContent = n;
    if (els.btnSezioniTutte) {
      els.btnSezioniTutte.hidden = n === 0;
    }
    const preview = list.slice(0, previewLimit);
    els.sezioniPreview.style.setProperty(
      "--n-sez-preview",
      String(Math.max(preview.length, 1))
    );
    els.sezioniPreview.innerHTML =
      preview.length > 0
        ? preview.map((s) => sezItemHtml(s, true)).join("")
        : '<div class="sez-item inattiva"><span class="sez-nome">Nessuna sezione</span></div>';
    if (els.sezioniOverlayGrid) {
      els.sezioniOverlayGrid.innerHTML = list
        .map((s) => sezItemHtml(s, false))
        .join("");
    }
  }

  function openSezioniOverlay() {
    document.body.classList.add("display-overlay-open");
    els.sezioniOverlay?.classList.add("open");
    els.sezioniOverlay?.setAttribute("aria-hidden", "false");
    requestAnimationFrame(() => {
      els.sezioniOverlayGrid?.scrollTo(0, 0);
    });
  }

  function closeSezioniOverlay() {
    document.body.classList.remove("display-overlay-open");
    els.sezioniOverlay?.classList.remove("open");
    els.sezioniOverlay?.setAttribute("aria-hidden", "true");
  }

  els.btnSezioniTutte?.addEventListener("click", openSezioniOverlay);
  els.btnOverlayChiudi?.addEventListener("click", closeSezioniOverlay);
  els.sezioniOverlayClose?.addEventListener("click", closeSezioniOverlay);

  function renderCandidati(candidati) {
    const sorted = [...candidati].sort(
      (a, b) => b.pct_proiettate - a.pct_proiettate
    );
    const n = Math.max(sorted.length, 1);
    els.candidatiList.style.setProperty("--n-candidati", String(n));
    els.candidatiList.dataset.count = String(sorted.length);

    els.candidatiList.innerHTML = sorted
      .map((c, i) => {
        const leader = i === 0 && c.pct_proiettate > 0;
        const nome = c.nome_display || c.nome;
        const lista = c.lista
          ? `<div class="cand-lista">${escapeHtml(c.lista)}</div>`
          : "";
        return `
        <div class="cand-row ${leader ? "leader" : ""}">
          <div class="cand-rank" style="color:${c.color}">${i + 1}</div>
          <div class="cand-main">
            <div class="cand-top">
              <div class="cand-names">
                <div class="cand-name">${escapeHtml(nome)}</div>
                ${lista}
              </div>
              <div class="cand-pct" style="color:${c.color}">${c.pct_proiettate}%</div>
            </div>
            <div class="cand-bar-wrap">
              <div class="cand-bar" style="width:${c.pct_reali}%;background:${c.color}"></div>
              <div class="cand-bar cand-bar-proj" style="width:${c.pct_proiettate}%;background:${c.color}"></div>
            </div>
          </div>
          <div class="cand-voti-mini">${c.voti_proiettati.toLocaleString("it-IT")}<br>proj.</div>
        </div>`;
      })
      .join("");
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function render(data) {
    const p = data.proiezione;
    const es = p.esito || {};
    els.comuneName.textContent = data.comune;
    els.tipoLabel.textContent = p.tipo_label || "";
    const pct = p.avanzamento_pct || 0;
    els.avanzamentoPct.textContent = pct;
    setRing(pct);
    els.progressFill.style.width = pct + "%";
    els.schedeScr.textContent = (p.schede_scrutinate || 0).toLocaleString(
      "it-IT"
    );
    els.schedeTot.textContent = (p.schede_totali || 0).toLocaleString("it-IT");
    els.updatedAt.textContent = formatTime(data.revision);

    els.esitoBadge.textContent = es.messaggio || "—";
    els.esitoBadge.className = "esito-badge " + esitoClass(es.stato);

    if (es.ballottaggio && es.ballottaggio.length) {
      els.ballottaggioBox.classList.remove("hidden");
      els.ballottaggioBox.innerHTML =
        es.ballottaggio
          .map((b) => `${b.nome_display || b.nome} (${b.pct_proiettate}%)`)
          .join(" · ");
    } else {
      els.ballottaggioBox.classList.add("hidden");
    }

    if (data.logo && data.logo.display) {
      els.logo.src =
        data.logo.display + "?t=" + encodeURIComponent(data.revision);
      els.logo.classList.remove("hidden");
      els.logoPh.style.display = "none";
    } else {
      els.logo.classList.add("hidden");
      els.logoPh.style.display = "block";
    }

    renderCandidati(p.candidati || []);
    renderSezioni(data.sezioni, data.sezioni_totali);
  }

  async function poll() {
    try {
      const r = await fetch(`/api/scrutinio/${sessionId}/live`);
      if (!r.ok) return;
      const data = await r.json();
      if (lastRevision && data.revision !== lastRevision) {
        body.classList.add("flash-update");
        setTimeout(() => body.classList.remove("flash-update"), 400);
      }
      lastRevision = data.revision;
      render(data);
    } catch (e) {
      console.warn("Poll error", e);
    }
  }

  poll();
  setInterval(poll, pollMs);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeSezioniOverlay();
    if (e.key === "f" || e.key === "F") {
      if (!document.fullscreenElement)
        document.documentElement.requestFullscreen?.();
      else document.exitFullscreen?.();
    }
    if (e.key === "s" || e.key === "S") {
      if (els.sezioniOverlay?.classList.contains("open")) closeSezioniOverlay();
      else openSezioniOverlay();
    }
  });
})();
