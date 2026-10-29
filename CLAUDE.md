# ThePond — guidance for Claude

ThePond is a Quarto website for asynchronous teaching of open and reproducible science. Learners come from many fields and may know no programming.

## Make every activity as interactive as possible

Learners should *do* something on every page, not only read. Prefer active formats over long tables or lists of facts.

- **Ask before you tell.** Have learners recall or guess first (type a definition, pick an option, sketch a workflow), then reveal the reference answer so they can compare it with their own.
- **Let learners choose.** Offer a set of items (e.g. a word cloud) and let learners pick which ones to engage with, rather than walking through everything in order.
- **Make the effort optional where it makes sense.** For unfamiliar material, let learners skip straight to the answer.
- **Break up long content.** If a table or list would run longer than a screen, turn it into cards, flip cards, tabs, or reveal-on-click elements.
- **Keep reference content editable as Markdown.** Put the answers in Quarto divs in the `.qmd` so authors can edit text and links without touching JavaScript, and let the script build the interactive parts from them. Without JavaScript, the content should still be readable.
- **Stay a static site.** Use plain inline `<script>` blocks and shared styles in `styles.css`, like the existing pages. Keep learner answers in the browser only (`localStorage`, wrapped in `try/catch`); nothing is sent anywhere.
- **Accessible by default.** Use real buttons and form labels, keep everything keyboard-operable, and respect `prefers-reduced-motion`.

Existing examples: `shallows/what-is-open-science.qmd` (word cloud + flip cards), `lilypads/workflow/sketching-workflows/index.qmd` (sketch, then show the answer), `deep-water/github/index.qmd` (filterable cards).
