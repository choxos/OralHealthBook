-- Map the book's custom divs and spans onto LaTeX environments.
--
-- Pandoc's LaTeX writer ignores unknown div classes, so `::: {.verdict}`
-- was rendering as a bare definition list in both PDF editions: the
-- tcolorbox environments in preamble.tex were defined and never used.
-- HTML needs none of this, the SCSS already styles the same classes.

if not FORMAT:match("latex") then return {} end

-- The certainty ratings are colour-coded on the web. Print is greyscale,
-- so carry them as small caps, which survives desaturation.
function Span(el)
  if el.classes:includes("certainty") then
    return {
      pandoc.RawInline("latex", "\\textsc{"),
      table.unpack(el.content),
      pandoc.RawInline("latex", "}"),
    }
  end
  if el.classes:includes("strength") then
    return {
      pandoc.RawInline("latex", "\\textbf{"),
      table.unpack(el.content),
      pandoc.RawInline("latex", "}"),
    }
  end
  -- tcolorbox supplies the box title, so drop the inline one.
  if el.classes:includes("verdict-title") then
    return {}
  end
end

function Div(el)
  if el.classes:includes("verdict") then
    -- Strip the now-empty paragraph the verdict-title span left behind.
    local body = {}
    for _, blk in ipairs(el.content) do
      local empty = blk.t == "Para" and #blk.content == 0
      if not empty then table.insert(body, blk) end
    end
    return {
      pandoc.RawBlock("latex", "\\begin{verdictbox}"),
      table.unpack(body),
      pandoc.RawBlock("latex", "\\end{verdictbox}"),
    }
  end
end
