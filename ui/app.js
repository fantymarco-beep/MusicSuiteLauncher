const ICONS = {
  compass: `
    <svg viewBox="0 0 48 48" width="34" height="34" fill="none">
      <circle cx="24" cy="24" r="19" fill="#EFF6FF" stroke="#2563EB" stroke-width="2.5"/>
      <polygon points="29,19 21,21 19,29 27,27" fill="#3B82F6"/>
      <polygon points="29,19 27,27 24,24" fill="#EF4444"/>
      <circle cx="24" cy="24" r="2.2" fill="#1E293B"/>
    </svg>`,
  waveform: `
    <svg viewBox="0 0 48 48" width="34" height="34" fill="none">
      <rect x="5" y="7" width="38" height="34" rx="8" fill="#ECFDF5" stroke="#059669" stroke-width="2.5"/>
      <line x1="13" y1="20" x2="13" y2="28" stroke="#10B981" stroke-width="3" stroke-linecap="round"/>
      <line x1="19" y1="14" x2="19" y2="34" stroke="#059669" stroke-width="3" stroke-linecap="round"/>
      <line x1="25" y1="17" x2="25" y2="31" stroke="#34D399" stroke-width="3" stroke-linecap="round"/>
      <line x1="31" y1="12" x2="31" y2="36" stroke="#047857" stroke-width="3" stroke-linecap="round"/>
      <line x1="37" y1="21" x2="37" y2="27" stroke="#10B981" stroke-width="3" stroke-linecap="round"/>
    </svg>`,
  playlist: `
    <svg viewBox="0 0 48 48" width="34" height="34" fill="none">
      <rect x="6" y="8" width="36" height="32" rx="7" fill="#FFF7ED" stroke="#EA580C" stroke-width="2.5"/>
      <line x1="13" y1="17" x2="27" y2="17" stroke="#EA580C" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="13" y1="24" x2="25" y2="24" stroke="#F97316" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="13" y1="31" x2="22" y2="31" stroke="#FB923C" stroke-width="2.5" stroke-linecap="round"/>
      <circle cx="32" cy="29" r="4" fill="#EA580C"/>
      <path d="M36 29V17l4 2" stroke="#EA580C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
  speaker: `
    <svg viewBox="0 0 48 48" width="34" height="34" fill="none">
      <rect x="10" y="6" width="28" height="36" rx="5" fill="#F5F3FF" stroke="#7C3AED" stroke-width="2.5"/>
      <circle cx="24" cy="14" r="3" fill="#8B5CF6"/>
      <circle cx="24" cy="28" r="8" fill="#DDD6FE" stroke="#6D28D9" stroke-width="2.5"/>
      <circle cx="24" cy="28" r="3" fill="#5B21B6"/>
    </svg>`,
  usb: `
    <svg viewBox="0 0 48 48" width="34" height="34" fill="none">
      <rect x="14" y="16" width="20" height="24" rx="5" fill="#ECFEFF" stroke="#0891B2" stroke-width="2.5"/>
      <rect x="18" y="8" width="12" height="8" rx="1.5" fill="#CFFAFE" stroke="#0891B2" stroke-width="2.5"/>
      <circle cx="24" cy="28" r="4.5" fill="#06B6D4"/>
    </svg>`,
  vinyl: `
    <svg viewBox="0 0 48 48" width="34" height="34" fill="none">
      <circle cx="24" cy="24" r="18" fill="#18181B" stroke="#E11D48" stroke-width="2.5"/>
      <circle cx="24" cy="24" r="12" stroke="#3F3F46" stroke-width="1.5"/>
      <circle cx="24" cy="24" r="6" fill="#F43F5E"/>
      <circle cx="24" cy="24" r="2" fill="#FFFFFF"/>
    </svg>`,
  books: `
    <svg viewBox="0 0 48 48" width="34" height="34" fill="none">
      <rect x="8" y="9" width="9" height="30" rx="2" fill="#FEF3C7" stroke="#D97706" stroke-width="2.2"/>
      <rect x="19" y="7" width="10" height="32" rx="2" fill="#DBEAFE" stroke="#2563EB" stroke-width="2.2"/>
      <rect x="31" y="11" width="9" height="28" rx="2" fill="#FCE7F3" stroke="#DB2777" stroke-width="2.2"/>
    </svg>`,
  database: `
    <svg viewBox="0 0 48 48" width="34" height="34" fill="none">
      <ellipse cx="24" cy="13" rx="14" ry="5.5" fill="#E0F2FE" stroke="#0284C7" stroke-width="2.5"/>
      <path d="M10 13v11c0 3 6.3 5.5 14 5.5s14-2.5 14-5.5V13" fill="#F0F9FF" stroke="#0284C7" stroke-width="2.5"/>
      <path d="M10 24v11c0 3 6.3 5.5 14 5.5s14-2.5 14-5.5V24" stroke="#0284C7" stroke-width="2.5"/>
    </svg>`,
  archive: `
    <svg viewBox="0 0 48 48" width="34" height="34" fill="none">
      <rect x="7" y="9" width="34" height="8" rx="2.5" fill="#FEF9C3" stroke="#CA8A04" stroke-width="2.5"/>
      <path d="M10 17h28v21a3 3 0 0 1-3 3H13a3 3 0 0 1-3-3V17z" fill="#FEFCE8" stroke="#CA8A04" stroke-width="2.5"/>
      <line x1="19" y1="25" x2="29" y2="25" stroke="#A16207" stroke-width="2.5" stroke-linecap="round"/>
    </svg>`
};

let allApps = [];
let currentFilter = "ALL";
let currentSort = "name";
let searchQuery = "";

const gridEl = document.getElementById("apps-grid");
const emptyEl = document.getElementById("empty-state");
const activeSummaryEl = document.getElementById("active-summary");
const statusTextEl = document.getElementById("status-text");
const modalBackdrop = document.getElementById("modal-backdrop");
const modalTitle = document.getElementById("modal-title");
const modalFilepath = document.getElementById("modal-filepath");
const modalBody = document.getElementById("modal-body");

function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.remove("hidden");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.add("hidden"), 2800);
}

async function fetchApps() {
  try {
    const res = await fetch("/api/apps");
    if (!res.ok) throw new Error("Errore caricamento app");
    allApps = await res.json();
    render();
  } catch (err) {
    statusTextEl.textContent = "ERRORE DI CONNESSIONE AL BACKEND LOCALE";
  }
}

function getFilteredApps() {
  const q = searchQuery.trim().toLowerCase();
  let items = allApps.filter((item) => {
    if (currentFilter === "ACTIVE" && !item.active) return false;
    if (currentFilter !== "ALL" && currentFilter !== "ACTIVE" && item.category !== currentFilter) {
      return false;
    }
    if (q) {
      const hay = `${item.name} ${item.description} ${item.category} ${item.tag}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  items.sort((a, b) => {
    if (currentSort === "active") {
      if (a.active !== b.active) return a.active ? -1 : 1;
    } else if (currentSort === "category") {
      const cmp = a.category.localeCompare(b.category);
      if (cmp !== 0) return cmp;
    }
    return a.name.localeCompare(b.name, "it");
  });

  return items;
}

function render() {
  const activeCount = allApps.filter((a) => a.active).length;
  activeSummaryEl.textContent = `${activeCount} ${activeCount === 1 ? "attivo" : "attivi"} · ${allApps.length} totali`;

  const items = getFilteredApps();
  emptyEl.classList.toggle("hidden", items.length > 0);
  gridEl.innerHTML = "";

  for (const item of items) {
    const card = document.createElement("article");
    card.className = `card${item.active ? " is-active" : ""}`;

    const githubHtml = item.github_url
      ? `<a class="github-link" href="${item.github_url}" target="_blank" rel="noopener">GITHUB ↗</a>`
      : `<span>LOCALE</span>`;

    const statusBadge = item.active
      ? `<div class="status-badge active"><span class="status-dot"></span>IN ESECUZIONE</div>`
      : `<div class="status-badge"><span class="status-dot"></span>PRONTO</div>`;

    const launchLabel = item.active ? "ATTIVO · RILANCIA" : item.action_label;

    card.innerHTML = `
      <div class="card-meta">
        <span>${item.category}</span>
        ${githubHtml}
      </div>
      <div class="card-header">
        <div class="app-icon-box">${ICONS[item.icon] || ICONS.archive}</div>
        <div class="app-title-wrap">
          <h3 class="app-name">
            <span>${item.name}</span>
            <span class="tag-chip">${item.tag}</span>
          </h3>
        </div>
      </div>
      ${statusBadge}
      <p class="card-desc">${item.description}</p>
      <div class="card-actions">
        <button class="btn-launch" data-action="launch" data-id="${item.id}">${launchLabel}</button>
        <button class="icon-btn" data-action="instructions" data-id="${item.id}" title="Apri istruzioni">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
        </button>
        <button class="icon-btn" data-action="folder" data-id="${item.id}" title="Apri cartella su E:\\">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
        </button>
      </div>
    `;

    gridEl.appendChild(card);
  }
}

gridEl.addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;
  const action = btn.dataset.action;
  const id = btn.dataset.id;

  if (action === "launch") {
    const res = await fetch(`/api/launch/${id}`, { method: "POST" });
    if (res.ok) {
      showToast("Avvio in corso...");
      setTimeout(fetchApps, 700);
    } else {
      const err = await res.json().catch(() => ({}));
      showToast(err.detail || "Errore durante l'avvio");
    }
  } else if (action === "folder") {
    const res = await fetch(`/api/open-folder/${id}`, { method: "POST" });
    if (!res.ok) showToast("Impossibile aprire la cartella");
  } else if (action === "instructions") {
    const res = await fetch(`/api/instructions/${id}`);
    if (res.ok) {
      const data = await res.json();
      modalTitle.textContent = data.title;
      modalFilepath.textContent = data.file || "";
      modalBody.innerHTML = data.html;
      modalBackdrop.classList.remove("hidden");
    } else {
      showToast("Impossibile caricare le istruzioni");
    }
  }
});

document.getElementById("filter-tabs").addEventListener("click", (e) => {
  const tab = e.target.closest(".tab[data-filter]");
  if (!tab) return;
  document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
  tab.classList.add("active");
  currentFilter = tab.dataset.filter;
  render();
});

document.getElementById("sort-select").addEventListener("change", (e) => {
  currentSort = e.target.value;
  render();
});

document.getElementById("search-input").addEventListener("input", (e) => {
  searchQuery = e.target.value;
  render();
});

document.getElementById("refresh-btn").addEventListener("click", () => {
  fetchApps();
  showToast("Stato aggiornato");
});

document.getElementById("modal-close").addEventListener("click", () => {
  modalBackdrop.classList.add("hidden");
});

modalBackdrop.addEventListener("click", (e) => {
  if (e.target === modalBackdrop) modalBackdrop.classList.add("hidden");
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    modalBackdrop.classList.add("hidden");
    addModalBackdrop.classList.add("hidden");
  }
});

const addModalBackdrop = document.getElementById("add-modal-backdrop");
const addAppForm = document.getElementById("add-app-form");

document.getElementById("add-app-btn").addEventListener("click", () => {
  addAppForm.reset();
  addModalBackdrop.classList.remove("hidden");
});

document.getElementById("add-modal-close").addEventListener("click", () => {
  addModalBackdrop.classList.add("hidden");
});

document.getElementById("add-cancel-btn").addEventListener("click", () => {
  addModalBackdrop.classList.add("hidden");
});

addModalBackdrop.addEventListener("click", (e) => {
  if (e.target === addModalBackdrop) addModalBackdrop.classList.add("hidden");
});

addAppForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(addAppForm);
  const payload = Object.fromEntries(fd.entries());
  const res = await fetch("/api/apps", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (res.ok) {
    addModalBackdrop.classList.add("hidden");
    showToast("Collegamento aggiunto al launcher");
    await fetchApps();
  } else {
    const err = await res.json().catch(() => ({}));
    showToast(err.detail || "Errore durante il salvataggio");
  }
});

fetchApps();
setInterval(fetchApps, 3000);
