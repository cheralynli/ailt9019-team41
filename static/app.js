"use strict";

const gameSelect = document.querySelector("#game");
const editionSelect = document.querySelector("#edition");
const question = document.querySelector("#question");
const submit = document.querySelector("#submit");
const sample = document.querySelector("#sample");
const form = document.querySelector("#question-form");
let games = [];

function setEditions() {
  const game = games.find(item => item.id === gameSelect.value);
  editionSelect.replaceChildren(...game.editions.map(item => new Option(item.name, item.id)));
}

function showResult(status, heading, message) {
  document.querySelector("#result-status").textContent = status;
  document.querySelector("#answer-label").textContent = "RULEBOOK SEARCH · NOT AN AI RULING";
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
  // Future model adapter must return only validated citations from retrieved data.
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
sample.addEventListener("click", () => {
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
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch("/api/ask", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ game: gameSelect.value, edition: editionSelect.value, question: input }),
      signal: controller.signal
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The request could not be completed.");
    const headings = { search_only: "Here’s where to look.", not_ready: "Rulebook index needed.", unsupported: "Outside the planned scope.", no_evidence: "No matching passage found." };
    showResult(data.status === "search_only" ? "Search only" : data.status === "not_ready" ? "Setup needed" : "No ruling", headings[data.status] || "Pipeline response", data.message);
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
    document.querySelector("#collection-status").textContent = data.passage_count
      ? `${data.source_count} documents indexed · ${data.passage_count} searchable excerpts. Results are source passages, not verified AI rulings.`
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
