-- Breadcrumbs and previous/next links for The Pond (issue #86).
--
-- The site tree lives under `pond-nav` in _navigation.yml. It is read here
-- rather than through _quarto.yml, because Quarto rewrites any metadata value
-- that looks like a file path (even a label such as "LilyPads"). For every page listed
-- there, this filter adds
--   * a breadcrumb trail at the top: Home › LilyPads › Data › 2. Metadata
--   * a pager at the bottom: previous page, the parent overview, next page.
-- Pages not listed in the tree (and the home page) are left untouched.
-- The links are plain Markdown links, so they work without JavaScript and
-- Quarto turns the .qmd targets into .html.

local stringify = pandoc.utils.stringify

local HOME = { text = "Home", href = "index.qmd" }

-- Path from the folder `from_dir` to `to`, both relative to the project root.
local function relpath(from_dir, to)
  local a, b = {}, {}
  for s in from_dir:gmatch("[^/]+") do a[#a + 1] = s end
  for s in to:gmatch("[^/]+") do b[#b + 1] = s end
  local i = 1
  while i <= #a and i < #b and a[i] == b[i] do i = i + 1 end
  local parts = {}
  for _ = i, #a do parts[#parts + 1] = ".." end
  for j = i, #b do parts[#parts + 1] = b[j] end
  return table.concat(parts, "/")
end

-- Collapse "." and ".." in a '/'-separated path.
local function normalize(path)
  local parts = {}
  for s in path:gmatch("[^/]+") do
    if s == ".." and #parts > 0 and parts[#parts] ~= ".." then
      table.remove(parts)
    elseif s ~= "." then
      parts[#parts + 1] = s
    end
  end
  return table.concat(parts, "/")
end

-- Flatten the tree into href -> { node, ancestors, siblings, index }.
local function index_tree(list, ancestors, out)
  local siblings = {}
  for _, item in ipairs(list) do
    siblings[#siblings + 1] = {
      text = stringify(item.text),
      href = normalize(stringify(item.href)),
      pages = item.pages,
    }
  end
  for i, node in ipairs(siblings) do
    out[node.href] = { node = node, ancestors = ancestors, siblings = siblings, index = i }
    if node.pages then
      local next_ancestors = { table.unpack(ancestors) }
      next_ancestors[#next_ancestors + 1] = node
      index_tree(node.pages, next_ancestors, out)
    end
  end
  return out
end

local function project_root()
  local root = quarto.project.directory
  if not root then return nil end
  return (root:gsub("\\", "/"):gsub("/$", ""))
end

-- The page being rendered, relative to the project root.
local function current_page(root)
  local input = quarto.doc.input_file
  if not input then return nil end
  input = input:gsub("\\", "/")
  if input:sub(1, #root + 1) ~= root .. "/" then return nil end
  return input:sub(#root + 2)
end

-- Read the site map from _navigation.yml (parsed as a YAML metadata block).
local function read_tree(root)
  local f = io.open(root .. "/_navigation.yml", "r")
  if not f then return nil end
  local yaml = f:read("a")
  f:close()
  return pandoc.read("---\n" .. yaml .. "\n---\n", "markdown").meta["pond-nav"]
end

function Pandoc(doc)
  if not quarto.doc.is_format("html") then return nil end
  local root = project_root()
  if not root then return nil end
  local page = current_page(root)
  local tree = read_tree(root)
  if not tree or not page then return nil end

  local dir = page:match("^(.*)/[^/]*$") or ""
  local entry = index_tree(tree, { HOME }, {})[page]
  if not entry then return nil end
  local function link(item, content, classes)
    return pandoc.Link(content or item.text, relpath(dir, item.href), "",
      pandoc.Attr("", classes or {}))
  end

  -- Breadcrumb trail
  local crumbs = {}
  for _, a in ipairs(entry.ancestors) do
    crumbs[#crumbs + 1] = link(a)
    crumbs[#crumbs + 1] = pandoc.Span(" › ", pandoc.Attr("", { "pond-crumb-sep" }, { ["aria-hidden"] = "true" }))
  end
  crumbs[#crumbs + 1] = pandoc.Span(entry.node.text, pandoc.Attr("", {}, { ["aria-current"] = "page" }))
  local breadcrumbs = pandoc.Div({ pandoc.Plain(crumbs) },
    pandoc.Attr("", { "pond-breadcrumbs" }, { role = "navigation", ["aria-label"] = "Breadcrumb" }))

  -- Pager: a prominent "Onto the next part" card (issue #88), then small
  -- links to the previous page and the parent overview. On the last page of
  -- a section, the card leads back to the overview instead.
  local parent = entry.ancestors[#entry.ancestors]
  local prev = entry.siblings[entry.index - 1]
  local nxt = entry.siblings[entry.index + 1]
  local up_label = parent == HOME and "Home" or (parent.text .. " overview")

  local function card(item, kicker, title, arrow)
    return link(item, {
      pandoc.Span(kicker, pandoc.Attr("", { "pond-next-kicker" })),
      pandoc.Span(title, pandoc.Attr("", { "pond-next-title" })),
      pandoc.Span(arrow, pandoc.Attr("", { "pond-next-arrow" }, { ["aria-hidden"] = "true" })),
    }, { "pond-next-card" })
  end
  local next_card
  if nxt then
    next_card = card(nxt, "Onto the next part", nxt.text, "→")
  elseif parent == HOME then
    next_card = card(HOME, "You've reached the end", "Back to Home", "↑")
  else
    next_card = card(parent, "You've reached the end of this section", "Back to the " .. up_label, "↑")
  end

  local small = {}
  if prev then small[#small + 1] = link(prev, "← " .. prev.text) end
  if nxt then
    if #small > 0 then
      small[#small + 1] = pandoc.Span(" | ", pandoc.Attr("", { "pond-pager-sep" }, { ["aria-hidden"] = "true" }))
    end
    small[#small + 1] = link(parent, "↑ " .. up_label)
  end

  local pager_blocks = { pandoc.Plain({ next_card }) }
  if #small > 0 then
    pager_blocks[#pager_blocks + 1] = pandoc.Div({ pandoc.Plain(small) }, pandoc.Attr("", { "pond-pager-links" }))
  end
  local pager = pandoc.Div(pager_blocks,
    pandoc.Attr("pond-pager", { "pond-pager" }, { role = "navigation", ["aria-label"] = "Pages in this section" }))

  table.insert(doc.blocks, 1, breadcrumbs)
  doc.blocks:insert(pager)
  return doc
end
