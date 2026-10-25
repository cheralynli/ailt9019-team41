"use strict";

const gameSelect = document.querySelector("#game");
const editionSelect = document.querySelector("#edition");
const question = document.querySelector("#question");
const submit = document.querySelector("#submit");
const sample = document.querySelector("#sample");
const form = document.querySelector("#question-form");
const answerSection = document.querySelector("#answer-section");
const feedback = document.querySelector("#feedback");
const viewMatches = document.querySelector("#view-matches");
let games = [];
let apiConfigured = false;
let cancelAnswerScroll = () => {};

function showFeedback(title, message, tone = "notice") {
  feedback.hidden = false;
  feedback.dataset.tone = tone;
  document.querySelector("#feedback-title").textContent = title;
  document.querySelector("#feedback-message").textContent = message;
  viewMatches.hidden = true;
}

function resetResult() {
  cancelAnswerScroll();
  answerSection.hidden = true;
  feedback.hidden = true;
  viewMatches.hidden = true;
  document.querySelector("#citations").replaceChildren();
  document.querySelector("#asked-question").textContent = "";
  document.querySelector("#answer-text").textContent = "";
  const game = games.find(item => item.id === gameSelect.value);
  const searchOnly = game?.answer_mode !== "ai_ready";
  document.querySelector("#ruleset-status").textContent = gameSelect.value === "chess"
    ? searchOnly ? "Chess is search-only until its official-law passages are verified." : "Chess uses verified law-only text, excluding commentary and non-law guidance."
    : "Search stays within the selected ruleset. Expansions include their base rules.";
  document.querySelector("#model-status").textContent = searchOnly ? "Source verification or indexing is still needed."
    : apiConfigured ? "The course API is configured. Availability and quota are checked when you ask."
    : "No API key configured. You can still search the local rulebooks.";
}

function setEditions() {
  const game = games.find(item => item.id === gameSelect.value);
  editionSelect.replaceChildren(...game.editions.map(item => new Option(item.name, item.id)));
  question.placeholder = game.sample;
  resetResult();
}

function showCitations(citations) {
  const container = document.querySelector("#citations");
  container.replaceChildren();
  for (const citation of citations) {
    const card = document.createElement("details");
    card.className = "source-card";
    const summary = document.createElement("summary");
    summary.textContent = citation.document + " · " + citation.edition_label + " · PDF page " + citation.page
      + (citation.printed_page ? " (printed " + citation.printed_page + ")" : "");
    const body = document.createElement("div");
    body.className = "source-body";
    const quote = document.createElement("blockquote");
    quote.textContent = citation.text;
    body.append(quote);
    if (citation.warning) {
      const warning = document.createElement("p");
      warning.className = "source-warning";
      warning.textContent = citation.warning;
      body.append(warning);
    }
    if (typeof citation.source_url === "string" && /^\/api\/sources\/[a-z0-9-]+#page=\d+$/.test(citation.source_url)) {
      const link = document.createElement("a");
      link.href = citation.source_url;
      link.target = "_blank";
      link.rel = "noopener";
      link.textContent = "Open original PDF · page " + citation.page + " ↗";
      body.append(link);
    }
    card.append(summary, body);
    container.append(card);
  }
}

function gentleScrollTo(destination) {
  cancelAnswerScroll();
  const startY = window.scrollY;
  const targetY = Math.max(0, Math.min(destination,
    document.documentElement.scrollHeight - window.innerHeight));
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    window.scrollTo({ top: targetY, behavior: "instant" });
    return;
  }
  // Longer journeys (including expanded citations) get extra time too.
  const duration = Math.min(3200, Math.max(2200, Math.abs(targetY - startY) * 0.8));
  let startedAt;
  let frame;
  const stop = () => {
    window.cancelAnimationFrame(frame);
    for (const event of ["wheel", "touchstart", "pointerdown", "keydown"]) window.removeEventListener(event, stop);
    cancelAnswerScroll = () => {};
  };
  cancelAnswerScroll = stop;
  // Give control back immediately if the player scrolls or interacts.
  for (const event of ["wheel", "touchstart", "pointerdown", "keydown"]) window.addEventListener(event, stop, { passive: true });
  const step = timestamp => {
    startedAt ??= timestamp;
    const progress = Math.min((timestamp - startedAt) / duration, 1);
    const eased = (1 - Math.cos(Math.PI * progress)) / 2;
    window.scrollTo({ top: startY + (targetY - startY) * eased, behavior: "instant" });
    if (progress < 1) frame = window.requestAnimationFrame(step);
    else stop();
  };
  frame = window.requestAnimationFrame(step);
}

function revealAnswer() {
  answerSection.hidden = false;
  document.querySelector("#result-heading").focus({ preventScroll: true });
  gentleScrollTo(window.scrollY + answerSection.getBoundingClientRect().top);
}

function presentResponse(data, selection) {
  const citations = Array.isArray(data.citations) ? data.citations : [];
  if (data.status === "answer" || (data.status === "search_only" && citations.length)) {
    const excerpt = data.answer_method === "source_excerpt";
    document.querySelector("#result-status").textContent = data.status === "search_only" ? "Search only" : excerpt ? "Source excerpts" : "Supported answer";
    document.querySelector("#answer-label").textContent = data.status === "search_only" ? "MATCHING PASSAGES · NOT AN AI RULING"
      : excerpt ? "RULEBOOK EXCERPTS · NOT AI-GENERATED" : "AI EXPLANATION · CHECK THE SOURCES";
    document.querySelector("#result-heading").textContent = data.status === "search_only" ? "Here’s where to look." : excerpt ? "Straight from the rulebook." : "Here’s the rule.";
    document.querySelector("#asked-question").textContent = selection;
    document.querySelector("#answer-text").textContent = data.message;
    showCitations(citations);
    if (data.status === "answer") {
      feedback.hidden = true;
      revealAnswer();
    } else {
      showFeedback("Matching passages found — no AI ruling.", data.message);
      viewMatches.hidden = false;
    }
    return;
  }
  answerSection.hidden = true;
  const headings = {
    refusal: "I can’t give a supported answer to that.",
    clarification: "A little more detail?",
    api_error: "The AI service isn’t available right now.",
    not_ready: "This rulebook isn’t ready yet.",
    unsupported: "That’s outside the selected ruleset.",
    no_evidence: "I couldn’t find a supporting rule.",
    search_only: "No AI answer is available."
  };
  showFeedback(headings[data.status] || "Unable to show an answer.", data.message || "Please try again.",
    data.status === "api_error" ? "error" : "notice");
}

gameSelect.addEventListener("change", () => { setEditions(); question.value = ""; });
editionSelect.addEventListener("change", resetResult);
sample.addEventListener("click", () => {
  resetResult();
  question.value = games.find(item => item.id === gameSelect.value).sample;
  question.focus();
});
viewMatches.addEventListener("click", revealAnswer);
document.querySelector("#ask-another").addEventListener("click", () => {
  question.focus({ preventScroll: true });
  gentleScrollTo(0);
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  const input = question.value.trim();
  resetResult();
  if (!input) {
    showFeedback("What would you like to know?", "Enter a rules question, or try a sample.");
    question.focus();
    return;
  }
  if (input.length > 2000) {
    showFeedback("That question is a little long.", "Please keep your question under 2,001 characters.");
    question.focus();
    return;
  }
  const selection = gameSelect.selectedOptions[0].text + " · " + editionSelect.selectedOptions[0].text + " — " + input;
  const payload = { game: gameSelect.value, edition: editionSelect.value, question: input };
  submit.disabled = gameSelect.disabled = editionSelect.disabled = sample.disabled = question.disabled = true;
  form.setAttribute("aria-busy", "true");
  document.querySelector("#submit-label").textContent = "Checking…";
  showFeedback("Checking the rulebook", "Finding relevant passages" + (apiConfigured ? " and checking the explanation." : "."), "loading");
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 110000);
  try {
    const response = await fetch("/api/ask", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload), signal: controller.signal
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The request could not be completed.");
    if (typeof data.status !== "string" || typeof data.message !== "string") throw new Error("An incomplete response was received. Please try again.");
    presentResponse(data, selection);
  } catch (error) {
    showFeedback("Something interrupted the connection.", error.name === "AbortError"
      ? "The request timed out. Please try again in a moment." : error.message, "error");
  } finally {
    clearTimeout(timeout);
    submit.disabled = gameSelect.disabled = editionSelect.disabled = sample.disabled = question.disabled = false;
    form.setAttribute("aria-busy", "false");
    document.querySelector("#submit-label").textContent = "Ask BoardMaster";
  }
});

async function initialise() {
  try {
    const response = await fetch("/api/games");
    if (!response.ok) throw new Error("Could not load the rulebooks.");
    const data = await response.json();
    games = data.games;
    if (!Array.isArray(games) || !games.length) throw new Error("No games available.");
    apiConfigured = data.mode === "course";
    document.querySelector("#service-status").textContent = apiConfigured ? "AI configured" : "Local search";
    document.querySelector("#collection-status").textContent = data.passage_count
      ? data.source_count + " documents · " + data.passage_count + " searchable passages. " + (apiConfigured ? "Model: " + (data.model || "server-selected") + "." : "")
      : "No passages indexed yet. Ask your team to rebuild the rulebook index.";
    gameSelect.replaceChildren(...games.map(game => new Option(game.name, game.id)));
    setEditions();
    gameSelect.disabled = editionSelect.disabled = submit.disabled = sample.disabled = false;
  } catch {
    document.querySelector("#service-status").textContent = "Offline";
    document.querySelector("#collection-status").textContent = "Could not load the rulebook index.";
    showFeedback("The website can’t reach the server.", "Check that the Python app is running, then refresh this page.", "error");
  }
}
initialise();
