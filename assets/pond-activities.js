/*
 * Shared interactive components for The Pond's activity pages.
 * Uses the .pond-md-* styles in styles.css (first designed for lilypads/data/metadata).
 *
 * Load it from a page with a relative path, then call it from an inline script:
 *   <script src="../../../assets/pond-activities.js"></script>
 *
 *   const state = Pond.store("pond-mypage");     // learner answers, kept in this browser only
 *   Pond.textBoxes(state);                        // .pond-md-save inputs and textareas
 *   const whatifs = Pond.whatifs(state);          // .pond-md-whatif single-choice groups
 *   const needs = Pond.needBanks(state);          // .pond-md-need "pick, then reveal" activities
 *   Pond.restore(state, needs);                   // re-reveal what was revealed on an earlier visit
 *   Pond.downloadMarkdown("mypage-response-summary.md", text);
 *
 * Markup for each component: see lilypads/workflow/containers/index.qmd.
 *
 * TODO: harmonize with scripts/response-summary.js (PondSummary), added by the data-quality
 * branch (PR #83). Once it is merged, build this page's summary with PondSummary and keep
 * only the widgets (text boxes, single-choice groups, "What would you need?") here.
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
  // <div class="pond-md-whatif" role="group" aria-label="Question">
  //   <button type="button" class="pond-md-tag" aria-pressed="false" data-verdict="...">Option</button>
  // </div>
  // <p class="pond-md-take" aria-live="polite" hidden></p>

  function whatifs(state) {
    const groups = [...document.querySelectorAll(".pond-md-whatif")];
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
      box.className = "pond-md";
      box.innerHTML = `
        <div class="pond-md-choices" role="group" aria-label="Options to choose from"></div>
        <p class="pond-md-status" aria-live="polite"></p>
        <button type="button" class="btn btn-primary"></button>
        <div class="pond-md-cards" hidden></div>`;
      const choices = box.querySelector(".pond-md-choices");
      const status = box.querySelector(".pond-md-status");
      const revealBtn = box.querySelector(".btn-primary");
      const cards = box.querySelector(".pond-md-cards");
      revealBtn.textContent = bank.dataset.button || "Reveal our answer";

      function updateStatus() {
        status.textContent = picks.length ? `${picks.length} of ${options.length} selected.` : "Nothing selected yet.";
      }

      options.forEach(opt => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "pond-md-tag";
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
          card.className = "pond-md-card" + (opt.needed ? " is-needed" : "");
          card.dataset.name = opt.name;
          card.classList.toggle("is-picked", picks.includes(opt.name));
          card.innerHTML = `<h4></h4><span class="pond-md-badge"></span><div class="pond-md-card-text"></div>`;
          card.querySelector("h4").textContent = opt.name;
          card.querySelector(".pond-md-badge").textContent = opt.needed ? yes : no;
          card.querySelector(".pond-md-card-text").innerHTML = opt.html;
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
        meta.classList.add("pond-md-notes", "pond-md-meta-panel");
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

  // ---------- Page HTML to Markdown, for the response summary ----------

  function inlineMd(node) {
    let s = "";
    node.childNodes.forEach(n => {
      if (n.nodeType === Node.TEXT_NODE) { s += n.textContent.replace(/\s+/g, " "); return; }
      if (n.nodeType !== Node.ELEMENT_NODE || n.classList.contains("anchorjs-link")) return;
      const inner = inlineMd(n);
      switch (n.tagName) {
        case "STRONG": case "B": s += `**${inner.trim()}**`; break;
        case "EM": case "I": s += `*${inner.trim()}*`; break;
        case "CODE": s += "`" + n.textContent + "`"; break;
        case "A": s += `[${inner.trim()}](${n.href})`; break;
        case "BR": s += "  \n"; break;
        default: s += inner;
      }
    });
    return s;
  }

  function blockMd(node) {
    const blocks = [];
    [...node.children].forEach(el => {
      switch (el.tagName) {
        case "P": blocks.push(inlineMd(el).trim()); break;
        case "UL": case "OL":
          blocks.push([...el.children].map(li => "- " + inlineMd(li).trim()).join("\n")); break;
        case "TABLE": {
          const rows = [...el.querySelectorAll("tr")].map(tr =>
            "| " + [...tr.cells].map(c => inlineMd(c).trim().replace(/\|/g, "\\|")).join(" | ") + " |");
          if (rows.length) rows.splice(1, 0, "|" + " --- |".repeat(el.rows[0].cells.length));
          blocks.push(rows.join("\n")); break;
        }
        case "PRE": blocks.push("```\n" + el.textContent.trim() + "\n```"); break;
        case "BLOCKQUOTE": blocks.push(blockMd(el).split("\n").map(l => "> " + l).join("\n")); break;
        case "SUMMARY": case "BUTTON": case "IMG": break;
        default: if (el.children.length) blocks.push(blockMd(el));
      }
    });
    return blocks.filter(Boolean).join("\n\n");
  }

  // Markdown for one element (a clone, so the page is untouched)
  function elementMd(el) {
    const wrap = document.createElement("div");
    wrap.append(el.cloneNode(true));
    return blockMd(wrap);
  }

  // The learner's picks in a "What would you need?" activity, with our answer
  function needMd(n) {
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

  // The learner's choice in a single-choice group
  function whatifMd(state, groups, el) {
    const i = state.saved.whatif[groups.indexOf(el)];
    const btn = el.querySelectorAll("button")[i];
    return `**${el.getAttribute("aria-label")}**  \n` +
      (btn ? `My answer: *${btn.textContent.trim()}*. ${btn.dataset.verdict}` : "*Not answered.*");
  }

  // A "Key takeaway" heading's text: the paragraph or quote right after it
  function takeawayMd(heading) {
    const next = heading.nextElementSibling;
    return next ? elementMd(next).replace(/^>\s*/gm, "").trim() : "";
  }

  function labelFor(id) {
    const label = document.querySelector(`label[for="${id}"]`);
    return label ? label.textContent.trim() : "My answer";
  }

  function downloadMarkdown(filename, text) {
    const a = document.createElement("a");
    a.href = "data:text/markdown;charset=utf-8," + encodeURIComponent(text);
    a.download = filename;
    document.body.append(a);
    a.click();
    a.remove();
  }

  window.Pond = {
    store, textBoxes, whatifs, needBanks, restore, showAfter,
    inlineMd, blockMd, elementMd, needMd, whatifMd, takeawayMd, labelFor, downloadMarkdown
  };
})();
