const storage = {
  get(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch {
      return fallback;
    }
  },
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // ignore
    }
  },
};

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  storage.set("vsai:theme", theme);
}

function updateFavoritesPill() {
  const pill = document.getElementById("favoritesCount");
  if (!pill) return;
  const favs = storage.get("vsai:favorites", []);
  pill.textContent = `Favorites: ${Array.isArray(favs) ? favs.length : 0}`;
}

document.addEventListener("DOMContentLoaded", () => {
  const saved = storage.get("vsai:theme", "light");
  applyTheme(saved);

  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "light";
      applyTheme(current === "light" ? "dark" : "light");
    });
  }

  updateFavoritesPill();

  // Minimal favorites rendering on Explore page (if present).
  const favoritesGrid = document.getElementById("favoritesGrid");
  if (favoritesGrid) {
    const favs = storage.get("vsai:favorites", []);
    favoritesGrid.innerHTML = "";
    if (!Array.isArray(favs) || favs.length === 0) {
      favoritesGrid.innerHTML =
        '<div class="sub">No favorites yet. Generate outfits in Stylist and tap the heart.</div>';
      return;
    }
    for (const o of favs) {
      const card = document.createElement("div");
      card.className = "outfit-card";
      card.innerHTML = `
        <div class="outfit-top">
          <div class="outfit-title">${o.label || "Saved outfit"}</div>
          <button class="icon-btn" type="button" data-action="remove" aria-label="Remove favorite" data-outfit-id="${o.id}">
            <span aria-hidden="true">✕</span>
          </button>
        </div>
        <div class="outfit-meta">
          <span class="pill">Score ${(o.score ?? 0).toFixed(2)}</span>
          <span class="pill">ML ${(o.ml_score ?? 0).toFixed(2)}</span>
          <span class="pill">Harmony ${(o.harmony_score ?? 0).toFixed(2)}</span>
        </div>
        <div class="outfit-split">
          <div class="tile"><div class="swatch" style="background: var(--c-${(o.colors?.top || "gray").toLowerCase()});"></div><div class="tile-k">Top</div><div class="tile-v">${o.colors?.top || ""} ${o.items?.top || ""}</div></div>
          <div class="tile"><div class="swatch" style="background: var(--c-${(o.colors?.bottom || "gray").toLowerCase()});"></div><div class="tile-k">Bottom</div><div class="tile-v">${o.colors?.bottom || ""} ${o.items?.bottom || ""}</div></div>
          <div class="tile"><div class="swatch" style="background: var(--c-${(o.colors?.shoes || "gray").toLowerCase()});"></div><div class="tile-k">Shoes</div><div class="tile-v">${o.colors?.shoes || ""} ${o.items?.shoes || ""}</div></div>
        </div>
      `;
      favoritesGrid.appendChild(card);
    }

    favoritesGrid.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-action='remove']");
      if (!btn) return;
      const id = btn.getAttribute("data-outfit-id");
      let favs = storage.get("vsai:favorites", []);
      favs = Array.isArray(favs) ? favs.filter((x) => x && x.id !== id) : [];
      storage.set("vsai:favorites", favs);
      updateFavoritesPill();
      location.reload();
    });
  }
});

window.VSAI = { storage, updateFavoritesPill };

