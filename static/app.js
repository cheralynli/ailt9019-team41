"use strict";

const gameSelect = document.querySelector("#game");
const editionSelect = document.querySelector("#edition");
const question = document.querySelector("#question");
const submit = document.querySelector("#submit");
const sample = document.querySelector("#sample");
const form = document.querySelector("#question-form");
let games = [];
let apiConfigured = false;

function resetResult() {
  const edition = editionSelect.selectedOptions[0]?.text || "this ruleset";
  showResult("Ready", "Ask about the selected ruleset.", `Current selection: ${edition}. Each question is independent; include enough detail to identify the rule.`);
  document.querySelector("#asked-question").hidden = true;
  document.querySelector("#asked-question").textContent = "";
  showCitations([]);
  const chess = gameSelect.value === "chess";
  const searchOnly = games.find(item => item.id === gameSelect.value)?.answer_mode !== "ai_ready";
  document.querySelector("#ruleset-status").textContent = chess && searchOnly
    ? "Chess is currently search-only: official laws and arbiter commentary have not yet been separated."
    : chess ? "Chess AI uses verified law-only text. Commentary, non-law guidelines and glossary entries are excluded." : "Search stays within the selected ruleset. Expansions include their base rules.";
  const marker = document.querySelector("#model-step");
  marker.classList.toggle("built", apiConfigured && !searchOnly);
  document.querySelector("#model-status").textContent = searchOnly ? "Source verification / index needed" : apiConfigured ? "Course API configured · requests checked on use" : "Local search only · API key not configured";
}

function setEditions() {
  const game = games.find(item => item.id === gameSelect.value);
  editionSelect.replaceChildren(...game.editions.map(item => new Option(item.name, item.id)));
  resetResult();
}

function showResult(status, heading, message) {
  document.querySelector("#result-status").textContent = status;
  document.querySelector("#answer-label").textContent = status === "Answer" ? "AI EXPLANATION · CHECK THE SOURCES" : "RULEBOOK ASSISTANT";
  document.querySelector("#result-heading").textContent = heading;
  document.querySelector("#answer-text").textContent = message;
}

function showCitations(citations) {
  const container = document.querySelector("#citations");
  container.replaceChildren();
  if (!citations.length) {
    const note = document.createElement("p");
    note.textContent = "No matching passages to display.";
    container.append(note);
    return;
  }
  // Citation metadata is drawn from validated retrieved passages.
  for (const citation of citations) {
    const card = document.createElement("article");
    card.className = "source-card";
    const quote = document.createElement("blockquote");
    quote.textContent = citation.text;
    const source = document.createElement("p");
    source.textContent = `${citation.document} · ${citation.game} · ${citation.edition_label} · PDF page ${citation.page}${citation.printed_page ? ` (printed page ${citation.printed_page})` : ""}`;
    card.append(source, quote);
    if (citation.warning) {
      const warning = document.createElement("p");
      warning.className = "source-warning";
      warning.textContent = citation.warning;
      card.append(warning);
    }
    if (typeof citation.source_url === "string" && /^\/api\/sources\/[a-z0-9-]+#page=\d+$/.test(citation.source_url)) {
      const link = document.createElement("a");
      link.href = citation.source_url;
      link.target = "_blank";
      link.rel = "noopener";
      link.textContent = `Open original PDF · page ${citation.page}`;
      card.append(link);
    }
    container.append(card);
  }
}

gameSelect.addEventListener("change", setEditions);
editionSelect.addEventListener("change", resetResult);
sample.addEventListener("click", () => {
  resetResult();
  question.value = games.find(item => item.id === gameSelect.value).sample;
  question.focus();
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  const input = question.value.trim();
  if (!input) { question.focus(); return; }
  submit.disabled = true;
  gameSelect.disabled = true;
  editionSelect.disabled = true;
  sample.disabled = true;
  submit.textContent = "Checking…";
  const asked = document.querySelector("#asked-question");
  asked.hidden = false;
  asked.textContent = `${gameSelect.selectedOptions[0].text} · ${editionSelect.selectedOptions[0].text}: ${input}`;
  showResult("Processing", "Checking the local pipeline…", "Sending your question to the Python backend.");
  showCitations([]);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);
  try {
    const response = await fetch("/api/ask", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ game: gameSelect.value, edition: editionSelect.value, question: input }),
      signal: controller.signal
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The request could not be completed.");
    const headings = { answer: "Here’s the supported explanation.", refusal: "Cannot provide a supported ruling.", clarification: "Please clarify your question.", api_error: "Model unavailable.", search_only: "Here’s where to look.", not_ready: "Rulebook index needed.", unsupported: "Outside the planned scope.", no_evidence: "No matching passage found." };
    const labels = {answer: "Answer", refusal: "Refused", clarification: "Clarification needed", api_error: "API issue", search_only: "Search only", not_ready: "Setup needed", unsupported: "Unsupported", no_evidence: "No evidence"};
    showResult(labels[data.status] || "Response", headings[data.status] || "Pipeline response", data.message + (data.diagnostic ? ` [${data.diagnostic}]` : ""));
    showCitations(data.citations || []);
  } catch (error) {
    showResult("Connection issue", "Let’s check the connection.", error.name === "AbortError" ? "The request timed out. Check that the Python server is running and try again." : error.message);
  } finally {
    clearTimeout(timeout);
    submit.disabled = false;
    gameSelect.disabled = false;
    editionSelect.disabled = false;
    sample.disabled = false;
    submit.textContent = "Ask BoardMaster →";
  }
});

async function initialise() {
  try {
    const response = await fetch("/api/games");
    if (!response.ok) throw new Error("Could not load the game list.");
    const data = await response.json();
    games = data.games;
    apiConfigured = data.mode === "course";
    document.querySelector("#service-status").textContent = apiConfigured
      ? `Course API configured · ${data.model || "server-selected model"}`
      : "Local search only · course API key not configured";
    document.querySelector("#collection-status").textContent = data.passage_count
      ? `${data.source_count} documents indexed · ${data.passage_count} searchable excerpts. Check every explanation against its cited source passages.`
      : "No passages indexed yet. Run python3 -m referee.indexer to connect the rulebooks.";
    gameSelect.replaceChildren(...games.map(game => new Option(game.name, game.id)));
    setEditions();
    gameSelect.disabled = editionSelect.disabled = submit.disabled = sample.disabled = false;
  } catch {
    document.querySelector("#collection-status").textContent = "Could not load the rulebook index. Check the Python server and rebuild the index if needed.";
    showResult("Connection issue", "The backend is unavailable.", "Start the app with python3 app.py, then reload this page.");
  }
}
initialise();
