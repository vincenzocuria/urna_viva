(function () {
  const body = document.body;
  const sessionId = body.dataset.session;
  const pollMs = parseInt(body.dataset.poll, 10) || 2500;
  const previewLimit =
    parseInt(body.dataset.sezioniPreview, 10) || 6;
  let lastRevision = null;
  let sezioniCache = [];
  let tipoCache = "";
  const RING_LEN = 327;

  const els = {
    comuneName: document.getElementById("comune-name"),
    tipoLabel: document.getElementById("tipo-label"),
    logo: document.getElementById("comune-logo"),
    logoPh: document.getElementById("logo-placeholder"),
    avanzamentoPct: document.getElementById("avanzamento-pct"),
    ringFg: document.getElementById("ring-fg"),
    progressFill: document.getElementById("progress-fill"),
    schedeVotateArr: document.getElementById("schede-votate-arrivate"),
    schedeVotateFinale: document.getElementById("schede-votate-finale"),
    schedeFinaleWrap: document.getElementById("schede-finale-wrap"),
    schedeFinalePrefix: document.getElementById("schede-finale-prefix"),
    sezioniArrivoLabel: document.getElementById("sezioni-arrivo-label"),
    schedeTot: document.getElementById("schede-totali"),
    updatedAt: document.getElementById("updated-at"),
    esitoBadge: document.getElementById("esito-badge"),
    ballottaggioBox: document.getElementById("ballottaggio-box"),
    candidatiList: document.getElementById("candidati-list"),
    sindacoConfronto: document.getElementById("sindaco-confronto"),
    alertSindaco: document.getElementById("alert-sindaco"),
    sezioniPreview: document.getElementById("sezioni-preview"),
    sezioniCount: document.getElementById("sezioni-count"),
    btnSezioniTutte: document.getElementById("btn-sezioni-tutte"),
    sezioniOverlay: document.getElementById("sezioni-overlay"),
    sezioniOverlayGrid: document.getElementById("sezioni-overlay-grid"),
    btnOverlayChiudi: document.getElementById("btn-overlay-chiudi"),
    sezioniOverlayClose: document.getElementById("sezioni-overlay-close"),
    candidatiTitle: document.getElementById("candidati-title"),
    btnPreferenze: document.getElementById("btn-preferenze"),
    preferenzeOverlay: document.getElementById("preferenze-overlay"),
    preferenzeOverlayBody: document.getElementById("preferenze-overlay-body"),
    btnPreferenzeChiudi: document.getElementById("btn-preferenze-chiudi"),
    preferenzeOverlayClose: document.getElementById("preferenze-overlay-close"),
    sezioneDettaglioOverlay: document.getElementById("sezione-dettaglio-overlay"),
    sezioneDettaglioBody: document.getElementById("sezione-dettaglio-body"),
    sezioneDettaglioTitle: document.getElementById("sezione-dettaglio-title"),
    btnSezioneIndietro: document.getElementById("btn-sezione-indietro"),
    btnSezioneDettaglioChiudi: document.getElementById("btn-sezione-dettaglio-chiudi"),
    sezioneDettaglioClose: document.getElementById("sezione-dettaglio-close"),
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
    const baseCls = compact ? "sez-item" : "sez-card";
    const cls = [
      baseCls,
      "sez-card-clickable",
      s.ha_dati ? (s.avanzamento_pct >= 99 ? "completa" : "") : "inattiva",
    ]
      .filter(Boolean)
      .join(" ");
    const cardCls = cls;
    const leader = s.leader_nome
      ? `${escapeHtml(s.leader_nome)} (${s.leader_pct}%)`
      : s.ha_dati
        ? "—"
        : "In attesa";
    const clickAttrs = ` data-sezione-id="${escapeHtml(String(s.id))}" tabindex="0" role="button"`;
    if (compact) {
      return `<div class="${cls}"${clickAttrs}>
        <span class="sez-nome">${escapeHtml(s.nome)}</span>
        <span class="sez-pct">${s.avanzamento_pct}%</span>
        <span class="sez-meta">${s.schede_scrutinate} votate / ${s.elettori}</span>
        <span class="sez-leader">${leader}</span>
        <div class="sez-bar"><div class="sez-bar-fill" style="width:${s.avanzamento_pct}%"></div></div>
      </div>`;
    }
    return `<div class="${cardCls}"${clickAttrs}>
      <h3>${escapeHtml(s.nome)}</h3>
      <div class="sez-stats">${s.schede_scrutinate.toLocaleString("it-IT")} schede votate / ${s.elettori.toLocaleString("it-IT")} elettori · ${s.avanzamento_pct}%</div>
      <div class="sez-leader-full">${leader}</div>
      <div class="sez-hint">Clicca per il dettaglio</div>
      <div class="sez-bar"><div class="sez-bar-fill" style="width:${s.avanzamento_pct}%"></div></div>
    </div>`;
  }

  function renderSezioni(sezioni, total) {
    if (!els.sezioniPreview) return;
    const list = sezioni || [];
    sezioniCache = list;
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
    closePreferenzeOverlay();
    document.body.classList.add("display-overlay-open");
    els.sezioniOverlay?.classList.add("open");
    els.sezioniOverlay?.setAttribute("aria-hidden", "false");
    requestAnimationFrame(() => {
      els.sezioniOverlayGrid?.scrollTo(0, 0);
    });
  }

  function closeSezioniOverlay() {
    els.sezioniOverlay?.classList.remove("open");
    els.sezioniOverlay?.setAttribute("aria-hidden", "true");
    if (!els.preferenzeOverlay?.classList.contains("open")) {
      document.body.classList.remove("display-overlay-open");
    }
  }

  els.btnSezioniTutte?.addEventListener("click", openSezioniOverlay);
  els.btnOverlayChiudi?.addEventListener("click", closeSezioniOverlay);
  els.sezioniOverlayClose?.addEventListener("click", closeSezioniOverlay);

  function sezioneById(id) {
    return sezioniCache.find((s) => String(s.id) === String(id));
  }

  function sezioneCandidatoRow(c) {
    const cap = c.capolista ? ' <span class="pref-cap-tag">★</span>' : "";
    return `<tr>
      <td>${escapeHtml(c.nome)}${cap}</td>
      <td class="pref-voti">${c.voti.toLocaleString("it-IT")}</td>
      <td class="pref-pct">${c.pct}%</td>
    </tr>`;
  }

  function renderSezioneDettaglioBody(s) {
    const d = s.dettaglio || {};
    if (!s.ha_dati) {
      return '<p class="pref-empty">Nessun dato registrato per questa sezione.</p>';
    }
    const riepilogo = `<div class="sez-det-riepilogo">
      <div class="sez-det-stat"><span class="muted">Schede votate</span><strong>${s.schede_scrutinate.toLocaleString("it-IT")}</strong></div>
      <div class="sez-det-stat"><span class="muted">Elettori</span><strong>${s.elettori.toLocaleString("it-IT")}</strong></div>
      <div class="sez-det-stat"><span class="muted">Voti validi</span><strong>${(d.voti_validi || 0).toLocaleString("it-IT")}</strong></div>
      <div class="sez-det-stat"><span class="muted">Nulli</span><strong>${(d.nulli || 0).toLocaleString("it-IT")}</strong></div>
      <div class="sez-det-stat"><span class="muted">Bianche</span><strong>${(d.bianche || 0).toLocaleString("it-IT")}</strong></div>
      <div class="sez-det-stat"><span class="muted">Contestati</span><strong>${(d.contestati || 0).toLocaleString("it-IT")}</strong></div>
      <div class="sez-det-stat"><span class="muted">Spoglio</span><strong>${d.spoglio_pct || 0}%</strong></div>
      ${d.mancano > 0 ? `<div class="sez-det-stat sez-det-warn"><span class="muted">Mancano</span><strong>${d.mancano.toLocaleString("it-IT")}</strong></div>` : ""}
    </div>`;
    if (d.liste && d.liste.length) {
      const listeHtml = d.liste
        .map(
          (lista) => `<section class="pref-lista-block">
          <header class="pref-lista-head">
            <h3>${escapeHtml(lista.nome)} → ${escapeHtml(lista.capolista)} ★</h3>
            <span class="pref-lista-tot">${lista.totale.toLocaleString("it-IT")} voti (${lista.pct}%)</span>
          </header>
          <table class="pref-table-display">
            <thead><tr><th>Consigliere</th><th>Voti</th><th>%</th></tr></thead>
            <tbody>${lista.candidati.map(sezioneCandidatoRow).join("")}</tbody>
          </table>
        </section>`
        )
        .join("");
      return riepilogo + listeHtml;
    }
    if (d.candidati && d.candidati.length) {
      return (
        riepilogo +
        `<table class="pref-table-display">
          <thead><tr><th>Candidato</th><th>Voti</th><th>%</th></tr></thead>
          <tbody>${d.candidati.map(sezioneCandidatoRow).join("")}</tbody>
        </table>`
      );
    }
    return riepilogo;
  }

  function openSezioneDettaglio(id) {
    const s = sezioneById(id);
    if (!s || !els.sezioneDettaglioOverlay) return;
    if (els.sezioneDettaglioTitle) {
      els.sezioneDettaglioTitle.textContent = s.nome;
    }
    if (els.sezioneDettaglioBody) {
      els.sezioneDettaglioBody.innerHTML = renderSezioneDettaglioBody(s);
    }
    document.body.classList.add("display-overlay-open");
    els.sezioneDettaglioOverlay.classList.add("open");
    els.sezioneDettaglioOverlay.setAttribute("aria-hidden", "false");
    requestAnimationFrame(() => {
      els.sezioneDettaglioBody?.scrollTo(0, 0);
    });
  }

  function closeSezioneDettaglio() {
    els.sezioneDettaglioOverlay?.classList.remove("open");
    els.sezioneDettaglioOverlay?.setAttribute("aria-hidden", "true");
    if (
      !els.sezioniOverlay?.classList.contains("open") &&
      !els.preferenzeOverlay?.classList.contains("open")
    ) {
      document.body.classList.remove("display-overlay-open");
    }
  }

  function onSezioneClick(ev) {
    const card = ev.target.closest("[data-sezione-id]");
    if (!card) return;
    openSezioneDettaglio(card.dataset.sezioneId);
  }

  function onSezioneKey(ev) {
    if (ev.key !== "Enter" && ev.key !== " ") return;
    const card = ev.target.closest("[data-sezione-id]");
    if (!card) return;
    ev.preventDefault();
    openSezioneDettaglio(card.dataset.sezioneId);
  }

  els.sezioniPreview?.addEventListener("click", onSezioneClick);
  els.sezioniPreview?.addEventListener("keydown", onSezioneKey);
  els.sezioniOverlayGrid?.addEventListener("click", onSezioneClick);
  els.sezioniOverlayGrid?.addEventListener("keydown", onSezioneKey);
  els.btnSezioneIndietro?.addEventListener("click", closeSezioneDettaglio);
  els.btnSezioneDettaglioChiudi?.addEventListener("click", () => {
    closeSezioneDettaglio();
    closeSezioniOverlay();
  });
  els.sezioneDettaglioClose?.addEventListener("click", closeSezioneDettaglio);

  function formatPrefPct(pct) {
    const n = Number(pct);
    const v = Number.isFinite(n) ? n : 0;
    return (
      v.toLocaleString("it-IT", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }) + "%"
    );
  }

  function preferenzeRowHtml(c, listaColor) {
    const capBadge = c.capolista
      ? '<span class="pref-badge pref-badge-cap">Capolista ★</span>'
      : "";
    const rowCls = [
      "pref-row",
      c.capolista ? "pref-row-cap" : "",
      !c.capolista && !c.voti_reali && !c.voti_proiettati ? "pref-row-empty" : "",
    ]
      .filter(Boolean)
      .join(" ");
    const pct = Number(c.pct_proiettate) || 0;
    return `<tr class="${rowCls}">
      <td class="pref-col-nome">
        <span class="pref-nome">${escapeHtml(c.nome)}</span>${capBadge}
      </td>
      <td class="pref-col-num">${c.voti_reali.toLocaleString("it-IT")}</td>
      <td class="pref-col-num pref-col-proj">${c.voti_proiettati.toLocaleString("it-IT")}</td>
      <td class="pref-col-pct">
        <div class="pref-pct-wrap">
          <span class="pref-pct-val">${formatPrefPct(pct)}</span>
          <div class="pref-pct-bar" aria-hidden="true">
            <div class="pref-pct-fill" style="width:${Math.min(100, pct)}%;background:${listaColor}"></div>
          </div>
        </div>
      </td>
    </tr>`;
  }

  function renderPreferenze(preferenze) {
    if (!els.preferenzeOverlayBody) return;
    const liste = preferenze || [];
    if (!liste.length) {
      els.preferenzeOverlayBody.innerHTML =
        '<p class="pref-empty">Nessuna preferenza registrata.</p>';
      return;
    }
    const cards = liste
      .map((lista, idx) => {
        const color = lista.color || "#60a5fa";
        const totR = (lista.totale_reale ?? 0).toLocaleString("it-IT");
        const totP = (lista.totale_proiettato ?? 0).toLocaleString("it-IT");
        return `<section class="pref-lista-card" style="--lista-color:${color}">
        <header class="pref-lista-head">
          <div class="pref-lista-title">
            <span class="pref-lista-badge">Lista ${idx + 1}</span>
            <h3>${escapeHtml(lista.capolista_nome || lista.nome)}</h3>
            ${lista.capolista_nome ? `<span class="pref-lista-sub">${escapeHtml(lista.nome)}</span>` : ""}
          </div>
          <div class="pref-lista-chips">
            <span class="pref-chip">
              <span class="pref-chip-label">Voti reali</span>
              <strong>${totR}</strong>
            </span>
            <span class="pref-chip pref-chip-proj">
              <span class="pref-chip-label">Proj.</span>
              <strong>${totP}</strong>
            </span>
          </div>
        </header>
        <div class="pref-table-wrap">
          <table class="pref-table-display">
            <thead>
              <tr>
                <th class="pref-col-nome">Candidato</th>
                <th class="pref-col-num">Voti reali</th>
                <th class="pref-col-num">Proj.</th>
                <th class="pref-col-pct">% proj.</th>
              </tr>
            </thead>
            <tbody>
              ${lista.candidati.map((c) => preferenzeRowHtml(c, color)).join("")}
            </tbody>
          </table>
        </div>
      </section>`;
      })
      .join("");
    els.preferenzeOverlayBody.innerHTML = `<div class="pref-modal-grid">${cards}</div>`;
  }

  function openPreferenzeOverlay() {
    closeSezioniOverlay();
    document.body.classList.add("display-overlay-open");
    els.preferenzeOverlay?.classList.add("open");
    els.preferenzeOverlay?.setAttribute("aria-hidden", "false");
    requestAnimationFrame(() => {
      els.preferenzeOverlayBody?.scrollTo(0, 0);
    });
  }

  function closePreferenzeOverlay() {
    els.preferenzeOverlay?.classList.remove("open");
    els.preferenzeOverlay?.setAttribute("aria-hidden", "true");
    if (!els.sezioniOverlay?.classList.contains("open")) {
      document.body.classList.remove("display-overlay-open");
    }
  }

  els.btnPreferenze?.addEventListener("click", openPreferenzeOverlay);
  els.btnPreferenzeChiudi?.addEventListener("click", closePreferenzeOverlay);
  els.preferenzeOverlayClose?.addEventListener("click", closePreferenzeOverlay);

  function renderSindacoConfronto(sorted, isListe) {
    const box = els.sindacoConfronto;
    if (!box) return;
    if (!isListe || sorted.length < 2) {
      box.classList.add("hidden");
      box.innerHTML = "";
      return;
    }
    const a = sorted[0];
    const b = sorted[1];
    const diffR = a.voti_reali - b.voti_reali;
    const diffP = a.voti_proiettati - b.voti_proiettati;
    const nomeA = a.nome_display || a.nome;
    box.classList.remove("hidden");
    box.innerHTML = `
      <div class="sindaco-confronto-inner">
        <span class="sindaco-confronto-label">Vantaggio ${escapeHtml(nomeA)}</span>
        <span class="sindaco-confronto-diff">
          <strong>+${diffR.toLocaleString("it-IT")}</strong> voti reali
          · <strong>+${diffP.toLocaleString("it-IT")}</strong> proj.
        </span>
      </div>`;
  }

  function renderCandidati(candidati, isListe) {
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
        const suValidi =
          isListe && c.pct_su_validi_proiettati != null
            ? `<div class="cand-su-validi">${c.pct_su_validi_proiettati}% su voti validi</div>`
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
            ${suValidi}
          </div>
          <div class="cand-voti">
            <div class="cand-voti-reali"><strong>${c.voti_reali.toLocaleString("it-IT")}</strong> <span>reali</span></div>
            <div class="cand-voti-proj"><strong>${c.voti_proiettati.toLocaleString("it-IT")}</strong> <span>proj.</span></div>
          </div>
        </div>`;
      })
      .join("");
    renderSindacoConfronto(sorted, isListe);
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
    const sv = data.schede_votate || {};
    const arrivate = sv.arrivate ?? p.schede_scrutinate ?? 0;
    const stimaFinale = sv.stima_finale ?? arrivate;
    const elettori = sv.elettori ?? p.schede_totali ?? 0;
    if (els.schedeVotateArr) {
      els.schedeVotateArr.textContent = arrivate.toLocaleString("it-IT");
    }
    if (els.schedeTot) {
      els.schedeTot.textContent = elettori.toLocaleString("it-IT");
    }
    if (els.schedeFinaleWrap && els.schedeVotateFinale) {
      const showStima = !sv.completo && stimaFinale > arrivate;
      const showDefinitivo = sv.completo && arrivate > 0;
      const show = showStima || showDefinitivo;
      els.schedeFinaleWrap.classList.toggle("hidden", !show);
      if (els.schedeFinalePrefix) {
        els.schedeFinalePrefix.textContent = showDefinitivo
          ? "Totale definitivo"
          : "Stima finale";
      }
      els.schedeVotateFinale.textContent = (showDefinitivo
        ? arrivate
        : stimaFinale
      ).toLocaleString("it-IT");
    }
    if (els.sezioniArrivoLabel) {
      const con = sv.sezioni_con_arrivo ?? 0;
      const tot = sv.sezioni_totali ?? data.sezioni_totali ?? 0;
      els.sezioniArrivoLabel.textContent = con + "/" + tot + " sezioni";
    }
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

    renderCandidati(p.candidati || [], data.tipo === "liste");
    if (els.alertSindaco) {
      const msg = data.alert_sindaco || "";
      els.alertSindaco.textContent = msg;
      els.alertSindaco.classList.toggle("hidden", !msg);
    }
    renderPreferenze(data.preferenze || []);
    if (els.btnPreferenze) {
      els.btnPreferenze.hidden = !(data.preferenze && data.preferenze.length);
    }
    if (els.candidatiTitle) {
      els.candidatiTitle.textContent =
        data.tipo === "liste" ? "Sindaci" : "Candidati";
    }
    renderSezioni(data.sezioni, data.sezioni_totali);
    tipoCache = data.tipo || "";
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
    if (e.key === "Escape") {
      if (els.sezioneDettaglioOverlay?.classList.contains("open")) {
        closeSezioneDettaglio();
        return;
      }
      closeSezioniOverlay();
      closePreferenzeOverlay();
    }
    if (e.key === "f" || e.key === "F") {
      if (!document.fullscreenElement)
        document.documentElement.requestFullscreen?.();
      else document.exitFullscreen?.();
    }
    if (e.key === "s" || e.key === "S") {
      if (els.sezioniOverlay?.classList.contains("open")) closeSezioniOverlay();
      else openSezioniOverlay();
    }
    if (e.key === "p" || e.key === "P") {
      if (els.preferenzeOverlay?.classList.contains("open")) closePreferenzeOverlay();
      else if (els.btnPreferenze && !els.btnPreferenze.hidden) openPreferenzeOverlay();
    }
  });
})();
