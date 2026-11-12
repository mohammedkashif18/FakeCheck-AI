const input = document.getElementById("scan-input");
const scanBtn = document.getElementById("scan-btn");
const errorBox = document.getElementById("error");
const resultBox = document.getElementById("result");
const tabs = [...document.querySelectorAll(".tab")];
let mode = "message";
const samples = {
  message: "Congratulations! You are selected for a work from home internship. Earn ₹50,000 per month. Pay a registration fee of ₹999 today only to confirm your seat. Contact us on WhatsApp.",
  url: "http://secure-login-verify-bonus.example-login.com"
};

function setMode(next) {
  mode = next;
  tabs.forEach(t => {
    const active = t.dataset.mode === mode;
    t.classList.toggle("active", active);
    t.setAttribute("aria-selected", String(active));
  });
  document.getElementById("input-label").textContent = mode === "message" ? "PASTE A MESSAGE OR JOB OFFER" : "ENTER A WEBSITE ADDRESS";
  input.placeholder = mode === "message" ? "Paste a suspicious message here..." : "Paste a website URL here, e.g. https://example.com";
  input.value = "";
  updateCount();
  resultBox.hidden = true;
  errorBox.hidden = true;
}
tabs.forEach(t => t.addEventListener("click", () => setMode(t.dataset.mode)));
input.addEventListener("input", updateCount);
function updateCount() { document.getElementById("char-count").textContent = `${input.value.length.toLocaleString()} / 10,000`; }
document.getElementById("sample-btn").addEventListener("click", () => { input.value = samples[mode]; updateCount(); });

scanBtn.addEventListener("click", async () => {
  const value = input.value.trim();
  errorBox.hidden = true;
  resultBox.hidden = true;
  if (!value) { showError("Please enter something to scan first."); return; }
  scanBtn.disabled = true;
  scanBtn.querySelector("span").textContent = "Checking patterns...";
  try {
    const response = await fetch("/api/scan", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({type: mode, value})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Unable to scan this input.");
    renderResult(data);
    saveHistory(mode, value, data);
    renderHistory();
  } catch (err) {
    showError(err.message || "Something went wrong. Please try again.");
  } finally {
    scanBtn.disabled = false;
    scanBtn.querySelector("span").textContent = "Scan for warning signs";
  }
});
function showError(message) { errorBox.textContent = message; errorBox.hidden = false; }
function renderResult(data) {
  document.getElementById("score").textContent = data.score;
  document.getElementById("level").textContent = `${data.level.toUpperCase()} RISK INDICATORS`;
  document.getElementById("level").className = `level ${data.level.toLowerCase()}`;
  document.getElementById("summary").textContent = data.summary;
  const color = data.level === "High" ? "var(--red)" : data.level === "Medium" ? "var(--yellow)" : "var(--green)";
  document.getElementById("score-ring").style.background = `conic-gradient(${color} ${data.score * 3.6}deg, #223149 0deg)`;
  document.getElementById("findings").innerHTML = "";
  data.findings.forEach(f => {
    const div = document.createElement("div");
    div.className = "finding";
    const title = document.createElement("strong");
    title.textContent = f.title;
    const weight = document.createElement("span");
    weight.className = "weight";
    weight.textContent = f.weight ? `+${f.weight} pts` : "INFO";
    title.appendChild(weight);
    const p = document.createElement("p");
    p.textContent = f.advice;
    div.append(title, p);
    document.getElementById("findings").appendChild(div);
  });
  const ul = document.getElementById("recommendations");
  ul.innerHTML = "";
  data.recommendations.forEach(item => { const li = document.createElement("li"); li.textContent = item; ul.appendChild(li); });
  document.getElementById("disclaimer").textContent = data.disclaimer;
  resultBox.hidden = false;
  resultBox.scrollIntoView({behavior:"smooth", block:"nearest"});
}
function saveHistory(type, value, data) {
  const history = JSON.parse(localStorage.getItem("fakecheck-history") || "[]");
  history.unshift({type, preview:value.slice(0,70), score:data.score, level:data.level, time:new Date().toLocaleString()});
  localStorage.setItem("fakecheck-history", JSON.stringify(history.slice(0,8)));
}
function renderHistory() {
  const history = JSON.parse(localStorage.getItem("fakecheck-history") || "[]");
  const container = document.getElementById("history");
  container.innerHTML = "";
  if (!history.length) { container.innerHTML = '<p class="empty-history">Your recent scans will appear here.</p>'; return; }
  history.forEach(item => {
    const row = document.createElement("div"); row.className = "history-item";
    const left = document.createElement("div");
    const strong = document.createElement("strong"); strong.textContent = `${item.type === "message" ? "Message" : "URL"} · ${item.preview}`;
    const small = document.createElement("small"); small.textContent = item.time;
    left.append(strong, small);
    const right = document.createElement("span"); right.className = "history-badge"; right.textContent = `${item.level.toUpperCase()} · ${item.score}/100`;
    right.style.color = item.level === "High" ? "var(--red)" : item.level === "Medium" ? "var(--yellow)" : "var(--green)";
    row.append(left, right); container.appendChild(row);
  });
}
document.getElementById("clear-btn").addEventListener("click", () => { resultBox.hidden = true; });
document.getElementById("history-clear").addEventListener("click", () => { localStorage.removeItem("fakecheck-history"); renderHistory(); });
renderHistory();
