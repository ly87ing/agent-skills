#!/usr/bin/env python3
"""Report reader-level defects in the default-visible text of an HTML or Markdown artifact.

Only what a reader sees without clicking is analysed: <details> bodies (their
<summary> stays), <script>, <style>, <template>, elements marked hidden, and
Markdown code fences are skipped. SVG <text> counts as figure text.

The report lists, in order: the heading outline; the opening text and how much
text precedes the first figure or table; paragraphs and table cells over a length
limit; table columns whose values barely vary; numbers and long text runs that
recur across blocks; and code-like terms with where they first appear. It does not
render the page, so the real first screen still needs a browser capture, and it
cannot judge whether a heading states a claim or a term is defined — it lists
where to look.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path

SKIP_TAGS = {"script", "style", "template", "noscript", "head", "nav", "button"}
BOUNDARY_TAGS = {"div", "section", "article", "header", "footer", "main", "figure", "aside", "ul", "ol"}
BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "figcaption", "summary", "dd", "dt", "pre"}
FIGURE_TAGS = {"svg", "img", "figure", "table", "video", "canvas"}
VOID_TAGS = {"br", "img", "hr", "meta", "link", "input", "source", "wbr", "col", "area", "base", "embed", "param", "track"}
NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?\s*(?:%|ms|s|px|KB|MB|GB|秒|分钟|小时|天|份|条|个|项|行|次|处|倍)?")
CODE_LIKE = re.compile(r"\b(?:[A-Za-z]+[_.][\w.]+|[a-z]+[A-Z]\w*|[A-Z][a-z]+[A-Z]\w*|[A-Z]{3,}\w*|[a-z]+-[a-z][\w-]*)\b")
STRIP = re.compile(r"[\s\W_]+", re.UNICODE)


def width(text: str) -> float:
    """Reading length in CJK-character units: an ASCII character counts half."""
    return sum(0.5 if ord(ch) < 128 else 1 for ch in text if not ch.isspace())


def is_term(span: str) -> bool:
    """A code span worth listing: short, mostly ASCII, at least two word characters."""
    ascii_share = sum(ord(ch) < 128 for ch in span) / max(len(span), 1)
    return len(span) <= 40 and ascii_share >= 0.8 and len(re.findall(r"[A-Za-z0-9_]", span)) >= 2


class Block:
    def __init__(self, kind: str, text: str, level: int = 0):
        self.kind, self.text, self.level = kind, re.sub(r"\s+", " ", text).strip(), level


class Doc:
    def __init__(self):
        self.blocks: list[Block] = []
        self.tables: list[list[list[str]]] = []
        self.first_figure_at: float | None = None
        self.text_before_figure = 0.0
        self.code_spans: list[str] = []

    def add(self, block: Block) -> None:
        if not block.text:
            return
        self.blocks.append(block)
        if self.first_figure_at is None and block.kind != "figure":
            self.text_before_figure += width(block.text)

    def mark_figure(self) -> None:
        if self.first_figure_at is None:
            self.first_figure_at = self.text_before_figure


class HtmlReader(HTMLParser):
    def __init__(self, doc: Doc):
        super().__init__(convert_charrefs=True)
        self.doc = doc
        self.stack: list[str] = []
        self.skip_depth = 0
        self.details_depth = 0
        self.in_summary = 0
        self.buffer: list[str] = []
        self.block_tag: str | None = None
        self.table: list[list[str]] | None = None
        self.row: list[str] | None = None
        self.cell: list[str] | None = None
        self.svg_depth = 0
        self.svg_text: list[str] = []
        self.code: list[str] | None = None

    def hidden(self) -> bool:
        return self.skip_depth > 0 or (self.details_depth > 0 and self.in_summary == 0)

    def flush(self) -> None:
        if self.block_tag and self.buffer:
            level = int(self.block_tag[1]) if re.fullmatch(r"h[1-6]", self.block_tag) else 0
            kind = "heading" if level else ("summary" if self.block_tag == "summary" else "para")
            self.doc.add(Block(kind, "".join(self.buffer), level))
        self.buffer, self.block_tag = [], None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag not in VOID_TAGS:
            self.stack.append(tag)
        if self.skip_depth or tag in SKIP_TAGS or "hidden" in attrs or attrs.get("aria-hidden") == "true" and tag != "svg":
            if tag not in VOID_TAGS:
                self.skip_depth += 1
            return
        if tag == "details":
            if self.details_depth == 0 and self.in_summary == 0:
                self.flush()
            self.details_depth += 1
            return
        if tag == "summary" and self.details_depth == 1:
            self.flush()
            self.in_summary += 1
            self.block_tag = "summary"
            return
        if self.hidden():
            return
        if tag in FIGURE_TAGS:
            self.doc.mark_figure()
        if tag == "svg":
            self.flush()
            self.svg_depth += 1
        elif tag == "table":
            self.flush()
            self.table = []
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag == "code":
            self.code = []
        elif tag in BLOCK_TAGS and self.svg_depth == 0 and self.cell is None:
            self.flush()
            self.block_tag = tag
        elif tag == "br" and self.cell is None:
            self.buffer.append(" ")
        elif tag in BOUNDARY_TAGS and self.cell is None and self.svg_depth == 0:
            self.flush()

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        while self.stack and self.stack[-1] != tag:
            self.stack.pop()
        if self.stack:
            self.stack.pop()
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "summary" and self.in_summary:
            self.flush()
            self.in_summary -= 1
            return
        if tag == "details" and self.details_depth:
            self.details_depth -= 1
            return
        if self.hidden():
            return
        if tag == "svg" and self.svg_depth:
            self.svg_depth -= 1
            if self.svg_depth == 0 and self.svg_text:
                self.doc.add(Block("figure", " / ".join(self.svg_text)))
                self.svg_text = []
        elif tag in ("td", "th") and self.cell is not None and self.row is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None and self.table is not None:
            if self.row:
                self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            if self.table:
                self.doc.tables.append(self.table)
                for row in self.table:
                    for value in row:
                        self.doc.add(Block("cell", value))
            self.table = None
        elif tag == "code" and self.code is not None:
            span = "".join(self.code).strip()
            if is_term(span):
                self.doc.code_spans.append(span)
            self.code = None
        elif tag == self.block_tag or (tag in BOUNDARY_TAGS and self.cell is None and self.svg_depth == 0):
            self.flush()

    def handle_data(self, data):
        if self.hidden():
            return
        if self.code is not None:
            self.code.append(data)
        if self.svg_depth:
            if data.strip() and self.stack and self.stack[-1] in ("text", "tspan", "title"):
                self.svg_text.append(data.strip())
            return
        if self.cell is not None:
            self.cell.append(data)
        elif self.block_tag:
            self.buffer.append(data)
        elif data.strip():
            self.block_tag = "p"
            self.buffer.append(data)

    def close(self):
        super().close()
        self.flush()


def read_markdown(text: str, doc: Doc) -> None:
    text = re.sub(r"<details\b.*?</details>", "", text, flags=re.S | re.I)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines, in_fence, para, table = text.splitlines(), False, [], []

    def end_para():
        if para:
            doc.add(Block("para", " ".join(para)))
            para.clear()

    def end_table():
        if table:
            rows = [r for r in table if not re.fullmatch(r"\|?[\s:|-]+\|?", r)]
            parsed = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            doc.tables.append(parsed)
            for row in parsed:
                for value in row:
                    doc.add(Block("cell", value))
            table.clear()

    for line in lines:
        if line.lstrip().startswith(("```", "~~~")):
            end_para(); end_table()
            if not in_fence and line.strip().startswith("```mermaid"):
                doc.mark_figure()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if stripped.startswith("|"):
            end_para(); table.append(stripped)
            continue
        end_table()
        heading = re.match(r"(#{1,6})\s+(.*)", stripped)
        if heading:
            end_para(); doc.add(Block("heading", heading.group(2), len(heading.group(1))))
        elif re.match(r"!\[", stripped):
            end_para(); doc.mark_figure()
        elif re.match(r"([-*+]|\d+\.)\s+", stripped):
            end_para(); doc.add(Block("para", re.sub(r"^([-*+]|\d+\.)\s+", "", stripped)))
        elif not stripped:
            end_para()
        else:
            para.append(stripped)
    end_para(); end_table()
    doc.code_spans.extend(m.group(1) for m in re.finditer(r"`([^`\n]+)`", text) if is_term(m.group(1)))


def parse(path: Path) -> Doc:
    doc = Doc()
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".md", ".markdown"):
        read_markdown(text, doc)
    else:
        reader = HtmlReader(doc)
        reader.feed(text)
        reader.close()
    return doc


def near_constant_columns(table: list[list[str]], min_rows: int) -> list[tuple[str, str, int, int]]:
    if len(table) < min_rows + 1:
        return []
    header, body = table[0], table[1:]
    found = []
    for index, name in enumerate(header):
        values = [row[index] for row in body if index < len(row) and row[index]]
        if len(values) < min_rows:
            continue
        value, count = Counter(values).most_common(1)[0]
        if count / len(values) >= 0.8:
            found.append((name, value, count, len(values)))
    return found


def shared_runs(blocks: list[Block], min_len: int, limit: int) -> list[tuple[str, int]]:
    """Long text runs appearing in two or more blocks, longest first."""
    flat = [(i, STRIP.sub("", b.text)) for i, b in enumerate(blocks) if b.kind != "heading"]
    flat = [(i, t) for i, t in flat if len(t) >= min_len]
    runs: dict[str, set[int]] = defaultdict(set)
    for a in range(len(flat)):
        for b in range(a + 1, len(flat)):
            (ia, ta), (ib, tb) = flat[a], flat[b]
            match = SequenceMatcher(None, ta, tb, autojunk=False).find_longest_match(0, len(ta), 0, len(tb))
            if match.size >= min_len:
                runs[ta[match.a:match.a + match.size]].update((ia, ib))
    kept: list[tuple[str, int]] = []
    for run in sorted(runs, key=len, reverse=True):
        if not any(run in longer for longer, _ in kept):
            kept.append((run, len(runs[run])))
    return kept[:limit]


def analyse(doc: Doc, para_limit: int, cell_limit: int, opening: int, min_run: int) -> dict:
    visible = [b for b in doc.blocks]
    opening_text, total = [], 0.0
    for block in visible:
        if total >= opening:
            break
        opening_text.append(f"[{block.kind}] {block.text}")
        total += width(block.text)
    numbers = Counter()
    for block in visible:
        if block.kind == "heading":
            continue
        for match in NUMBER.finditer(block.text):
            token = re.sub(r"\s+", "", match.group(0))
            if len(re.sub(r"\D", "", token)) >= 2 or not token.isdigit():
                numbers[token] += 1
    terms: dict[str, list[int]] = {}
    for index, block in enumerate(visible):
        found = set(CODE_LIKE.findall(block.text)) | {s for s in doc.code_spans if s in block.text}
        for term in found:
            terms.setdefault(term, []).append(index)
    return {
        "outline": [("  " * (b.level - 1)) + b.text for b in visible if b.kind == "heading"],
        "opening": opening_text,
        "text_before_first_figure": None if doc.first_figure_at is None else round(doc.first_figure_at),
        "long_paragraphs": [(round(width(b.text)), b.text[:40]) for b in visible if b.kind in ("para", "summary") and width(b.text) > para_limit],
        "long_cells": [(round(width(b.text)), b.text[:40]) for b in visible if b.kind == "cell" and width(b.text) > cell_limit],
        "near_constant_columns": [c for t in doc.tables for c in near_constant_columns(t, 4)],
        "repeated_numbers": sorted(((n, c) for n, c in numbers.items() if c >= 2), key=lambda x: -x[1]),
        "shared_runs": shared_runs(visible, min_run, 15),
        "terms": sorted(((t, len(ix), ix[0]) for t, ix in terms.items()), key=lambda x: x[2])[:40],
        "blocks": len(visible),
    }


def render(result: dict, limits: dict) -> str:
    out = [f"Default-visible blocks: {result['blocks']} (folded, hidden, script, and code content excluded)", ""]
    out.append("Outline — does each heading state its section's point?")
    out += [f"  {h}" for h in result["outline"]] or ["  (no headings)"]
    out.append("")
    out.append(f"Opening, first ~{limits['opening']} characters — is the conclusion here?")
    out += [f"  {line[:120]}" for line in result["opening"]]
    tbf = result["text_before_first_figure"]
    out.append(f"  Text before the first figure or table: {'no figure' if tbf is None else f'{tbf} characters'}")
    out.append("  (Not rendered: capture the real first screen in a browser.)")
    sections = [
        (f"Paragraphs over {limits['para']} characters", result["long_paragraphs"], lambda x: f"{x[0]:>4}  {x[1]}…"),
        (f"Table cells over {limits['cell']} characters", result["long_cells"], lambda x: f"{x[0]:>4}  {x[1]}…"),
        ("Columns whose values barely vary (drop or fold into a heading)", result["near_constant_columns"], lambda x: f"'{x[0]}': '{x[1]}' in {x[2]} of {x[3]} rows"),
        ("Numbers stated more than once — each needs a reason", result["repeated_numbers"], lambda x: f"{x[1]}×  {x[0]}"),
        (f"Text runs of {limits['run']}+ characters shared by blocks — the same point said again?", result["shared_runs"], lambda x: f"{x[1]} blocks  {x[0][:60]}"),
        ("Code-like terms by first appearance — is each defined before or where it is first used?", result["terms"], lambda x: f"block {x[2]:>3}, {x[1]}×  {x[0]}"),
    ]
    for title, items, fmt in sections:
        out.append("")
        out.append(f"{title}: {len(items)}")
        out += [f"  {fmt(item)}" for item in items]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", type=Path)
    parser.add_argument("--para-limit", type=int, default=100, help="paragraph length limit in CJK characters (ASCII counts half)")
    parser.add_argument("--cell-limit", type=int, default=40)
    parser.add_argument("--opening", type=int, default=200, help="characters shown as the opening")
    parser.add_argument("--min-run", type=int, default=14, help="shortest shared text run reported")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.path.is_file():
        print(f"not a file: {args.path}", file=sys.stderr)
        return 2
    result = analyse(parse(args.path), args.para_limit, args.cell_limit, args.opening, args.min_run)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result, {"para": args.para_limit, "cell": args.cell_limit, "opening": args.opening, "run": args.min_run}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
