// Shared "Download response summary" builder (see CLAUDE.md and issue #79).
//
// A page loads this file, then, once its own activities are built, calls:
//
//   PondSummary.attach({
//     button: document.getElementById("..."),   // the download button
//     filename: "page-response-summary.md",
//     title: "Page title",                       // first line of the file
//     idea: "The page's central idea.",          // optional, shown as a quote
//     handlers: [{ selector: "#my-activity", md: el => "Markdown" }],
//     next: { text: "Next LilyPad", href: "../next/index.html" }  // optional
//   });
//
// The summary walks the page in order and writes:
//   - activity headings (h2) and sub-activity headings (h3, only if something follows);
//   - every "Key takeaway" (the paragraph or quote after an h3/h4 with that title);
//   - every text box (textarea), under its label;
//   - every single-choice group (role="group" with buttons carrying data-verdict):
//     the learner's choice and its verdict;
//   - whatever the page's own handlers return, for page-specific activities.
// Everything is built in the browser; nothing is sent anywhere.

(function () {
  // ---------- HTML to Markdown (only what our pages use) ----------

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
        case "SUMMARY": case "BUTTON": case "SCRIPT": case "STYLE": break;
        default: if (el.children.length) blocks.push(blockMd(el));
      }
    });
    return blocks.filter(Boolean).join("\n\n");
  }

  // Markdown for a single element, e.g. one card or one hidden answer
  function elementMd(el) {
    const wrap = document.createElement("div");
    wrap.append(el.cloneNode(true));
    return blockMd(wrap);
  }

  // ---------- Built-in pieces ----------

  function choiceMd(group) {
    const btn = group.querySelector('button[aria-pressed="true"]');
    const question = group.getAttribute("aria-label") || "My answer";
    return `**${question}**  \n` +
      (btn ? `My answer: *${btn.textContent.trim()}*. ${btn.dataset.verdict || ""}`.trim() : "*Not answered.*");
  }

  function textMd(box) {
    const label = document.querySelector(`label[for="${box.id}"]`);
    const text = box.value.trim();
    const body = !text ? "*No response entered.*"
      : /-code\b/.test(box.className) ? "```\n" + text + "\n```" : text;
    return `**${label ? label.textContent.trim() : "My answer"}**\n\n${body}`;
  }

  function takeawayMd(heading) {
    const next = heading.nextElementSibling;
    const body = next ? elementMd(next).replace(/^>\s*/gm, "").trim() : "";
    return `> **Key takeaway:** ${body}`;
  }

  // ---------- The summary ----------

  function build(opts) {
    const root = opts.root || document.getElementById("quarto-document-content") ||
      document.querySelector("main") || document.body;
    const handlers = opts.handlers || [];
    const out = [`# ${opts.title}: my response summary`, "",
      `*From [The Pond](${location.href.split("#")[0]}), downloaded on ${new Date().toLocaleDateString()}.*`];
    if (opts.idea) out.push("", `> ${opts.idea}`);
    (opts.intro || []).forEach(md => out.push("", md));

    let pending = null;                         // a sub-heading is written only if something follows it
    const emit = md => {
      if (!md) return;
      if (pending) { out.push("", pending); pending = null; }
      out.push("", md);
    };

    const selectors = ["h2", "h3", "h4", "textarea", "[role=group]"]
      .concat(handlers.map(h => h.selector)).join(", ");
    const handled = [];
    root.querySelectorAll(selectors).forEach(el => {
      if (handled.some(h => h.contains(el))) return;     // already covered by a page handler
      if (el.closest(".card")) return;                   // reference cards, not learner answers
      const handler = handlers.find(h => el.matches(h.selector));
      if (handler) { handled.push(el); emit(handler.md(el)); return; }

      if (/^H[234]$/.test(el.tagName)) {
        const title = el.textContent.trim();
        if (title === "Key takeaway") emit(takeawayMd(el));
        else if (el.tagName === "H2") { pending = null; out.push("", `## ${title}`); }
        else if (el.tagName === "H3") pending = `### ${title}`;
      } else if (el.tagName === "TEXTAREA") {
        emit(textMd(el));
      } else if (el.querySelector("button[data-verdict]")) {
        emit(choiceMd(el));
      }
    });

    if (opts.next) {
      out.push("", "---", "", `Next: [${opts.next.text}](${new URL(opts.next.href, location.href).href}).`);
    }
    out.push("");
    return out.join("\n");
  }

  function download(text, filename) {
    const a = document.createElement("a");
    a.href = "data:text/markdown;charset=utf-8," + encodeURIComponent(text);
    a.download = filename;
    document.body.append(a);
    a.click();
    a.remove();
  }

  function attach(opts) {
    opts.button.addEventListener("click", () => download(build(opts), opts.filename));
  }

  window.PondSummary = { inlineMd, blockMd, elementMd, build, download, attach };
})();
