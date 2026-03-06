const api = {
  async getPresets() {
    const res = await fetch("/api/presets");
    if (!res.ok) throw new Error("Failed to load presets");
    return res.json();
  },
  async recommend(payload) {
    const res = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to generate recommendations");
    return res.json();
  },
};

function $(id) {
  return document.getElementById(id);
}

function clampColors(selected) {
  const unique = Array.from(new Set(selected));
  return unique.slice(0, 3);
}

function getSelectedColors() {
  const chips = document.querySelectorAll(".color-chip[data-selected='true']");
  return clampColors(Array.from(chips).map((c) => c.getAttribute("data-color")));
}

function setChipSelected(btn, selected) {
  btn.setAttribute("data-selected", selected ? "true" : "false");
}

function renderPresets(presets) {
  const row = $("presetRow");
  if (!row) return;
  row.innerHTML = "";
  for (const p of presets) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "preset";
    btn.setAttribute("data-preset", p.id);
    btn.setAttribute("data-selected", "false");
    btn.innerHTML = `<div class="k">${p.label}</div><div class="v">${p.vibe}</div>`;
    row.appendChild(btn);
  }
}

function getSelectedPreset() {
  const btn = document.querySelector(".preset[data-selected='true']");
  return btn ? btn.getAttribute("data-preset") : null;
}

function wirePresetClicks() {
  const row = $("presetRow");
  if (!row) return;
  row.addEventListener("click", (e) => {
    const btn = e.target.closest(".preset");
    if (!btn) return;
    const all = row.querySelectorAll(".preset");
    for (const b of all) b.setAttribute("data-selected", "false");
    btn.setAttribute("data-selected", "true");
  });
}

function wireColorClicks() {
  const row = $("colorRow");
  if (!row) return;
  row.addEventListener("click", (e) => {
    const btn = e.target.closest(".color-chip");
    if (!btn) return;
    const currently = btn.getAttribute("data-selected") === "true";
    if (currently) {
      setChipSelected(btn, false);
      return;
    }

    const selected = getSelectedColors();
    if (selected.length >= 3) {
      // remove the oldest selected to keep UX snappy
      const first = document.querySelector(".color-chip[data-selected='true']");
      if (first) setChipSelected(first, false);
    }
    setChipSelected(btn, true);
  });
}

function outfitCardHTML(o) {
  const cTop = (o.colors?.top || "Gray").toLowerCase();
  const cBottom = (o.colors?.bottom || "Gray").toLowerCase();
  const cShoes = (o.colors?.shoes || "Gray").toLowerCase();
  return `
    <article class="outfit-card" data-outfit-id="${o.id}">
      <div class="outfit-top">
        <div class="outfit-title">${o.label}</div>
        <div class="card-actions">
          <button class="icon-btn" type="button" data-action="favorite" aria-label="Save outfit">
            <span aria-hidden="true">♥</span>
          </button>
          <button class="icon-btn" type="button" data-action="regen" aria-label="Regenerate outfits">
            <span aria-hidden="true">↻</span>
          </button>
        </div>
      </div>
      <div class="outfit-meta">
        <span class="pill">Score ${(o.score ?? 0).toFixed(2)}</span>
        <span class="pill">ML ${(o.ml_score ?? 0).toFixed(2)}</span>
        <span class="pill">Harmony ${(o.harmony_score ?? 0).toFixed(2)}</span>
      </div>
      <div class="outfit-meta" style="margin-top: 8px;">
        <span class="pill">Colors ${o.colors.top} / ${o.colors.bottom} / ${o.colors.shoes}</span>
      </div>
      <div class="outfit-split">
        <div class="tile">
          <div class="swatch" style="background: var(--c-${cTop});"></div>
          <div class="tile-k">Top</div>
          <div class="tile-v">${o.colors.top} ${o.items.top}</div>
        </div>
        <div class="tile">
          <div class="swatch" style="background: var(--c-${cBottom});"></div>
          <div class="tile-k">Bottom</div>
          <div class="tile-v">${o.colors.bottom} ${o.items.bottom}</div>
        </div>
        <div class="tile">
          <div class="swatch" style="background: var(--c-${cShoes});"></div>
          <div class="tile-k">Shoes</div>
          <div class="tile-v">${o.colors.shoes} ${o.items.shoes}</div>
        </div>
      </div>
    </article>
  `;
}

function saveFavorite(outfit) {
  const favs = window.VSAI.storage.get("vsai:favorites", []);
  const list = Array.isArray(favs) ? favs : [];
  if (list.some((x) => x && x.id === outfit.id)) return;
  list.unshift(outfit);
  window.VSAI.storage.set("vsai:favorites", list.slice(0, 60));
  window.VSAI.updateFavoritesPill();
}

function wireFavorites(grid, outfits) {
  grid.addEventListener("click", (e) => {
    const favBtn = e.target.closest("button[data-action='favorite']");
    if (favBtn) {
      const card = e.target.closest(".outfit-card");
      if (!card) return;
      const id = card.getAttribute("data-outfit-id");
      const outfit = outfits.find((x) => x.id === id);
      if (!outfit) return;
      favBtn.setAttribute("data-favorited", "true");
      saveFavorite(outfit);
      return;
    }

    const regenBtn = e.target.closest("button[data-action='regen']");
    if (regenBtn) {
      generate();
    }
  });
}

function getPayload() {
  return {
    top: $("topSelect")?.value || "Any",
    bottom: $("bottomSelect")?.value || "Any",
    shoes: $("shoesSelect")?.value || "Any",
    colors: getSelectedColors(),
    preset: getSelectedPreset(),
    style: $("styleSelect")?.value || "",
    season: $("seasonSelect")?.value || "",
    seed: Date.now(),
    limit: parseInt($("limitSelect")?.value || "8", 10),
  };
}

async function generate() {
  const loading = $("loading");
  const errorBox = $("errorBox");
  const grid = $("outfitGrid");
  if (!grid) return;

  errorBox.classList.add("hidden");
  window.VSAIAnimations?.show(loading);
  grid.innerHTML = "";

  try {
    const payload = getPayload();
    const data = await api.recommend(payload);
    const outfits = data.outfits || [];
    grid.innerHTML = outfits.map(outfitCardHTML).join("");
    wireFavorites(grid, outfits);
  } catch (err) {
    errorBox.textContent = err?.message || "Something went wrong.";
    errorBox.classList.remove("hidden");
  } finally {
    window.VSAIAnimations?.hide(loading);
  }
}

async function init() {
  wirePresetClicks();
  wireColorClicks();

  try {
    const presets = await api.getPresets();
    renderPresets(presets);
  } catch {
    // ignore
  }

  $("generateBtn")?.addEventListener("click", generate);
  $("shuffleBtn")?.addEventListener("click", generate);
}

document.addEventListener("DOMContentLoaded", init);

