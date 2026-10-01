# Notebook workflow tracing — The Pond

## Install

Copy the contents of this folder into a new lesson folder, for example:
`lilypads/workflow/tracing-a-workflow/`

Keep `index.qmd` and the `activities` folder together. Run your normal Quarto
preview from The Pond project and open this lesson. Add a landing-page card separately
when you are ready to publish it.

The page inherits your site's theme. It uses Quarto's four scenario tabs. Each tab
embeds one isolated notebook/canvas activity so its styles and selections do not
interfere with Quarto or another scenario. Full-tab links provide more working space.

## Included

- index.qmd — lesson text, native Quarto tabs, and embedding layout.
- activities/hydrology.html
- activities/seismology.html
- activities/oceanography.html
- activities/geophysics.html

Each HTML file includes the uploaded notebook's narrative, code, saved outputs,
reference PNG, CSS, and JavaScript. No Python execution, account, database, or
external JavaScript service is required. The repeated FROGS logo is omitted inside
these embedded views, allowing the surrounding site to provide branding.

Keep your original notebooks as the editable scientific source. These HTML views
are snapshots, not live links to the .ipynb files. Update them when notebook content
changes. The uploaded notebook files themselves were not changed.

## Learner work

Each scenario has its own browser-save key, including a notebook revision identifier.
Downloads are JSON containing node names/types, source quotations, positions, and
connections. Restore checks the scenario and revision. Saving is local to the browser;
there is no instructor submission service. The new revision keys deliberately avoid
loading source selections made in an older notebook version.

The activity has no automatic grading. Learners compare with the collapsed reference.
Selections stay within a notebook cell or output block. Figure images are visible,
but cannot themselves be selected as text; select their description or plotting code.

## Local check

1. Select text in each scenario and create two named boxes.
2. Connect them, move a box, and use Source to return to its passage.
3. Switch tabs and verify each canvas is separate.
4. Download a scenario, clear that canvas, and restore its download.
5. Expand the reference sketch and inspect the notebook's output figure.

This package received static HTML and JavaScript checks. A full Quarto/browser
render was not available in the build environment. The Hydrology prototype interaction
was previously tested successfully by the user; the four-scenario integration needs
this local preview check.
