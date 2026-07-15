const API_BASE = "http://localhost:5000/api";

const ledger = document.getElementById("ledger");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const statusLine = document.getElementById("status-line");

// Simple guest user id kept in memory for this session (no localStorage per artifact rules)
let currentUserId = null;

async function ensureUser() {
  try {
    const res = await fetch(`${API_BASE}/users`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: "guest" }),
    });
    const user = await res.json();
    currentUserId = user.id;
  } catch (err) {
    console.warn("Could not initialize user (backend/MySQL may be offline):", err);
  }
}

function addEntry({ role, text, cls = "" }) {
  const entry = document.createElement("div");
  entry.className = `entry ${role} ${cls}`.trim();

  const label = document.createElement("div");
  label.className = "entry-label";
  label.textContent = role === "user" ? "YOU" : "LIBRARIAN";

  const body = document.createElement("div");
  body.className = "entry-body";
  body.innerHTML = text;

  entry.appendChild(label);
  entry.appendChild(body);
  ledger.appendChild(entry);
  ledger.scrollTop = ledger.scrollHeight;
  return entry;
}

function renderRecommendations(intro, recommendations) {
  const entry = addEntry({ role: "bot", text: intro });
  const stack = document.createElement("div");
  stack.className = "card-stack";

  recommendations.forEach((book, i) => {
    const card = document.createElement("div");
    card.className = "book-card";
    card.innerHTML = `
      <span class="call-number">No. ${String(i + 1).padStart(2, "0")}</span>
      <p class="title">${escapeHtml(book.title)}</p>
      <p class="meta">${escapeHtml(book.authors || "Unknown author")} · ${escapeHtml(book.categories || "Uncategorized")}${
        book.average_rating ? ` · ★ ${Number(book.average_rating).toFixed(1)}` : ""
      }</p>
    `;
    stack.appendChild(card);
  });

  entry.appendChild(stack);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addEntry({ role: "user", text: escapeHtml(message) });
  input.value = "";
  sendBtn.disabled = true;
  statusLine.textContent = "Searching the stacks...";

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, userId: currentUserId }),
    });

    const data = await res.json();

    if (!res.ok) {
      addEntry({ role: "bot", cls: "error", text: data.error || "I couldn't find anything for that." });
    } else {
      renderRecommendations(data.intro, data.recommendations);
    }
  } catch (err) {
    console.error(err);
    addEntry({
      role: "bot",
      cls: "error",
      text: "Couldn't reach the backend. Make sure the Express server (port 5000) and Flask ML service (port 5001) are running.",
    });
  } finally {
    sendBtn.disabled = false;
    statusLine.textContent = "";
  }
});

ensureUser();
