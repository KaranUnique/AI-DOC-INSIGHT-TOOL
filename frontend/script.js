const API_BASE = "http://localhost:8000";

const tabUpload = document.getElementById("tab-upload");
const tabHistory = document.getElementById("tab-history");
const uploadSection = document.getElementById("upload-section");
const historySection = document.getElementById("history-section");
const form = document.getElementById("upload-form");
const fileInput = document.getElementById("pdf-file");
const resultDiv = document.getElementById("result");
const historyList = document.getElementById("history-list");

tabUpload.addEventListener("click", () => {
  tabUpload.classList.add("active");
  tabHistory.classList.remove("active");
  uploadSection.style.display = "";
  historySection.style.display = "none";
});

tabHistory.addEventListener("click", () => {
  tabHistory.classList.add("active");
  tabUpload.classList.remove("active");
  uploadSection.style.display = "none";
  historySection.style.display = "";
  loadHistory();
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) return;

  const fd = new FormData();
  fd.append("file", file);

  resultDiv.style.display = "block";
  resultDiv.innerHTML = "<p>Uploading and processing...</p>";

  try {
    const resp = await fetch(`${API_BASE}/upload-resume`, {
      method: "POST",
      body: fd
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Upload failed");
    }
    const data = await resp.json();
    showInsight(data);
  } catch (err) {
    resultDiv.innerHTML = `<p style="color:#f87171">Error: ${err.message}</p>`;
  }
});

function showInsight(item) {
  const topWords = (item.top_words || [])
    .map(([w, c]) => `${w} (${c})`)
    .join(", ");
  resultDiv.innerHTML = `
    <h3>${item.filename}</h3>
    <p class="small">Uploaded: ${new Date(item.uploaded_at).toLocaleString()}</p>
    <p><b>Type:</b> ${item.summary_type.toUpperCase()}</p>
    <div class="card"><b>Summary</b><div class="code">${escapeHtml(item.summary)}</div></div>
    <p><b>Top words:</b> ${topWords || "—"}</p>
    <details>
      <summary>Text excerpt</summary>
      <div class="code">${escapeHtml(item.text_excerpt || "")}</div>
    </details>
  `;
}

async function loadHistory() {
  historyList.innerHTML = "<p>Loading...</p>";
  try {
    const resp = await fetch(`${API_BASE}/insights`);
    const data = await resp.json();
    const items = data.items || [];
    if (!items.length) {
      historyList.innerHTML = "<p>No history yet.</p>";
      return;
    }
    historyList.innerHTML = items.map(renderItem).join("");
    document.querySelectorAll(".view-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const id = e.currentTarget.dataset.id;
        const res = await fetch(`${API_BASE}/insights?id=${encodeURIComponent(id)}`);
        const item = await res.json();
        tabUpload.click();
        showInsight(item);
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    });
  } catch (e) {
    historyList.innerHTML = `<p style="color:#f87171">Failed to load history: ${e.message}</p>`;
  }
}

function renderItem(item) {
  return `
    <div class="item">
      <div><b>${item.filename}</b></div>
      <div class="small">${new Date(item.uploaded_at).toLocaleString()} • ${item.summary_type.toUpperCase()}</div>
      <button class="view-btn" data-id="${item.id}">View</button>
    </div>
  `;
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, s => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[s]);
}
