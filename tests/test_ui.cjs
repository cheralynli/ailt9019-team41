// Offline DOM-contract checks. No provider calls or real AI answers.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'static/app.js'), 'utf8');
const html = fs.readFileSync(path.join(root, 'static/index.html'), 'utf8');

function setup(reduced = false) {
  const elements = new Map();
  const frames = new Map();
  const listeners = new Map();
  let frameId = 0;
  const scrolls = [];
  function element() {
    return {hidden: false, dataset: {}, textContent: '', children: [], handlers: {},
      selectedOptions: [{text: 'Synthetic ruleset'}], value: '', disabled: false,
      replaceChildren(...items) { this.children = items; },
      append(...items) { this.children.push(...items); },
      addEventListener(name, fn) { this.handlers[name] = fn; },
      getBoundingClientRect() { return {top: 900}; },
      setAttribute() {}, focus() {}, scrollIntoView(options) { this.scroll = options; }};
  }
  for (const match of html.matchAll(/id="([^"]+)"/g)) elements.set('#' + match[1], element());
  const context = vm.createContext({
    document: {documentElement: {scrollHeight: 2200}, querySelector(id) { assert.ok(elements.has(id), 'Missing DOM ID ' + id); return elements.get(id); }, createElement: element},
    window: {matchMedia: () => ({matches: reduced}), scrollY: 0, innerHeight: 800,
      requestAnimationFrame(fn) { frames.set(++frameId, fn); return frameId; },
      cancelAnimationFrame(id) { frames.delete(id); },
      scrollTo(options) { scrolls.push(options.top); },
      addEventListener(name, fn) { listeners.set(name, fn); },
      removeEventListener(name) { listeners.delete(name); }},
    Option: function(text, value) { this.text = text; this.value = value; },
    fetch: () => new Promise(() => {}), AbortController, setTimeout, clearTimeout
  });
  vm.runInContext(source, context);
  return {elements, context, frames, listeners, scrolls,
    tick(time) { const pending = [...frames.values()]; frames.clear(); pending.forEach(fn => fn(time)); },
    run: code => vm.runInContext(code, context)};
}

test('supported answer reveals and scrolls to the black results section', () => {
  const ui = setup();
  ui.run('presentResponse({status:"answer", message:"Synthetic test answer", citations:[]}, "Test question")');
  assert.equal(ui.elements.get('#answer-section').hidden, false);
  ui.tick(0);
  ui.tick(1100);
  assert.ok(Math.abs(ui.scrolls.at(-1) - 450) < 1);
  ui.tick(2200);
  assert.equal(ui.scrolls.at(-1), 900);
  assert.equal(ui.frames.size, 0);
  assert.equal(ui.listeners.size, 0);
  assert.equal(ui.elements.get('#feedback').hidden, true);
});

test('all non-answer states stay inline without scrolling', () => {
  for (const status of ['refusal', 'clarification', 'api_error', 'not_ready', 'unsupported', 'no_evidence', 'unexpected']) {
    const ui = setup();
    ui.run('presentResponse({status:' + JSON.stringify(status) + ',message:"Original backend message",citations:[]}, "Test")');
    assert.equal(ui.elements.get('#answer-section').hidden, true, status);
    assert.equal(ui.elements.get('#answer-section').scroll, undefined, status);
    assert.equal(ui.frames.size, 0);
    assert.equal(ui.elements.get('#feedback-message').textContent, 'Original backend message');
  }
});

test('search-only results require an explicit click and are not labelled AI answers', () => {
  const ui = setup();
  ui.run('answerSection.hidden=true; presentResponse({status:"search_only",message:"Search results",citations:[{document:"Fixture",edition_label:"Test",page:1,text:"Synthetic"}]}, "Test")');
  assert.equal(ui.elements.get('#answer-section').hidden, true);
  assert.equal(ui.elements.get('#view-matches').hidden, false);
  ui.elements.get('#view-matches').handlers.click();
  assert.equal(ui.elements.get('#answer-section').hidden, false);
  assert.match(ui.elements.get('#answer-label').textContent, /NOT AN AI RULING/);
});

test('reduced motion disables smooth scrolling', () => {
  const ui = setup(true);
  ui.run('revealAnswer()');
  assert.equal(ui.scrolls.at(-1), 900);
  assert.equal(ui.frames.size, 0);
});

test('ask another question gently returns all the way to page top', () => {
  const ui = setup();
  ui.run('window.scrollY = 1200');
  ui.elements.get('#ask-another').handlers.click();
  ui.tick(0);
  assert.equal(ui.scrolls.at(-1), 1200);
  ui.tick(1100);
  assert.ok(Math.abs(ui.scrolls.at(-1) - 600) < 1);
  ui.tick(2200);
  assert.equal(ui.scrolls.at(-1), 0);
  assert.equal(ui.frames.size, 0);
});

test('return to top respects reduced motion and replaces an active scroll', () => {
  const reduced = setup(true);
  reduced.run('window.scrollY = 1200');
  reduced.elements.get('#ask-another').handlers.click();
  assert.equal(reduced.scrolls.at(-1), 0);
  assert.equal(reduced.frames.size, 0);
  const ui = setup();
  ui.run('revealAnswer()');
  ui.elements.get('#ask-another').handlers.click();
  assert.equal(ui.frames.size, 1);
});

test('player interaction cancels the gentle scroll', () => {
  const ui = setup();
  ui.run('revealAnswer()');
  ui.tick(0);
  ui.listeners.get('wheel')();
  ui.tick(700);
  assert.equal(ui.scrolls.length, 1);
  assert.equal(ui.frames.size, 0);
  assert.equal(ui.listeners.size, 0);
});

test('source-extractive answer retains truthful label', () => {
  const ui = setup();
  ui.run('presentResponse({status:"answer",answer_method:"source_excerpt",message:"Synthetic quote",citations:[]}, "Test")');
  assert.match(ui.elements.get('#answer-label').textContent, /NOT AI-GENERATED/);
});

test('citations use expandable details and never inject response HTML', () => {
  const ui = setup();
  ui.run('showCitations([{document:"Fixture",edition_label:"Test",page:1,text:"<script>bad()</script>",source_url:"javascript:bad()"}])');
  const card = ui.elements.get('#citations').children[0];
  assert.equal(card.children[1].children[0].textContent, '<script>bad()</script>');
  assert.equal(card.children[1].children.length, 1);
});

test('empty question is handled inline without a request', async () => {
  const ui = setup();
  ui.elements.get('#question').value = '   ';
  await ui.elements.get('#question-form').handlers.submit({preventDefault() {}});
  assert.equal(ui.elements.get('#feedback').hidden, false);
  assert.equal(ui.elements.get('#answer-section').hidden, true);
});
