/*
 * Shared interactive components for The Pond's activity pages.
 * Uses the shared .pond-pad-* styles in styles.css (and .pond-md-* for "What would you need?").
 *
 * The response summary itself is built by scripts/response-summary.js (PondSummary);
 * this file only adds Pond.needMd, for PondSummary handlers.
 *
 * Load both from a page with a relative path, then call them from an inline script:
 *   <script src="../../../scripts/response-summary.js"></script>
 *   <script src="../../../scripts/pond-activities.js"></script>
 *
 *   const state = Pond.store("pond-mypage");     // learner answers, kept in this browser only
 *   Pond.textBoxes(state);                        // .pond-md-save inputs and textareas
 *   Pond.whatifs(state);                          // .pond-pad-whatif single-choice groups
 *   const needs = Pond.needBanks(state);          // .pond-md-need "pick, then reveal" activities
 *   Pond.restore(state, needs);                   // re-reveal what was revealed on an earlier visit
 *   PondSummary.attach({ ..., handlers: [{ selector: ".pond-md-need",
 *     md: el => Pond.needMd(needs.find(n => n.bank === el)) }] });
 *
 * Markup for each component: see lilypads/workflow/containers/index.qmd.
 */
(function () {
  "use strict";

  // ---------- Storage: answers stay in this browser (localStorage, never sent anywhere) ----------

  function store(key) {
    let saved = {};
    try { saved = JSON.parse(localStorage.getItem(key)) || {}; } catch (e) {}
    ["notes", "picks", "whatif"].forEach(k => {
      if (typeof saved[k] !== "object" || !saved[k] || Array.isArray(saved[k])) saved[k] = {};
    });
    if (!Array.isArray(saved.revealed)) saved.revealed = [];
    return {
      saved,
      save() { try { localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {} },
      hooks: {}   // functions run after a given activity is revealed, keyed by its id
    };
  }

  // ---------- Free-text and number answers ----------

  function textBoxes(state, selector = ".pond-md-save") {
    document.querySelectorAll(selector).forEach(box => {
      if (state.saved.notes[box.id] !== undefined) box.value = state.saved.notes[box.id];
      box.addEventListener("input", () => { state.saved.notes[box.id] = box.value; state.save(); });
    });
  }

  // ---------- Single-choice buttons that show a short verdict ----------
  // <div class="pond-pad-whatif" role="group" aria-label="Question">
  //   <button type="button" class="pond-pad-tag" aria-pressed="false" data-verdict="...">Option</button>
  // </div>
  // <p class="pond-pad-take" aria-live="polite" hidden></p>

  function whatifs(state) {
    const groups = [...document.querySelectorAll(".pond-pad-whatif")];
    groups.forEach((group, g) => {
      const out = group.nextElementSibling;
      const buttons = [...group.querySelectorAll("button")];
      function choose(i) {
        buttons.forEach((b, j) => b.setAttribute("aria-pressed", String(i === j)));
        out.textContent = buttons[i].dataset.verdict;
        out.hidden = false;
      }
      buttons.forEach((btn, i) => btn.addEventListener("click", () => {
        state.saved.whatif[g] = i;
        state.save();
        choose(i);
      }));
      if (buttons[state.saved.whatif[g]]) choose(state.saved.whatif[g]);
    });
    return groups;
  }

  // ---------- Elements shown only after an activity is revealed (data-after="<activity id>") ----------

  function hideAfter() {
    document.querySelectorAll("[data-after]").forEach(el => { el.hidden = true; });
  }
  function showAfter(state, id) {
    document.querySelectorAll(`[data-after="${id}"]`).forEach(el => { el.hidden = false; });
    if (state.hooks[id]) state.hooks[id]();
  }

  // ---------- "What would you need?": pick options, then reveal what each one is for ----------
  // ::: {#my-id .pond-md-need data-yes="Needed" data-no="Not needed" data-button="Reveal our answer"}
  // ::: {.pond-md-option data-name="Option" data-needed="true"}
  // Why it is (or isn't) needed.
  // :::
  // ::: {.pond-md-meta}
  // Shown after the reveal.
  // :::
  // :::

  function needBanks(state) {
    const { saved } = state;
    const needs = [];
    hideAfter();
    document.querySelectorAll(".pond-md-need").forEach(bank => {
      const id = bank.id;
      const yes = bank.dataset.yes || "Needed";
      const no = bank.dataset.no || "Not needed";
      const options = [...bank.querySelectorAll(":scope > .pond-md-option")].map(div => ({
        name: div.dataset.name, needed: div.dataset.needed === "true", html: div.innerHTML
      }));
      const meta = bank.querySelector(":scope > .pond-md-meta");
      const picks = saved.picks[id] = Array.isArray(saved.picks[id]) ? saved.picks[id] : [];

      const box = document.createElement("div");
      box.className = "pond-pad";
      box.innerHTML = `
        <div class="pond-pad-choices" role="group" aria-label="Options to choose from"></div>
        <p class="pond-pad-status" aria-live="polite"></p>
        <button type="button" class="btn btn-primary"></button>
        <div class="pond-pad-cards" hidden></div>`;
      const choices = box.querySelector(".pond-pad-choices");
      const status = box.querySelector(".pond-pad-status");
      const revealBtn = box.querySelector(".btn-primary");
      const cards = box.querySelector(".pond-pad-cards");
      revealBtn.textContent = bank.dataset.button || "Reveal our answer";

      function updateStatus() {
        status.textContent = picks.length ? `${picks.length} of ${options.length} selected.` : "Nothing selected yet.";
      }

      options.forEach(opt => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "pond-pad-tag";
        btn.textContent = opt.name;
        btn.setAttribute("aria-pressed", String(picks.includes(opt.name)));
        btn.addEventListener("click", () => {
          const on = btn.getAttribute("aria-pressed") !== "true";
          btn.setAttribute("aria-pressed", String(on));
          if (on) picks.push(opt.name); else picks.splice(picks.indexOf(opt.name), 1);
          state.save();
          updateStatus();
          const card = cards.querySelector(`[data-name="${CSS.escape(opt.name)}"]`);
          if (card) card.classList.toggle("is-picked", on);
        });
        choices.append(btn);
      });
      updateStatus();

      function reveal() {
        cards.innerHTML = "";
        options.forEach(opt => {
          const card = document.createElement("div");
          card.className = "pond-pad-card" + (opt.needed ? " is-needed" : "");
          card.dataset.name = opt.name;
          card.classList.toggle("is-picked", picks.includes(opt.name));
          card.innerHTML = `<h4></h4><span class="pond-md-badge"></span><div class="pond-pad-card-text"></div>`;
          card.querySelector("h4").textContent = opt.name;
          card.querySelector(".pond-md-badge").textContent = opt.needed ? yes : no;
          card.querySelector(".pond-pad-card-text").innerHTML = opt.html;
          cards.append(card);
        });
        cards.hidden = false;
        revealBtn.hidden = true;
        if (meta) meta.hidden = false;
        if (!saved.revealed.includes(id)) { saved.revealed.push(id); state.save(); }
        showAfter(state, id);
      }
      revealBtn.addEventListener("click", reveal);

      bank.querySelectorAll(":scope > .pond-md-option").forEach(div => div.remove());
      if (meta) {
        meta.classList.add("pond-pad-notes", "pond-md-meta-panel");
        meta.hidden = true;
      }
      bank.prepend(box);
      needs.push({ id, reveal, bank, options, picks, yes, no, meta });
    });
    return needs;
  }

  // Re-reveal activities revealed on an earlier visit. Call after setting state.hooks.
  function restore(state, needs) {
    needs.forEach(n => { if (state.saved.revealed.includes(n.id)) n.reveal(); });
  }

  // ---------- For the response summary (PondSummary handler) ----------
  // The learner's picks in a "What would you need?" activity, then our answer

  function needMd(n) {
    if (!n) return "";
    const blockMd = window.PondSummary.blockMd;
    const lines = [];
    n.options.forEach(opt => {
      const picked = n.picks.includes(opt.name);
      if (picked && opt.needed) lines.push(`- ✓ ${opt.name}`);
      else if (picked) lines.push(`- ✗ ${opt.name} (${n.no.toLowerCase()})`);
      else if (opt.needed) lines.push(`- ○ ${opt.name} (missed)`);
    });
    let s = "**My choices** (✓ = matches our answer, ✗ = doesn't, ○ = missed):\n\n" +
      (lines.length ? lines.join("\n") : "*None selected.*");
    s += "\n\n" + n.options.filter(o => o.needed).map(o => {
      const tmp = document.createElement("div");
      tmp.innerHTML = o.html;
      return `**Our take: ${o.name}.** ${blockMd(tmp)}`;
    }).join("\n\n");
    if (n.meta) s += "\n\n" + blockMd(n.meta);
    return s;
  }

  window.Pond = { store, textBoxes, whatifs, needBanks, restore, showAfter, needMd };
})();
