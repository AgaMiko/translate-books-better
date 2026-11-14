# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1"]
# ///
"""Helper for the translate-books-better skill.

Claude does the reading and translating. This script does the parts that
need exact counting: splitting the manuscript, cutting fragments, merging
translated paragraphs into chapter files, checks, and export. It keeps all
state in plain files inside the book folder, so a run can stop and continue.

Run it with uv (installs python-docx for .docx input on the fly):

    uv run scripts/mneme.py <command> [args]

or with plain Python 3.10+ (python-docx is needed only to read .docx).

Any source and target language; fiction or non-fiction. Language facts
(letters, chapter words, pronouns, dialogue style) are in LANGUAGES below;
a language that is not listed still works, with fewer checks.

Commands (run in the book folder, or pass --dir):

    prepare <manuscript> --source-language pl --target-language en
            [--genre fiction|nonfiction] [--chapter-level N] [--title T]
            [--target-title T] [--letters L] [--force]
        Split a .docx, .md or .txt manuscript into source/chapter-NN.md
        and plan fragments of about 1,200 words. Writes mneme.json. Text
        before the first chapter heading goes to source/front-matter.md.
        Non-fiction keeps section headings inside chapters.
    status                      Steps, fragments done, next fragment.
    mark <step> <state>         Record a step state, e.g. "mark glossary reviewed".
    dialogue [chapters] [--skeleton | --group]
                                Paragraphs that look like dialogue, with ids.
                                --skeleton writes work/lines-draft.md to fill in;
                                --group turns it into work/lines.md per speaker,
                                with counts of short lines, ! ? and ….
    inner [chapters]            Italic thoughts and narration questions per
                                chapter, with counts: the inner voice of a
                                point-of-view character, or the author's.
    terms <chapter>             Glossary terms found in a chapter (source side).
    fragment <id>               One fragment with its neighbours, the glossary
                                terms and voice files that apply to it.
    save <id> <file>            Check a translated fragment (same ids, same
                                order) and merge it into translation/chapter-NN.md.
    letters <chapter> <first> <last> [--translation] [--from WORDS] [--to WORDS]
                                First letters of sentences, lines, paragraphs
                                and words of a passage, for hidden messages.
    check [chapters]            Write check-report.md: missing paragraphs,
                                leftover source letters, dialogue marks,
                                placeholders, footnotes, links, numbers
                                (non-fiction), glossary use, style metrics.
                                Merges notes/chapter-NN.md into notes.md.
    export [--draft] [--chapters 1-2] [--title T]
                                Write export/<title>.md (and .docx / .epub
                                when pandoc is installed).

Chapters are given as 3, 1-4 or 1,3,5-6.

The rules and numbers mirror the Mneme app (github.com/AgaMiko/mneme-book-translator:
backend/app/services/fragmenter.py,
translation_qa.py, constants/languages.py, manuscript_parser.py).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

# ─── Numbers and language facts copied from the app ─────────────────────

TARGET_WORDS = 1200  # fragmenter.TARGET_WORDS
MIN_WORDS_BEFORE_SCENE_CUT = 600
MIN_TAIL_WORDS = 400  # the app uses 250; 400 avoids tiny last fragments
NEIGHBOUR_PARAGRAPHS = 2  # paragraphs of context on each side of a fragment

# Facts per language, by ISO code. All fields are optional.
#   letters   letters (or a regex class range) that belong to this language and should
#             not be left in a translation into another language;
#   chapter   regex for the chapter word; prologue/epilogue words; heading = export word;
#   pronouns  third-person subject pronouns that open sentences (She/He in English).
#             Empty for languages that usually drop the subject (pro_drop);
#   dialogue  "quotes" or "dash": how the language marks speech in fiction.
LANGUAGES: dict[str, dict] = {
    "en": {"name": "English", "chapter": r"chapter", "pro": ["prologue", "epilogue"], "heading": "Chapter",
           "pronouns": ["She", "He"], "dialogue": "quotes"},
    "pl": {"name": "Polish", "letters": "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "chapter": r"rozdzia[łl]",
           "pro": ["prolog", "epilog"], "heading": "Rozdział", "pro_drop": True, "dialogue": "dash"},
    "de": {"name": "German", "letters": "äöüßÄÖÜ", "chapter": r"kapitel", "pro": ["prolog", "epilog"],
           "heading": "Kapitel", "pronouns": ["Sie", "Er"], "dialogue": "quotes"},
    "fr": {"name": "French", "letters": "àâæçéèêëîïôœùûüÿÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸ", "chapter": r"chapitre",
           "pro": ["prologue", "épilogue"], "heading": "Chapitre", "pronouns": ["Elle", "Il"], "dialogue": "dash"},
    "es": {"name": "Spanish", "letters": "áéíñóúü¿¡ÁÉÍÑÓÚÜ", "chapter": r"cap[ií]tulo",
           "pro": ["prólogo", "epílogo"], "heading": "Capítulo", "pro_drop": True, "dialogue": "dash"},
    "it": {"name": "Italian", "letters": "àèéìíòóùÀÈÉÌÍÒÓÙ", "chapter": r"capitolo", "pro": ["prologo", "epilogo"],
           "heading": "Capitolo", "pro_drop": True, "dialogue": "quotes"},
    "pt": {"name": "Portuguese", "letters": "ãõáâàçéêíóôúÃÕÁÂÀÇÉÊÍÓÔÚ", "chapter": r"cap[ií]tulo",
           "pro": ["prólogo", "epílogo"], "heading": "Capítulo", "pro_drop": True, "dialogue": "dash"},
    "nl": {"name": "Dutch", "chapter": r"hoofdstuk", "pro": ["proloog", "epiloog"], "heading": "Hoofdstuk",
           "pronouns": ["Ze", "Zij", "Hij"], "dialogue": "quotes"},
    "sv": {"name": "Swedish", "letters": "åäöÅÄÖ", "chapter": r"kapitel", "pro": ["prolog", "epilog"],
           "heading": "Kapitel", "pronouns": ["Hon", "Han"], "dialogue": "dash"},
    "cs": {"name": "Czech", "letters": "áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ", "chapter": r"kapitola",
           "pro": ["prolog", "epilog"], "heading": "Kapitola", "pro_drop": True, "dialogue": "quotes"},
    "sk": {"name": "Slovak", "letters": "áäčďéíĺľňóôŕšťúýžÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽ", "chapter": r"kapitola",
           "pro": ["prológ", "epilóg"], "heading": "Kapitola", "pro_drop": True, "dialogue": "quotes"},
    "hu": {"name": "Hungarian", "letters": "áéíóöőúüűÁÉÍÓÖŐÚÜŰ", "chapter": r"fejezet",
           "pro": ["prológus", "epilógus"], "heading": "fejezet", "pro_drop": True, "dialogue": "dash"},
    "ru": {"name": "Russian", "letters": "\u0400-\u04ff", "chapter": r"глава", "pro": ["пролог", "эпилог"],
           "heading": "Глава", "pronouns": ["Она", "Он"], "dialogue": "dash"},
    "uk": {"name": "Ukrainian", "letters": "\u0400-\u04ff", "chapter": r"розділ", "pro": ["пролог", "епілог"],
           "heading": "Розділ", "pronouns": ["Вона", "Він"], "dialogue": "dash"},
    "kn": {"name": "Kannada", "letters": "\u0c80-\u0cff", "chapter": r"ಅಧ್ಯಾಯ", "pro": [], "heading": "ಅಧ್ಯಾಯ",
           "pro_drop": True, "dialogue": "quotes"},
    "ja": {"name": "Japanese", "letters": "\u3040-\u30ff\u4e00-\u9fff", "chapter": r"第\s*[\d一二三四五六七八九十百]+\s*章",
           "pro": ["序章", "終章"], "heading": "第{n}章", "pro_drop": True, "dialogue": "quotes"},
    "zh": {"name": "Chinese", "letters": "\u4e00-\u9fff", "chapter": r"第\s*[\d一二三四五六七八九十百]+\s*章",
           "pro": ["序章", "尾声"], "heading": "第{n}章", "pro_drop": True, "dialogue": "quotes"},
}
ARTICLES = {  # leading articles the glossary check ignores in the target form
    "en": "the|a|an", "de": "der|die|das|den|dem|des", "fr": "le|la|les|l'|l’", "es": "el|la|los|las",
    "it": "il|lo|la|i|gli|le|l'|l’", "pt": "o|a|os|as", "nl": "de|het", "sv": "den|det",
}
LANG_BY_NAME = {v["name"].lower(): k for k, v in LANGUAGES.items()}


def lang_code(value: str) -> str:
    """'pl', 'PL', 'Polish' or 'en-GB' → 'pl' / 'en'. An unknown language keeps its own lower-case name."""
    v = (value or "").strip().lower()
    return LANG_BY_NAME.get(v) or v.split("-")[0].split("_")[0]


def lang(value: str) -> dict:
    return LANGUAGES.get(lang_code(value), {"name": value})


_NUMBER = r"\s+[\divxlcdm\d]+"


def chapter_markers(code: str) -> list[str]:
    info = LANGUAGES.get(code, {})
    out = []
    if info.get("chapter"):
        out.append(info["chapter"] + ("" if info["chapter"].startswith("第") else _NUMBER))
    out += [rf"{re.escape(w)}(?:\s+.*)?$" for w in info.get("pro", [])]
    return out


ALL_CHAPTER_MARKERS = [m for code in LANGUAGES for m in chapter_markers(code)]

# translation_qa.py targets (fiction)
SHE_HE_MAX_PCT = 15.0
ELLIPSES_MAX_PER_1K = 3.0
DASHES_MAX_PER_1K = 6.0
STOCK_PHRASES = (  # English only
    r"the weight of", r"\ba beat\b", r"ghost of a smile", r"a flicker of",
    r"couldn't help but", r"something shifted", r"didn't know (?:she|he) was holding",
    r"let out a breath (?:she|he)", r"a wave of(?! (?:her |his |their |the |a )?hand)", r"for a heartbeat", r"(?:^|(?<=\n)|(?<=[.!?…\"”] ))[*_]?suddenly\b",
)
STOCK_LABEL = {STOCK_PHRASES[-1]: "Suddenly (opening a sentence)"}
PLACEHOLDER = re.compile(r"x{4,}|\[x+\]")

SCENE_BREAK = re.compile(r"^\*\*\*(?: |$)")
SECTION = re.compile(r"^#{2,6} \S")  # a section heading inside a non-fiction chapter
STAR_SPLIT = re.compile(r"(?:^|\s+)(?<!\*)\*{3}(?!\*)(?:\s+|$)")  # "***" standing alone in a paragraph
MD_ESCAPE = re.compile(r"\\([!.\-()\[\]#+>~'\"`=|{}])")  # \! \. and the like; \* and \_ are kept
ID_LINE = re.compile(r"^\[([A-Za-z0-9_-]+)\]\s*$")
DIALOGUE_START = re.compile(r"^\s*[–—-]\s")
# A sentence ends at . ! ? or … (or 。！？), maybe followed by closing quotes or italic marks.
SENTENCE_END = re.compile(r"(?<=[.!?\u2026])[*_\"\u201d\u2019\u00bb)」』]*\s+|(?<=[。！？])[」』）]*\s*")
FOOTNOTE = re.compile(r"\[\^[^\]]+\]|<sup>[^<]+</sup>")
LINK = re.compile(r"https?://\S+|www\.\S+")
# A number: digit groups with one thousands separator before each group of three ("1 000",
# "12,500"), or digits with an optional decimal part ("0,4", "2.7"). A comma followed by a
# space ends the number, so "In 2020, 804 images" holds two numbers.
NUMBER = re.compile(r"(?<![\w.,])(?:\d{1,3}(?:[ ,.\u00a0\u202f]\d{3})+|\d+(?:[.,]\d+)?)(?!\w)")

STATE_FILE = "mneme.json"


# ─── Paragraph files: "[id]" on its own line, then the text ─────────────


def read_paragraphs(path: Path) -> list[tuple[str, str]]:
    """Read a file of "[id]\\ntext" blocks. Text may span lines."""
    if not path.exists():
        return []
    out: list[tuple[str, str]] = []
    pid: str | None = None
    buf: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ID_LINE.match(line)
        if m:
            if pid is not None:
                out.append((pid, "\n".join(buf).strip()))
            pid, buf = m.group(1), []
        elif pid is not None:
            buf.append(line)
    if pid is not None:
        out.append((pid, "\n".join(buf).strip()))
    return out


def write_paragraphs(path: Path, header: str, paras: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n\n".join(f"[{pid}]\n{text}" for pid, text in paras)
    path.write_text(f"{header}\n\n{body}\n", encoding="utf-8")


def render(paras: list[tuple[str, str]]) -> str:
    return "\n\n".join(f"[{pid}]\n{text}" for pid, text in paras)


# ─── State ──────────────────────────────────────────────────────────────


def load_state(root: Path) -> dict:
    path = root / STATE_FILE
    if not path.exists():
        sys.exit(f"No {STATE_FILE} in {root}. Run 'prepare' first.")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(root: Path, state: dict) -> None:
    (root / STATE_FILE).write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def chapter_file(root: Path, n: int, kind: str = "source") -> Path:
    return root / kind / f"chapter-{n:02d}.md"


def find_fragment(state: dict, fid: str) -> dict:
    for f in state["fragments"]:
        if f["id"] == fid:
            return f
    sys.exit(f"No fragment {fid}. Run 'status' to see the ids.")


def translated_ids(root: Path, n: int) -> set[str]:
    return {pid for pid, text in read_paragraphs(chapter_file(root, n, "translation")) if text}


# ─── prepare ────────────────────────────────────────────────────────────


def chapter_pattern(code: str) -> re.Pattern[str]:
    keys = chapter_markers(code) + [k for k in chapter_markers("en") if k not in chapter_markers(code)]
    return re.compile(rf"^\s*({'|'.join(keys)})", re.IGNORECASE)


def docx_blocks(path: Path) -> tuple[str | None, list[tuple[str, str | None]]]:
    """(title, [(text, style)]). Italic and bold runs become *…* and **…**."""
    try:
        from docx import Document
    except ImportError:
        sys.exit("Reading .docx needs python-docx: run with 'uv run' or 'pip install python-docx'.")
    doc = Document(str(path))
    blocks: list[tuple[str, str | None]] = []
    for para in doc.paragraphs:
        parts = []
        for run in para.runs:
            t = run.text
            if not t.strip():
                parts.append(t)
                continue
            lead, core, trail = re.match(r"^(\s*)(.*?)(\s*)$", t, re.S).groups()
            if run.bold:
                core = f"**{core}**"
            elif run.italic:
                core = f"*{core}*"
            parts.append(lead + core + trail)
        # Adjacent runs with the same formatting leave "**" or "* *" seams; join them.
        text = re.sub(r"\*\*\*\*|(?<=\w)\*\*(?=\w)", "", "".join(parts)).strip()
        blocks.append((text, para.style.name if para.style else None))
    return (doc.core_properties.title or None), blocks


def text_blocks(path: Path, levels: int = 2) -> list[tuple[str, str | None]]:
    """Paragraphs of .md/.txt: blank-line separated, or one per line if no blank lines.
    '#' to '#'*levels lines become 'Heading N' blocks (the first '#' line the 'Title');
    deeper heading marks stay in the text (fiction uses '###' for scene breaks)."""
    raw = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    chunks = [c for c in re.split(r"\n\s*\n", raw) if c.strip()]
    if len(chunks) <= 2 and raw.count("\n") > 10:
        chunks = [line for line in raw.split("\n") if line.strip()]
    out: list[tuple[str, str | None]] = []
    for c in chunks:
        c = c.strip()
        if re.fullmatch(r"#+", c):
            continue  # an empty heading line
        m = re.match(r"^(#{1,6})\s+(.*)$", c)
        if m and "\n" not in c and len(m.group(1)) <= levels and not scene_break(c):
            k = len(m.group(1))
            out.append((m.group(2).strip(), "Title" if k == 1 and not out else ("Heading 1" if levels == 2 else f"Heading {k}")))
        else:
            out.append((c, None))
    return out


def plain(text: str) -> str:
    """Text without markdown marks: heading signs, escapes, * and _."""
    return re.sub(r"\s+", " ", re.sub(r"[*_\\]", "", re.sub(r"^\s*#+\s*", "", text))).strip()


def has_chapter_word(text: str, pattern: re.Pattern[str], heading: bool) -> bool:
    """A heading counts as a chapter heading when a chapter word appears anywhere in it
    ("*Ola* **Rozdział 1** …"); a plain paragraph only when it starts with one."""
    p = plain(text)
    if heading:
        return any(pattern.match(p[m.start():]) for m in re.finditer(r"(?<!\w)\w", p))
    return bool(pattern.match(p))


def scene_break(text: str) -> str | None:
    """'***' or '*** Name' when the block is a scene break, else None. Accepts the
    escaped forms of Word-to-Markdown exports: '### **\\*\\*\\***', '### **\\*\\*\\* Ola**'."""
    t = text.strip()
    escaped = t.startswith("#") or "\\*" in t
    if not escaped:
        m = re.fullmatch(r"\*\s*\*\s*\*(?:\s+(\S.*))?", t)
        name = m.group(1) if m else None
        if not m or (name and (name.startswith("*") or len(name.split()) > 3 or re.search(r"[.!?…]", name))):
            return None
    else:
        t = re.sub(r"^#+\s*", "", t).replace("\\", "")
        m = re.fullmatch(r"\*{3,}\s*(.*?)\s*", t)
        if not m:
            return None
        name = m.group(1).strip("* ").strip()
        if name and (len(name.split()) > 3 or re.search(r"[.!?…]", name)):
            return None
    return f"*** {name}" if name else "***"


def split_heading(text: str) -> str:
    """Put each part of a chapter heading on its own line: the POV name, the chapter
    line, each epigraph line and the attribution. Parts are separated by two spaces or
    sit in separate italic/bold runs ('*line one.* *line two.*')."""
    parts = [p.strip() for p in re.split(r"\s{2,}", text.strip()) if p.strip()]
    lines: list[str] = []
    for part in parts:
        lines += [s for s in re.split(r"(?<=[^\s*]\*)\s+(?=\*[^\s*])", part) if s.strip()]
    return "\n".join(lines)


def short_label(title: str) -> str:
    """'chapter 2 (Ola)'-style label: the first line of the heading, without marks."""
    first = plain(split_heading(title).split("\n")[0]) if title else ""
    return first[:40]


def cmd_prepare(root: Path, a: argparse.Namespace) -> None:
    src = Path(a.manuscript).expanduser()
    if not src.exists():
        sys.exit(f"Manuscript not found: {src}")
    if (root / STATE_FILE).exists():
        if not a.force:
            sys.exit(f"{STATE_FILE} already exists. Use --force to split the manuscript again.")
        if any((root / "translation").glob("chapter-*.md")):
            sys.exit("translation/ already has chapter files, and a new split may change paragraph ids. "
                     "Move translation/ aside first if you really want to split again.")
        written = [d for d in ("work", "voices") if any((root / d).glob("*.md"))] \
            + (["notes.md"] if (root / "notes.md").exists() else [])
        if written:
            print(f"Warning: {', '.join(written)} already exist. Paragraph ids may change with the new "
                  "split, so line ids in work/lines.md, voice evidence and notes may point at the "
                  "wrong paragraphs. Compare source/ before and after.")
        for old in (root / "source").glob("chapter-*.md"):
            old.unlink()
    code = lang_code(a.source_language)
    target = lang_code(a.target_language)
    genre = a.genre
    title = a.title
    if src.suffix.lower() == ".docx":
        doc_title, blocks = docx_blocks(src)
        title = title or doc_title
    else:
        blocks = text_blocks(src, levels=6 if genre == "nonfiction" else 2)
    pattern = chapter_pattern(code)
    blocks = [(t, s) for t, s in blocks if t]

    def level(style: str | None) -> int:
        m = re.match(r"heading\s*(\d)", (style or "").lower())
        return int(m.group(1)) if m else 0

    # Non-fiction: chapters are the top heading level that occurs more than once
    # (Heading 1, or Heading 2 when Heading 1 is only the book title); deeper
    # headings stay in the chapter as section headings ('## …'). A single top heading
    # that looks like a chapter ("I", "3", "Rozdział 3") is one chapter, not the book
    # title. --chapter-level overrides the guess.
    chapter_level = a.chapter_level or 1
    if genre == "nonfiction":
        tops = [t for t, st_ in blocks if st_ == "Title" or level(st_) == 1]
        chapter_like = lambda t: bool(re.fullmatch(r"[IVXLCDM]+\.?|\d+\.?", plain(t), re.IGNORECASE)  # noqa: E731
                                      or has_chapter_word(t, pattern, True))
        if not a.chapter_level and len(tops) <= 1 and any(level(st_) == 2 for _, st_ in blocks):
            if tops and chapter_like(tops[0]):
                print(f"One top heading, '{plain(tops[0])}', taken as the only chapter; its '##' headings "
                      "are sections. If it is the book title, run again with --chapter-level 2.")
            elif tops:
                chapter_level = 2
                print(f"'{plain(tops[0])}' taken as the book title and '##' headings as "
                      "chapters. If the file is one chapter, run again with --chapter-level 1.")
            else:
                chapter_level = 2
                print("No top-level ('#') heading found, so '##' headings are taken as chapters. "
                      "If they are sections of one chapter, run again with --chapter-level 1.")
        if chapter_level == 2:
            blocks = [(t, "Title" if level(st_) == 1 else st_) for t, st_ in blocks]
        elif len(tops) <= 1 or (tops and chapter_like(tops[0])):
            blocks = [(t, "Heading 1" if st_ == "Title" else st_) for t, st_ in blocks]

    def is_heading(style: str | None) -> bool:
        s = (style or "").lower()
        return s == "title" or level(style) == chapter_level

    # Text before the first chapter heading (title page, author, dedication) is front matter.
    first_chapter = next((i for i, (t, s) in enumerate(blocks)
                          if level(s) == chapter_level or has_chapter_word(t, pattern, is_heading(s))), None)
    front: list[str] = []
    if first_chapter:
        front = [t for t, _ in blocks[:first_chapter]]
        if blocks[0][1] == "Title":
            title = title or blocks[0][0]
        blocks = blocks[first_chapter:]

    chapters: list[dict] = []
    current: dict = {"title": None, "paras": []}
    for text, style in blocks:
        s = (style or "").lower()
        chapter_word = has_chapter_word(text, pattern, is_heading(style))
        if s == "title" and not chapter_word and not chapters and not current["paras"] and current["title"] is None:
            title = title or text
            continue
        if level(style) == chapter_level or chapter_word:
            if current["paras"] or current["title"] is not None:
                chapters.append(current)
            current = {"title": split_heading(text), "paras": []}
            continue
        if genre == "nonfiction" and level(style) > chapter_level:  # a section heading inside the chapter
            current["paras"].append("#" * (level(style) - chapter_level + 1) + " " + plain(text))
            continue
        if brk := scene_break(text):
            current["paras"].append(brk)
            continue
        text = MD_ESCAPE.sub(r"\1", text)
        parts = STAR_SPLIT.split(text)
        for i, part in enumerate(parts):
            if part.strip():
                current["paras"].append(part.strip())
            if i < len(parts) - 1:
                current["paras"].append("***")
    if current["paras"] or current["title"] is not None:
        chapters.append(current)
    if not chapters:
        sys.exit("No text found in the manuscript.")

    (root / "source").mkdir(parents=True, exist_ok=True)
    if front:
        (root / "source" / "front-matter.md").write_text("\n\n".join(front) + "\n", encoding="utf-8")
    state_chapters, fragments = [], []
    for n, ch in enumerate(chapters, 1):
        paras: list[tuple[str, str]] = []
        if ch["title"]:
            paras.append(("title", ch["title"]))
        paras += [(f"p{i:03d}", t) for i, t in enumerate(ch["paras"], 1)]
        write_paragraphs(chapter_file(root, n), f"<!-- Chapter {n} source. One [id] per paragraph. -->", paras)
        words = sum(len(t.split()) for _, t in paras)
        state_chapters.append({"n": n, "title": ch["title"] or f"Chapter {n}",
                               "label": short_label(ch["title"] or ""), "words": words})
        fragments += plan_fragments(n, paras)

    state = {
        "title": title or src.stem,
        "target_title": a.target_title,
        "manuscript": str(src),
        "genre": genre,
        "source_language": lang(code).get("name", a.source_language),
        "source_language_code": code,
        "source_letters": a.letters if a.letters is not None else lang(code).get("letters", ""),
        "target_language": lang(target).get("name", a.target_language),
        "target_language_code": target,
        "target_variant": a.target_language,
        "steps": {"split": "done", "glossary": "todo", "voices": "todo",
                  "passages": "todo", "translation": "todo", "check": "todo", "export": "todo"},
        "chapters": state_chapters,
        "fragments": fragments,
    }
    save_state(root, state)
    for d in ("translation", "voices", "work", "notes"):
        (root / d).mkdir(exist_ok=True)
    total = sum(c["words"] for c in state_chapters)
    print(f"Split '{state['title']}': {len(state_chapters)} chapters, {total} words, "
          f"{len(fragments)} fragments. State in {root / STATE_FILE}.")
    if front:
        print(f"Front matter before chapter 1 ({sum(len(t.split()) for t in front)} words) "
              "is in source/front-matter.md and is not translated.")
    untitled = [c["n"] for c in state_chapters if not chapters[c["n"] - 1]["title"]]
    if untitled:
        print(f"Chapters without a heading: {untitled}. Check that the split is right.")
    if not state["source_letters"]:
        print(f"Note: no letter list for '{code}'. Pass --letters to enable the leftover-letters check.")
    if code not in LANGUAGES or target not in LANGUAGES:
        unknown = [c for c in (code, target) if c not in LANGUAGES]
        print(f"Note: no language facts for {', '.join(unknown)}: chapter words, pronoun and dialogue "
              "checks are reduced. Add an entry to LANGUAGES in mneme.py for full checks.")


def plan_fragments(n: int, paras: list[tuple[str, str]]) -> list[dict]:
    """Same rules as the app's fragmenter: ~1,200 words, cut early at a scene
    break or a section heading after 600; a tail under MIN_TAIL_WORDS joins the previous fragment."""
    frags: list[dict] = []
    cur: dict | None = None
    for pid, text in paras:
        words = len(text.split())
        if cur and cur["ids"]:
            if cur["words"] >= TARGET_WORDS or ((SCENE_BREAK.match(text) or SECTION.match(text)) and cur["words"] >= MIN_WORDS_BEFORE_SCENE_CUT):
                frags.append(cur)
                cur = None
        if cur is None:
            cur = {"ids": [], "words": 0}
        cur["ids"].append(pid)
        cur["words"] += words
    if cur and cur["ids"]:
        if frags and cur["words"] < MIN_TAIL_WORDS:
            frags[-1]["ids"] += cur["ids"]
            frags[-1]["words"] += cur["words"]
        else:
            frags.append(cur)
    return [{"id": f"{n:02d}-{i}", "chapter": n, "ids": f["ids"], "words": f["words"]}
            for i, f in enumerate(frags, 1)]


# ─── status / mark ──────────────────────────────────────────────────────


def fragment_done(root: Path, f: dict, cache: dict[int, set[str]]) -> bool:
    if f["chapter"] not in cache:
        cache[f["chapter"]] = translated_ids(root, f["chapter"])
    return set(f["ids"]) <= cache[f["chapter"]]


def cmd_status(root: Path, a: argparse.Namespace) -> None:
    st = load_state(root)
    cache: dict[int, set[str]] = {}
    done = [f for f in st["fragments"] if fragment_done(root, f, cache)]
    words_done = sum(f["words"] for f in done)
    words_all = sum(f["words"] for f in st["fragments"])
    print(f"{st['title']} ({st['source_language']} → {st.get('target_variant') or st['target_language']}, "
          f"{st.get('genre', 'fiction')})")
    print("Steps: " + ", ".join(f"{k} {v}" for k, v in st["steps"].items()))
    print(f"Fragments: {len(done)}/{len(st['fragments'])} translated, "
          f"{words_done}/{words_all} words ({100 * words_done // max(words_all, 1)}%)")
    for ch in st["chapters"]:
        frs = [f for f in st["fragments"] if f["chapter"] == ch["n"]]
        k = sum(fragment_done(root, f, cache) for f in frs)
        mark = "✓" if k == len(frs) else f"{k}/{len(frs)}"
        print(f"  {ch['n']:>3}  {mark:>5}  {ch['words']:>6} words  {ch.get('label') or plain(ch['title'])[:60]}")
    nxt = next((f for f in st["fragments"] if not fragment_done(root, f, cache)), None)
    print(f"Next fragment: {nxt['id']}" if nxt else "All fragments translated.")
    if lc := st.get("last_check"):
        print(f"Last check: chapters {', '.join(map(str, lc['chapters']))} on {lc['date']}.")


def cmd_mark(root: Path, a: argparse.Namespace) -> None:
    st = load_state(root)
    st["steps"][a.step] = a.state
    save_state(root, st)
    print(f"{a.step}: {a.state}")


# ─── Glossary ───────────────────────────────────────────────────────────


def load_glossary(root: Path) -> list[dict]:
    """Rows of the glossary.md table, without rejected ones."""
    path = root / "glossary.md"
    if not path.exists():
        return []
    rows, header = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            header = None if not line.strip() else header
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        row = dict(zip(header, cells))
        if row.get("status", "").lower().startswith(("rejected", "removed")):
            continue
        if row.get("source"):
            rows.append(row)
    return rows


def term_forms(row: dict) -> list[str]:
    forms = [row["source"]] + [f.strip() for f in row.get("forms seen", "").split(",")]
    return [f for f in dict.fromkeys(forms) if f and f not in ("—", "-")]


LETTER = r"[^\W_]"  # a letter or digit in any script


def word_pattern(word: str, inflect: bool) -> str:
    """Case endings for inflected languages. A word of 6+ letters may change its last
    letter and take up to 4 more (Polish 'rzekę' for 'rzeka'); a word of 5 letters
    may change its last letter and take up to 2 more ('Marta' → 'Marty', not 'martwy');
    a word of 4 letters may take up to 2 more ('Adam' → 'Adama', not 'adamaszek')."""
    if not inflect or not word[-1:].isalpha() or len(word) < 4:
        return re.escape(word)
    if len(word) >= 6:
        return re.escape(word[:-1]) + f"{LETTER}{{0,4}}"
    if len(word) == 5:
        return re.escape(word[:-1]) + f"{LETTER}{{0,2}}"
    return re.escape(word) + f"{LETTER}{{0,2}}"


def term_regex(row: dict) -> re.Pattern[str]:
    """Match any listed form, each word with case endings (see word_pattern).
    The optional Match column of the glossary turns this off: 'case' matches
    with the case as written, 'exact' matches the forms without endings.
    The app does this more carefully in term_matching.py."""
    mode = row.get("match", "").lower()
    inflect = "exact" not in mode
    alts = []
    for f in sorted(term_forms(row), key=len, reverse=True):
        alts.append(r"\s+".join(word_pattern(w, inflect) for w in f.split()))
    flags = 0 if "case" in mode else re.IGNORECASE
    return re.compile(rf"(?<!{LETTER})(?:{'|'.join(alts)})(?!{LETTER})", flags)


SENTENCE_START = re.compile(r"(?:^|[.!?…:]\s+|[–—-]\s+)[*_(]*$")


def row_spans(row: dict, text: str) -> list[tuple[int, int, bool]]:
    """Where a glossary row's term is in the text: (start, end, opens a sentence).
    'Opens a sentence' is set only for a row with Match 'case': a capitalised form
    that opens a sentence or a line ("Cienie wydłużyły się") says nothing about the term."""
    case = "case" in row.get("match", "").lower()
    spans = []
    for m in term_regex(row).finditer(text):
        initial = False
        if case:
            line_start = text.rfind("\n", 0, m.start()) + 1
            initial = bool(SENTENCE_START.search(text[line_start:m.start()]))
        spans.append((m.start(), m.end(), initial))
    return spans


def term_hits(text: str, glossary: list[dict]) -> tuple[list[dict], list[dict]]:
    """(found, maybe). A match that lies inside a longer term's match does not count
    ('Most' inside 'Kamienny Most'). 'maybe' holds the `case` rows found
    only where they open a sentence, so the translator can decide."""
    spans = {id(r): row_spans(r, text) for r in glossary}
    longer = [(s, e, id(r)) for r in glossary for s, e, _ in spans[id(r)]]
    found, maybe = [], []
    for r in glossary:
        own = [(s, e, ini) for s, e, ini in spans[id(r)]
               if not any(rid != id(r) and s2 <= s and e <= e2 and e2 - s2 > e - s for s2, e2, rid in longer)]
        if any(not ini for _, _, ini in own):
            found.append(r)
        elif own:
            maybe.append(r)
    return found, maybe


def terms_in(text: str, glossary: list[dict]) -> list[dict]:
    return term_hits(text, glossary)[0]


GLOSSARY_COLUMNS = {"source", "forms seen", "type", "alternatives", "notes", "status", "match"}


def target_of(row: dict) -> str:
    """The agreed translation: the 'Target' column (older glossaries: 'English', or a
    column named after the target language)."""
    if row.get("target") or row.get("english"):
        return row.get("target") or row.get("english") or ""
    return next((v for k, v in row.items() if k not in GLOSSARY_COLUMNS and v), "")


def target_forms(row: dict) -> list[str]:
    """The Target column may list several forms: 'bind/bound', or a long name and
    its accepted short form 'Common Redcap/Redcap'. The first is the main one."""
    return [f.strip() for f in target_of(row).split("/") if f.strip()]


def target_regex(row: dict, code: str = "en") -> re.Pattern[str]:
    """What counts as the agreed translation being used: the target form without a
    leading article, each word with the language's endings (English: Stonebridge/Stonebridges,
    bind/binding; other languages: case endings as for the source), or a listed source
    form that is itself written in the translation (a short form the rules keep, such as
    'Mag' for Magdalena)."""
    case = "case" in row.get("match", "").lower()
    article = r"^(?!)"
    if code in ARTICLES:
        words = [w for w in ARTICLES[code].split("|") if not w.endswith(("'", "’"))]
        elided = [w for w in ARTICLES[code].split("|") if w.endswith(("'", "’"))]
        article = rf"^(?:(?:{'|'.join(words)})\s+" + (f"|{'|'.join(elided)}" if elided else "") + ")"
    alts = []
    for form in target_forms(row):
        # With Match 'case', keep the article and its capital out of the comparison but the
        # term's own capitals in it ('the Shadows' must not be 'shadows').
        target = re.sub(article, "", form, flags=re.IGNORECASE)
        words = []
        for w in target.split():
            if code == "en":
                stem = re.sub(r"(?:ers|er|es|s|ing|ed|e|y)$", "", w, flags=re.IGNORECASE) if len(w) > 4 else w
                words.append(re.escape(stem) + r"[\w'’]{0,5}")
            else:
                words.append(word_pattern(w, True))
        alts.append(r"\s+".join(words))
    # A short form the rules keep as it is ('Mag' for Magdalena): a listed form that the
    # target form starts with.
    main = re.sub(article, "", (target_forms(row) or [""])[0], flags=re.IGNORECASE)
    alts += [re.escape(f) for f in term_forms(row)
             if f[:1].isupper() and main.lower().startswith(f.lower()) and f.lower() != main.lower()]
    if not alts:
        return re.compile(r"(?!)")
    return re.compile(rf"(?<!{LETTER})(?:{'|'.join(alts)})", 0 if case else re.IGNORECASE)


def cmd_terms(root: Path, a: argparse.Namespace) -> None:
    glossary = load_glossary(root)
    text = "\n".join(t for _, t in read_paragraphs(chapter_file(root, a.chapter)))
    for r in terms_in(text, glossary):
        print(f"{r['source']} → {target_of(r)}  ({r.get('type', '')})")


# ─── dialogue ───────────────────────────────────────────────────────────


LINE_ENTRY = re.compile(r"^- \[(\d+):(\w+)\]\s*(.*?)\s*(?:→\s*(.*?))?\s*\|")


QUOTED = re.compile(r"[„“\"«»]([^„“”\"«»\n]+)[”\"“»«]")


def looks_like_dialogue(text: str) -> bool:
    """A paragraph that opens with a dialogue dash, or quotes more than three words
    (a quoted single word or title, such as „ekstra", is not speech)."""
    return bool(DIALOGUE_START.match(text)) or any(len(q.split()) > 3 for q in QUOTED.findall(text))


def cmd_dialogue(root: Path, a: argparse.Namespace) -> None:
    st = load_state(root)
    if a.group:
        return group_lines(root)
    chapters = parse_chapters(a.chapters, st)
    out = []
    for n in chapters:
        lines = [(pid, t) for pid, t in read_paragraphs(chapter_file(root, n))
                 if pid != "title" and looks_like_dialogue(t)]
        if not lines:
            continue
        out.append(f"## Chapter {n}\n")
        for pid, t in lines:
            if a.skeleton:
                out.append(f"- [{n:02d}:{pid}] ? → ? | {plain(t)[:90]}")
            else:
                out.append(f"[{n:02d}:{pid}] {t}\n")
        if a.skeleton:
            out.append("")
    if not a.skeleton:
        print("\n".join(out))
        return
    path = root / "work" / "lines-draft.md"
    if path.exists():
        sys.exit(f"{path.relative_to(root)} already exists; delete it first to start again.")
    head = ["# Dialogue lines (draft)", "",
            "<!-- Replace '? → ?' with 'Speaker → Listener' (glossary English names), 'thought',",
            "     or 'not dialogue'. An unnamed speaker gets a short role ('Inn man 1', 'Older guard');",
            "     'Unknown' only when even the role is unclear. Then run 'dialogue --group'. -->", ""]
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(head + out), encoding="utf-8")
    print(f"Wrote {path.relative_to(root)} ({sum(1 for x in out if x.startswith('- ['))} candidate lines).")


def group_lines(root: Path) -> None:
    """work/lines-draft.md (chapter order) → work/lines.md (one section per speaker)."""
    draft = root / "work" / "lines-draft.md"
    if not draft.exists():
        sys.exit("No work/lines-draft.md. Run 'dialogue <chapters> --skeleton' first.")
    by: dict[str, list[str]] = {}
    stats: dict[str, dict[str, int]] = {}
    open_lines = 0
    sources: dict[int, dict[str, str]] = {}
    for line in draft.read_text(encoding="utf-8").splitlines():
        m = LINE_ENTRY.match(line)
        if not m:
            continue
        ch, pid, who, to = m.groups()
        who = who.strip()
        if who in ("?", "") :
            open_lines += 1
            continue
        if who.lower() in ("not dialogue", "-", "—"):
            continue
        n = int(ch)
        if n not in sources:
            sources[n] = dict(read_paragraphs(chapter_file(root, n)))
        said = plain(sources[n].get(pid, ""))
        said = said if len(said) <= 200 else said[:200].rsplit(" ", 1)[0] + " …"
        entry = f"[{ch}:{pid}]" + (f" to {to}" if to and to != "?" else "") + (f": {said}" if said else "")
        by.setdefault(who, []).append(entry)
        speech = " ".join(split_speech(sources[n].get(pid, ""))[1]) or sources[n].get(pid, "")
        k = stats.setdefault(who, {"short": 0, "!": 0, "?": 0, "…": 0})
        k["short"] += len(re.findall(r"\w+", speech)) <= 4
        for mark in ("!", "?", "…"):
            k[mark] += mark in speech or (mark == "…" and "..." in speech)
    order = sorted(by, key=lambda k: (k in ("Unknown", "thought"), -len(by[k])))
    parts = ["# Attributed lines", "",
             "<!-- Built by 'dialogue --group' from work/lines-draft.md. The counts under each heading are a",
             "     starting point for the brief: lines of four words or fewer, and lines with ! ? or …",
             "     in the speech. Count the voice's own markers by reading the lines. -->", ""]
    for who in order:
        k = stats[who]
        counts = (f"Counts: {len(by[who])} lines; four words or fewer {k['short']}; "
                  f"with ! {k['!']}; with ? {k['?']}; with … {k['…']}")
        parts += [f"## {who} ({len(by[who])})", "", counts, "", *by[who], ""]
    (root / "work" / "lines.md").write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote work/lines.md: {len(by)} speakers." + (f" {open_lines} lines still '?'." if open_lines else ""))


ITALIC = re.compile(r"(?<![*\w])\*(?!\*)([^*\n]+?)\*(?![*\w])|(?<![_\w])_([^_\n]+?)_(?![_\w])")


def narration_of(text: str, genre: str) -> str:
    """The narration of a paragraph for `inner`. Non-fiction keeps everything; fiction drops
    speech, but keeps short quotations (a word or a phrase of up to three words, such as
    „ekstra” or a quoted label), which belong to the sentence around them."""
    if genre == "nonfiction":
        return text
    if SOURCE_DASH.match(text):
        return " ".join(split_speech(text)[0])
    return SPEECH_QUOTES.sub(lambda m: m.group(0) if len(m.group(0).split()) <= 3 else " ", text)


def cmd_inner(root: Path, a: argparse.Namespace) -> None:
    """Italic thoughts and narration questions per chapter: the raw material for the
    inner voice of a point-of-view character (fiction) or the author's voice (non-fiction)."""
    st = load_state(root)
    total_i = total_q = 0
    for n in parse_chapters(a.chapters, st):
        chapter = next(c for c in st["chapters"] if c["n"] == n)
        italics, questions = [], []
        for pid, t in read_paragraphs(chapter_file(root, n)):
            if pid == "title" or SECTION.match(t):
                continue
            narration = narration_of(t, st.get("genre", "fiction"))
            for m in ITALIC.finditer(narration):
                frag = (m.group(1) or m.group(2)).strip()
                if len(frag.split()) >= 1 and not FOOTNOTE.search(frag):
                    italics.append(f"[{n:02d}:{pid}] *{frag}*")
            if "?" in narration:
                q = [x.strip() for x in SENTENCE_END.split(narration) if "?" in x]
                questions.append(f"[{n:02d}:{pid}] " + " ".join(q)[:160])
        total_i += len(italics)
        total_q += len(questions)
        label = chapter.get("label") or ""
        print(f"## Chapter {n}" + (f" ({label})" if label else "")
              + f": {len(italics)} italic passages, {len(questions)} narration paragraphs with a question\n")
        if italics:
            print("Italic (thoughts, emphasis, titles, foreign words; decide which are thought):")
            print("\n".join(italics) + "\n")
        if questions:
            print("Questions in narration:")
            print("\n".join(questions) + "\n")
    print(f"Total: {total_i} italic passages, {total_q} narration paragraphs with a question.")


# ─── fragment / save ────────────────────────────────────────────────────


def slug(name: str) -> str:
    """File name for a brief or an export: Latin letters lose their accents; other
    scripts (Cyrillic, Kannada, Japanese) are kept."""
    out, prev = [], ""
    for c in unicodedata.normalize("NFKD", name):
        if unicodedata.combining(c) and prev.isascii():
            continue  # an accent on a Latin letter
        out.append(c)
        prev = c
    s = unicodedata.normalize("NFC", "".join(out)).lower()
    s = s.replace("ł", "l").replace("ø", "o").replace("ß", "ss").replace("æ", "ae").replace("œ", "oe")
    keep = "".join(c if c.isalnum() or unicodedata.category(c).startswith("M") else " " for c in s)
    return "-".join(keep.split())


FOOTNOTE_DEF = re.compile(r"^\s*\[\^([^\]]+)\]:")


def footnote_texts(root: Path, st: dict, n: int, text: str, here: set[str]) -> dict:
    """{(chapter, id): (source, translation)} of footnote definitions ('[^3]: …') whose
    markers appear in `text` but which stand outside the fragment: in the same chapter
    first, else in the last chapter (endnotes collected at the end of the book). Other
    chapters are not searched, since footnote numbers often restart in each chapter."""
    marks = {m.group(1) for m in re.finditer(r"\[\^([^\]]+)\](?!:)", text)}
    marks -= {m.group(1) for line in text.split("\n") if (m := FOOTNOTE_DEF.match(line))}
    out: dict = {}
    last = st["chapters"][-1]["n"]
    order = [n] + ([last] if last != n else [])
    for ch in order:
        if not marks:
            break
        tgt = dict(read_paragraphs(chapter_file(root, ch, "translation")))
        for pid, t in read_paragraphs(chapter_file(root, ch)):
            m = FOOTNOTE_DEF.match(t)
            if m and m.group(1) in marks and not (ch == n and pid in here):
                out[(ch, pid)] = (t, tgt.get(pid, ""))
                marks.discard(m.group(1))
    return out


def cmd_fragment(root: Path, a: argparse.Namespace) -> None:
    st = load_state(root)
    f = find_fragment(st, a.id)
    n = f["chapter"]
    src = read_paragraphs(chapter_file(root, n))
    tgt = dict(read_paragraphs(chapter_file(root, n, "translation")))
    idx = {pid: i for i, (pid, _) in enumerate(src)}
    first, last = idx[f["ids"][0]], idx[f["ids"][-1]]
    body = src[first:last + 1]
    before = src[max(0, first - NEIGHBOUR_PARAGRAPHS):first]
    after = src[last + 1:last + 1 + NEIGHBOUR_PARAGRAPHS]
    chapter = next(c for c in st["chapters"] if c["n"] == n)

    glossary = load_glossary(root)
    text = "\n".join(t for _, t in body)
    found, maybe = term_hits(text, glossary)
    earlier = "\n".join(t for _, t in src[:first])  # this chapter before the fragment
    seen_before = {id(r) for r in terms_in(earlier, glossary)} if earlier else set()
    voices: list[Path] = []
    for r in found:
        if re.search(r"character|person", r.get("type", "").lower()):
            path = root / "voices" / f"{slug(target_of(r))}.md"
            if path.exists():
                voices.append(path)
    # Briefs for minor speakers: a line "Matches: word, word" lists source words that call them up.
    for path in sorted((root / "voices").glob("*.md")):
        if path.name.startswith("_") or path in voices:
            continue
        brief = path.read_text(encoding="utf-8")
        m = re.search(r"^Matches:\s*(.+)$", brief, re.MULTILINE)
        if m and any(w.strip() and w.strip().lower() in text.lower() for w in m.group(1).split(",")):
            voices.append(path)
            continue
        # A line "Quoted in: 01:p020, 01:p022" lists paragraphs where another character
        # quotes this one's pet word or phrase.
        q = re.search(r"^Quoted in:\s*(.+)$", brief, re.MULTILINE)
        here = {f"{n:02d}:{pid}" for pid in f["ids"]}
        if q and here & {x.strip() for x in q.group(1).split(",")}:
            voices.append(path)
    if (root / "voices" / "_author.md").exists():
        voices.insert(0, root / "voices" / "_author.md")
    if (root / "voices" / "_cast.md").exists():
        voices.append(root / "voices" / "_cast.md")

    label = chapter.get("label") or short_label(chapter["title"])
    out = [f"# Fragment {f['id']} ({f['words']} words), chapter {n}" + (f" ({label})" if label else ""), ""]
    out.append("## Glossary terms in this fragment\n")
    out.append("(Notes are shown where a term first appears in the chapter; see glossary.md for the rest.)\n")
    for r in found:
        note = r.get("notes") if id(r) not in seen_before and r.get("notes") not in (None, "", "—") else None
        out.append(f"- {r['source']} → {target_of(r)}" + (f" — {note}" if note else ""))
    if not found:
        out.append("(none found by the script; check the full glossary for names it missed)")
    if maybe:
        out.append("\nMaybe (found only at the start of a sentence, where the capital says nothing; "
                   "read the sentence and decide whether the term or the everyday word is meant):\n")
        out += [f"- {r['source']} → {target_of(r)}" + (f" — {r['notes']}" if r.get("notes") else "") for r in maybe]
    out.append("\n## Voice briefs to read (the author's voice first, then the speakers')\n")
    out += [f"- {p.relative_to(root)}" for p in voices] or ["(none matched; check who speaks in the fragment)"]
    if before:
        out.append("\n## End of the previous text (source; context only, do not translate)\n")
        out.append(render(before))
        prev_t = [(pid, tgt[pid]) for pid, _ in before if tgt.get(pid)]
        if prev_t:
            out.append("\n## End of the previous text (current translation; match its terms and tone)\n")
            out.append(render(prev_t))
    if after:
        out.append("\n## Start of the next text (source; context only, do not translate)\n")
        out.append(render(after))
    notes = footnote_texts(root, st, n, text, {pid for pid, _ in body})
    if notes:
        out.append("\n## Footnotes whose markers are in this fragment (context; each is translated where it stands)\n")
        for (ch, pid), (src_t, tgt_t) in notes.items():
            out.append(f"[{ch:02d}:{pid}] {src_t}" + (f"\n  current translation: {tgt_t}" if tgt_t else ""))
    out.append("\n## Source paragraphs to translate\n")
    out.append(render(body))
    out.append(f"\n<!-- Write the translation as the same [id] blocks to work/{f['id']}.md, "
               f"then run: save {f['id']} work/{f['id']}.md. Notes go under '## {f['id']}' "
               f"in notes/chapter-{n:02d}.md. -->")
    print("\n".join(out))


def cmd_save(root: Path, a: argparse.Namespace) -> None:
    st = load_state(root)
    f = find_fragment(st, a.id)
    new = read_paragraphs(Path(a.file) if Path(a.file).is_absolute() else root / a.file)
    got = [pid for pid, _ in new]
    if got != f["ids"]:
        missing = [p for p in f["ids"] if p not in got]
        extra = [p for p in got if p not in f["ids"]]
        sys.exit(f"Not saved: the ids must match the fragment, in order.\n"
                 f"  missing: {missing or '—'}\n  extra: {extra or '—'}\n"
                 f"  expected order: {' '.join(f['ids'])}")
    empty = [pid for pid, t in new if not t]
    if empty:
        sys.exit(f"Not saved: empty paragraphs {empty}.")
    n = f["chapter"]
    order = [pid for pid, _ in read_paragraphs(chapter_file(root, n))]
    merged = dict(read_paragraphs(chapter_file(root, n, "translation")))
    merged.update(dict(new))
    paras = [(pid, merged[pid]) for pid in order if pid in merged]
    write_paragraphs(chapter_file(root, n, "translation"),
                     f"<!-- Chapter {n} translation. Same [id]s as source/chapter-{n:02d}.md. -->", paras)
    problems = hard_checks(st, new, read_paragraphs(chapter_file(root, n)), load_glossary(root))
    print(f"Saved {f['id']} ({len(new)} paragraphs) to translation/chapter-{n:02d}.md.")
    for p in problems:
        print(f"  check: {p}")
    ids = {pid for pid, _ in new}
    src_paras = [t for pid, t in read_paragraphs(chapter_file(root, n)) if pid in ids]
    print("  style: " + style_line(st, [t for _, t in new], src_paras, per_fragment=True))
    print("  (Targets are warnings about translated prose, not goals: where the source does the same "
          "on purpose, keep it.)")


# ─── checks ─────────────────────────────────────────────────────────────


def leftover_pattern(st: dict) -> re.Pattern[str] | None:
    """Source letters that the target language does not use (Polish ó is fine in Czech)."""
    letters = st.get("source_letters") or ""
    if not letters:
        return None
    own = class_escape(LANGUAGES.get(st.get("target_language_code", "en"), {}).get("letters", ""))
    letters = class_escape(letters)
    return re.compile(f"(?![{own}])[{letters}]" if own else f"[{letters}]")


def class_escape(letters: str) -> str:
    """Letters for a regex character class: '\\', ']' and '^' are escaped; '-' between two
    letters stays a range (the LANGUAGES table uses ranges for whole scripts)."""
    return re.sub(r"([\\\]^])", r"\\\1", letters)


def kept_names(glossary: list[dict]) -> re.Pattern[str] | None:
    """Target forms the glossary keeps with letters outside plain ASCII ('Kraków', 'Paweł'),
    so the leftover-letters check does not report them."""
    forms = sorted({f for r in glossary for f in target_forms(r) if not f.isascii()}, key=len, reverse=True)
    if not forms:
        return None
    return re.compile(rf"(?<!{LETTER})(?:{'|'.join(word_pattern(f, True) for f in forms)})(?!{LETTER})")


def hard_checks(st: dict, tgt: list[tuple[str, str]], src: list[tuple[str, str]],
                glossary: list[dict] | None = None) -> list[str]:
    src_map = dict(src)
    leftover = leftover_pattern(st)
    names = kept_names(glossary or [])
    target = LANGUAGES.get(st.get("target_language_code", "en"), {})
    quotes = target.get("dialogue") == "quotes" and st.get("genre", "fiction") == "fiction"
    nonfiction = st.get("genre") == "nonfiction"
    problems = []
    for pid, text in tgt:
        source = src_map.get(pid, "")
        if leftover and (m := leftover.findall(names.sub(" ", text) if names else text)):
            problems.append(f"[{pid}] source-language letters left: {''.join(sorted(set(m)))}")
        if quotes and DIALOGUE_START.match(text) and SOURCE_DASH.match(source):
            problems.append(f"[{pid}] starts with a dialogue dash; this language uses quotation marks")
        if len(FOOTNOTE.findall(text)) != len(FOOTNOTE.findall(source)):
            problems.append(f"[{pid}] footnote markers: {len(FOOTNOTE.findall(source))} in the source, "
                            f"{len(FOOTNOTE.findall(text))} here")
        for url in LINK.findall(source):
            if url.rstrip(".,;:)") not in text:
                problems.append(f"[{pid}] link missing or changed: {url}")
        if nonfiction:
            digits = lambda t: [re.sub(r"\D", "", n) for n in NUMBER.findall(FOOTNOTE.sub(" ", t))]  # noqa: E731
            gone = [n for n in digits(source) if n and n not in digits(text)]
            if gone:
                problems.append(f"[{pid}] numbers not found in the translation: {', '.join(gone)} "
                                "(fine if written out or converted on purpose)")
        if re.search(r"\\[!.\-*_]", text):
            problems.append(f"[{pid}] markdown escape backslash")
        if re.search(r"(?<!\.)\.\.\.(?!\.)", text):
            problems.append(f"[{pid}] three full stops; write the ellipsis as …")
        s_ph = PLACEHOLDER.findall(src_map.get(pid, ""))
        if len(PLACEHOLDER.findall(text)) < len(s_ph):
            problems.append(f"[{pid}] author placeholder missing ({', '.join(s_ph)})")
    return problems


def glossary_drift(glossary: list[dict], src: dict[str, str], tgt: list[tuple[str, str]],
                   code: str = "en", skip: set[str] | None = None) -> dict[str, list[str]]:
    """{term line: [paragraph ids]} for source terms whose agreed translation is missing.
    Paragraphs in `skip` (special passages whose rule changed the wording) are left out."""
    out: dict[str, list[str]] = {}
    for pid, text in tgt:
        if skip and pid in skip:
            continue
        for r in terms_in(src.get(pid, ""), glossary):
            if target_of(r) and not target_regex(r, code).search(text):
                out.setdefault(f"'{r['source']}' → '{target_of(r)}'", []).append(pid)
    return out


def pronoun_re(code: str) -> re.Pattern[str] | None:
    """Sentence-opening third-person pronouns of a language (She/He), or None."""
    words = LANGUAGES.get(code, {}).get("pronouns")
    return re.compile(rf"^[*_\s]*({'|'.join(words)})\b") if words else None


def pronoun_runs(tgt: list[tuple[str, str]], code: str, top: int = 5) -> list[str]:
    """Paragraphs with the most pronoun sentence openers (two or more), for revision."""
    pr = pronoun_re(code)
    if not pr:
        return []
    counts = []
    for pid, text in tgt:
        narration = " ".join(split_speech(text)[0])
        k = sum(bool(pr.match(s)) for s in SENTENCE_END.split(narration) if s.strip())
        if k >= 2:
            counts.append((k, pid))
    return [f"{pid} ({k})" for k, pid in sorted(counts, key=lambda x: (-x[0], x[1]))[:top]]


SPEECH_QUOTES = re.compile(
    r'\u201e[^\u201d\u201c"\n]*[\u201d\u201c"]|\u00bb[^\u00ab\n]*\u00ab|\u00ab[^\u00bb\n]*\u00bb|'
    r'"[^"\n]*"|\u201c[^\u201d\n]*\u201d|「[^」\n]*」|『[^』\n]*』|'
    # British single quotes: curly ‘…’, or straight '…' that opens after a non-letter and
    # closes before one, so the apostrophes in "I'm" or "don't" do not end the span.
    r"\u2018[^\u2019\n]*(?:\u2019\w[^\u2019\n]*)*\u2019|(?<!\w)'(?=\S)[^'\n]*(?:'\w[^'\n]*)*(?<=\S)'(?!\w)")


def split_speech(text: str) -> tuple[list[str], list[str]]:
    """(narration parts, speech parts) of one paragraph, in any language. A paragraph
    that opens with a dash alternates speech and narration at each ' – ' (speech, tag,
    speech, ...); quoted spans („…“, »…«, «…», "…", “…”, 「…」) count as speech."""
    if SOURCE_DASH.match(text):
        parts = re.split(r"\s[\u2013\u2014]\s", SOURCE_DASH.sub("", text, count=1))
        return parts[1::2], parts[0::2]
    return [SPEECH_QUOTES.sub(" ", text)], SPEECH_QUOTES.findall(text)


def ellipses(text: str) -> int:
    return text.count("…") + len(re.findall(r"(?<!\.)\.\.\.(?!\.)", text))


SOURCE_DASH = re.compile(r"^\s*[\u2013\u2014-]\s")


def source_ellipses(paragraphs: list[str]) -> tuple[float, float]:
    """Ellipses per 1k source words in narration and in dialogue (see split_speech)."""
    narration, dialogue = [], []
    for text in paragraphs:
        n, d = split_speech(text)
        narration += n
        dialogue += d
    words = max(sum(len(t.split()) for t in paragraphs), 1)
    per_1k = lambda parts: round(1000 * sum(ellipses(t) for t in parts) / words, 1)  # noqa: E731
    return per_1k(narration), per_1k(dialogue)


def ellipsis_flag(value: float, source: float) -> str:
    """Narration ellipses with the target and the source rate; warn only above both."""
    warn = " ⚠" if value > ELLIPSES_MAX_PER_1K and value > source else ""
    return f"{value} (target ≤ {ELLIPSES_MAX_PER_1K}, source {source}){warn}"


def pronoun_share(paragraphs: list[str], code: str) -> float | None:
    """Share (%) of narration sentences that open with a third-person pronoun, or None
    when the language has no such list (it usually drops the subject)."""
    pr = pronoun_re(code)
    if not pr:
        return None
    narration = " ".join(n for t in paragraphs for n in split_speech(t)[0])
    sentences = [x for x in SENTENCE_END.split(narration) if x.strip()]
    return round(100 * sum(bool(pr.match(x)) for x in sentences) / max(len(sentences), 1), 1)


def sentence_count(paragraphs: list[str]) -> int:
    return sum(len([x for x in SENTENCE_END.split(t) if x.strip()]) for t in paragraphs if not t.startswith("#"))


def style_metrics(text: str, code: str = "en") -> dict:
    parts = [split_speech(t) for t in text.split("\n")]
    narration = " ".join(x for n, _ in parts for x in n)
    dialogue = " ".join(x for _, d in parts for x in d)
    words = max(len(text.split()), 1)
    stock = {p: len(re.findall(p, text, re.IGNORECASE)) for p in STOCK_PHRASES} if code == "en" else {}
    per_1k = lambda k: round(1000 * k / words, 1)  # noqa: E731
    return {
        "words": words,
        "she_he_pct": pronoun_share(text.split("\n"), code),
        "ellipses_per_1k": per_1k(ellipses(text)),
        "ellipses_narration_per_1k": per_1k(ellipses(narration)),
        "ellipses_dialogue_per_1k": per_1k(ellipses(dialogue)),
        "dashes_per_1k": per_1k(text.count("—")),
        "stock": {STOCK_LABEL.get(k, re.sub(r"\\b|\(\?!.*\)", "", k)): v for k, v in stock.items() if v},
    }


def style_line(st: dict, tgt: list[str], src: list[str], per_fragment: bool = False,
               m: dict | None = None) -> str:
    """One line of style numbers for a fragment or a chapter, each next to the source's
    own rate where one can be measured. All books: sentences and questions against the
    source (merged sentences and lost rhetorical questions flatten an author's voice).
    Fiction: pronoun openers and ellipses. Non-fiction: very long sentences against the
    source. Both: em dashes and stock phrases."""
    code = st.get("target_language_code", "en")
    m = m or style_metrics("\n".join(tgt), code)
    flag = lambda v, mx, unit="": f"{v}{unit} (target ≤ {mx}{unit}){' ⚠' if v > mx else ''}"  # noqa: E731
    parts = [f"{m['words']} words"] if not per_fragment else []
    n_t, n_s = sentence_count(tgt), sentence_count(src)
    parts.append(f"sentences {n_t} (source {n_s})")
    q_t = sum(t.count("?") for t in tgt if not t.startswith("#"))
    q_s = sum(t.count("?") for t in src if not t.startswith("#"))
    parts.append(f"questions {q_t} (source {q_s})")
    if st.get("genre") == "nonfiction":
        # "Long" is 30 words in the source and the same length scaled by the two texts' word
        # ratio in the translation, since languages need different numbers of words.
        word_count = lambda ps: sum(len(t.split()) for t in ps if not t.startswith("#"))  # noqa: E731
        limit = 30 * word_count(tgt) / max(word_count(src), 1)
        long_ = lambda ps, k: sum(1 for t in ps if not t.startswith("#")  # noqa: E731
                                  for x in SENTENCE_END.split(t) if len(x.split()) >= k)
        parts.append(f"long sentences {long_(tgt, limit)} (source {long_(src, 30)}; "
                     f"30 source words, {round(limit)} here)")
    if st.get("genre", "fiction") == "fiction":
        pronouns = LANGUAGES.get(code, {}).get("pronouns")
        if m["she_he_pct"] is not None:
            src_code = st.get("source_language_code", "")
            src_share = pronoun_share(src, src_code)
            if src_share is not None:
                note = f"source {src_share}%"
            elif LANGUAGES.get(src_code, {}).get("pro_drop"):
                note = "the source drops the subject, so it has no rate; its runs of short action sentences are the author's"
            else:
                note = "no source rate"
            parts.append(f"{'/'.join(pronouns)} openers {flag(m['she_he_pct'], SHE_HE_MAX_PCT, '%')}, {note}")
        src_narr, src_dial = source_ellipses(src)
        parts.append(f"ellipses per 1k in narration {ellipsis_flag(m['ellipses_narration_per_1k'], src_narr)}, "
                     f"in dialogue {m['ellipses_dialogue_per_1k']} (source {src_dial})")
    parts.append(f"em dashes per 1k {flag(m['dashes_per_1k'], DASHES_MAX_PER_1K)}")
    if m["stock"]:
        parts.append(f"check these phrases: {', '.join(f'{k} ×{v}' for k, v in m['stock'].items())}")
    return "; ".join(parts)


def passage_ids(root: Path) -> dict[int, set[str]]:
    """{chapter: paragraph ids} of kept special passages with status passed or corrected,
    read from passages.md headings such as '## 06: p043–p044 (hidden_message)'."""
    path = root / "passages.md"
    out: dict[int, set[str]] = {}
    if not path.exists():
        return out
    for block in re.split(r"(?m)^## ", path.read_text(encoding="utf-8"))[1:]:
        m = re.match(r"(\d+):\s*p(\d+)(?:\s*[–—-]\s*p(\d+))?", block)
        status = re.search(r"(?m)^Status:\s*(\w+)", block)
        if not m or not status or status.group(1).lower() not in ("passed", "corrected"):
            continue
        lo, hi = int(m.group(2)), int(m.group(3) or m.group(2))
        out.setdefault(int(m.group(1)), set()).update(f"p{i:03d}" for i in range(lo, hi + 1))
    return out


def parse_chapters(spec: str | None, st: dict) -> list[int]:
    """'3', '1-4' or '1,3,5-6' → chapter numbers; None → every chapter."""
    every = [c["n"] for c in st["chapters"]]
    if not spec:
        return every
    out: list[int] = []
    for part in spec.split(","):
        m = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+))?\s*", part)
        if not m:
            sys.exit(f"Chapters must look like 3, 1-4 or 1,3,5-6 (got '{spec}').")
        lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
        out += [n for n in every if lo <= n <= hi and n not in out]
    if not out:
        sys.exit(f"No chapters match '{spec}'.")
    return out


def merge_notes(root: Path, st: dict) -> int:
    """Join notes/chapter-NN.md into notes.md, in chapter order. Returns the count of notes."""
    files = sorted((root / "notes").glob("chapter-*.md"))
    if not files:
        return 0
    old = root / "notes.md"
    if old.exists() and "Built by 'check'" not in old.read_text(encoding="utf-8"):
        print("notes.md was written by hand, so it was not replaced. Move its notes into "
              "notes/chapter-NN.md, then delete it, and run check again.")
        return 0
    parts = [f"# Translator notes: {st['title']}",
             "", "<!-- Built by 'check' from notes/chapter-NN.md. Edit those files, not this one. -->", ""]
    count = 0
    for f in files:
        text = f.read_text(encoding="utf-8").strip()
        if text:
            parts += [f"# Chapter {int(f.stem.split('-')[1])}", "", text, ""]
            count += sum(1 for ln in text.splitlines() if ln.startswith("- ["))
    (root / "notes.md").write_text("\n".join(parts), encoding="utf-8")
    return count


def cmd_check(root: Path, a: argparse.Namespace) -> None:
    st = load_state(root)
    glossary = load_glossary(root)
    chapters = parse_chapters(a.chapter, st)
    lines = [f"# Check report: {st['title']}", ""]
    total, untranslated = 0, []
    code = st.get("target_language_code", "en")
    passages = passage_ids(root)
    for n in chapters:
        src = read_paragraphs(chapter_file(root, n))
        tgt = read_paragraphs(chapter_file(root, n, "translation"))
        if not tgt:
            untranslated.append(n)
            continue
        have = {pid for pid, _ in tgt}
        missing = [pid for pid, _ in src if pid not in have]
        problems = hard_checks(st, tgt, src, glossary)
        skip = passages.get(n, set())
        drift = glossary_drift(glossary, dict(src), tgt, code, skip)
        m = style_metrics("\n".join(t for _, t in tgt), code)
        total += len(problems) + len(drift)
        runs = pronoun_runs(tgt, code) if st.get("genre", "fiction") == "fiction" else []
        lines.append(f"## Chapter {n}\n")
        if missing:
            lines.append(f"Untranslated paragraphs: {' '.join(missing)}\n")
        lines.append("Problems:\n" + ("\n".join(f"- {p}" for p in problems) or "- none") + "\n")
        lines.append("Glossary (agreed translation not found; check each, a pronoun or short form may be fine):\n"
                     + ("\n".join(f"- {term} in {len(ids)} paragraph{'s' if len(ids) > 1 else ''}: {' '.join(ids)}"
                                  for term, ids in sorted(drift.items(), key=lambda kv: -len(kv[1])))
                        or "- none") + "\n")
        if skip:
            lines.append(f"(Glossary not checked in special passages: {' '.join(sorted(skip))}.)\n")
        lines.append(f"Style: {style_line(st, [t for _, t in tgt], [t for _, t in src], m=m)}\n")
        if runs and (m["she_he_pct"] or 0) > SHE_HE_MAX_PCT - 3:
            lines.append(f"Most pronoun openers: {', '.join(runs)}\n")
    if untranslated:
        lines.append(f"Not translated yet: {len(untranslated)} chapter{'s' if len(untranslated) > 1 else ''} "
                     f"({', '.join(map(str, untranslated))}).\n")
    (root / "check-report.md").write_text("\n".join(lines), encoding="utf-8")
    checked = [n for n in chapters if n not in untranslated]
    if checked:
        st["last_check"] = {"chapters": checked, "date": date.today().isoformat()}
        save_state(root, st)
    notes = merge_notes(root, st)
    print(f"Wrote check-report.md ({total} problems and glossary terms to look at)."
          + (f" Merged {notes} notes into notes.md." if notes else ""))


# ─── letters (hidden messages) ──────────────────────────────────────────


def cmd_letters(root: Path, a: argparse.Namespace) -> None:
    kind = "translation" if a.translation else "source"
    paras = read_paragraphs(chapter_file(root, a.chapter, kind))
    ids = [pid for pid, _ in paras]
    if a.first not in ids or a.last not in ids:
        sys.exit("First or last id not found in that chapter.")
    block = paras[ids.index(a.first):ids.index(a.last) + 1]
    if a.start_at:
        pid, t = block[0]
        k = t.find(a.start_at)
        if k < 0:
            sys.exit(f"'{a.start_at}' not found in [{pid}].")
        block[0] = (pid, t[k:])
    if a.end_at:
        pid, t = block[-1]
        k = t.find(a.end_at)
        if k < 0:
            sys.exit(f"'{a.end_at}' not found in [{pid}].")
        block[-1] = (pid, t[:k + len(a.end_at)])
    text = "\n".join(t for _, t in block)
    first = lambda items: "".join(w[0] for w in items if w)  # noqa: E731
    letter = lambda s: next((c for c in s if c.isalpha()), "")  # noqa: E731
    sentences = [s for s in SENTENCE_END.split(text) if s.strip()]
    lines_ = [ln for ln in text.splitlines() if ln.strip()]
    words = re.findall(r"[^\W\d_]+", text)
    marked = re.findall(r"\*\*?([^*]+)\*\*?", text)
    print(f"sentences:  {''.join(letter(s) for s in sentences)}")
    print(f"lines:      {''.join(letter(s) for s in lines_)}")
    print(f"paragraphs: {''.join(letter(t) for _, t in block)}")
    print(f"words:      {first(words)}")
    if marked:
        print(f"marked:     {''.join(letter(s) for s in marked)}")


# ─── export ─────────────────────────────────────────────────────────────


def to_md(text: str) -> str:
    if SECTION.match(text.strip()):
        return text.strip()  # a section heading stays a Markdown heading
    lines = text.strip().split("\n")
    if lines[0].strip() == "***":  # a scene break, maybe with a POV name under it
        rest = "  \n".join(lines[1:]).strip()
        return "* * *" + (f"\n\n{rest}" if rest else "")
    return "  \n".join(lines)


def default_heading(st: dict, n: int) -> str:
    word = LANGUAGES.get(st.get("target_language_code", "en"), {}).get("heading", "Chapter")
    return word.format(n=n) if "{n}" in word else f"{word} {n}"


def chapter_heading(title: str, n: int, st: dict | None = None) -> tuple[str, list[str]]:
    """('Chapter 3', [lines under it]) from a translated [title] paragraph: the
    chapter-word line (in any listed language) becomes the heading and the POV name and
    epigraph go under it. A title with no chapter word (non-fiction) is the heading itself."""
    lines = [ln for ln in title.strip().split("\n") if ln.strip()]
    marker = re.compile(rf"^\s*({'|'.join(ALL_CHAPTER_MARKERS)})", re.IGNORECASE)
    for i, ln in enumerate(lines):
        if marker.match(plain(ln)):
            return plain(ln).rstrip("."), lines[:i] + lines[i + 1:]
    return (plain(lines[0]) if lines else default_heading(st or {}, n)), lines[1:]


def cmd_export(root: Path, a: argparse.Namespace) -> None:
    st = load_state(root)
    if a.title:
        st["target_title"] = a.title
        save_state(root, st)
    book_title = st.get("target_title") or st["title"]
    chapters = parse_chapters(a.chapters, st)
    out = [f"% {book_title}", ""]
    gaps = 0
    for ch in [c for c in st["chapters"] if c["n"] in chapters]:
        n = ch["n"]
        src = read_paragraphs(chapter_file(root, n))
        tgt = dict(read_paragraphs(chapter_file(root, n, "translation")))
        has_title = any(p == "title" for p, _ in src)
        if tgt.get("title"):
            heading, under = chapter_heading(tgt["title"], n, st)
        elif has_title:
            gaps += 1
            heading, under = default_heading(st, n), [f"**[Untranslated: chapter {n}, heading]**"]
        else:
            heading, under = default_heading(st, n), []
        out.append(f"# {heading}\n")
        if under:
            out.append(to_md("\n".join(under)) + "\n")
        for f in [f for f in st["fragments"] if f["chapter"] == n]:
            for pid in f["ids"]:
                if pid == "title":
                    continue
                if tgt.get(pid):
                    out.append(to_md(tgt[pid]) + "\n")
                else:
                    gaps += 1
                    out.append(f"**[Untranslated: chapter {n}, paragraph {pid}]**\n")
    if gaps and not a.draft:
        sys.exit(f"{gaps} paragraphs are not translated. Use --draft to export with gaps marked.")
    exp = root / "export"
    exp.mkdir(exist_ok=True)
    name = slug(book_title) or "book"
    if a.chapters:
        name += "_ch" + re.sub(r"[^0-9,-]", "", a.chapters).replace(",", "+")
    if a.draft:
        name += "_DRAFT"
    md = exp / f"{name}.md"
    md.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {md.relative_to(root)}")
    if shutil.which("pandoc"):
        for ext in ("docx", "epub"):
            target = exp / f"{name}.{ext}"
            subprocess.run(["pandoc", str(md), "-o", str(target)], check=True)
            print(f"Wrote {target.relative_to(root)}")
    else:
        print("pandoc not found: only Markdown was written. Install pandoc for .docx and .epub.")


# ─── CLI ────────────────────────────────────────────────────────────────


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dir", default=".", help="book folder (default: current folder)")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("prepare")
    s.add_argument("manuscript")
    s.add_argument("--source-language", required=True, help="ISO code (pl, de, ja) or English name")
    s.add_argument("--target-language", default="en",
                   help="ISO code or name, with a variant if it matters (en-GB, en-US, pt-BR); default en")
    s.add_argument("--genre", choices=["fiction", "nonfiction"], default="fiction")
    s.add_argument("--chapter-level", type=int, choices=[1, 2],
                   help="non-fiction: the heading level of chapters (default: guessed); deeper levels are sections")
    s.add_argument("--title")
    s.add_argument("--target-title", help="title of the translation, used by export")
    s.add_argument("--letters", help="source letters that must not stay in the translation")
    s.add_argument("--force", action="store_true")
    sub.add_parser("status")
    s = sub.add_parser("mark"); s.add_argument("step"); s.add_argument("state")
    s = sub.add_parser("dialogue"); s.add_argument("chapters", nargs="?", help="3, 1-4 or 1,3,5-6")
    s.add_argument("--skeleton", action="store_true", help="write work/lines-draft.md to fill in")
    s.add_argument("--group", action="store_true", help="turn work/lines-draft.md into work/lines.md")
    s = sub.add_parser("inner"); s.add_argument("chapters", nargs="?", help="3, 1-4 or 1,3,5-6")
    s = sub.add_parser("terms"); s.add_argument("chapter", type=int)
    s = sub.add_parser("fragment"); s.add_argument("id")
    s = sub.add_parser("save"); s.add_argument("id"); s.add_argument("file")
    s = sub.add_parser("letters"); s.add_argument("chapter", type=int); s.add_argument("first")
    s.add_argument("last"); s.add_argument("--translation", action="store_true")
    s.add_argument("--from", dest="start_at", help="start inside the first paragraph at these words")
    s.add_argument("--to", dest="end_at", help="end inside the last paragraph after these words")
    s = sub.add_parser("check"); s.add_argument("chapter", nargs="?", help="3, 1-4 or 1,3,5-6")
    s = sub.add_parser("export"); s.add_argument("--draft", action="store_true")
    s.add_argument("--chapters", help="export only these chapters: 3, 1-4 or 1,3,5-6")
    s.add_argument("--title", help="title of the translation (saved for later exports)")
    a = p.parse_args()
    root = Path(a.dir).expanduser().resolve()
    {
        "prepare": cmd_prepare, "status": cmd_status, "mark": cmd_mark, "dialogue": cmd_dialogue,
        "inner": cmd_inner,
        "terms": cmd_terms, "fragment": cmd_fragment, "save": cmd_save, "letters": cmd_letters,
        "check": cmd_check, "export": cmd_export,
    }[a.cmd](root, a)


if __name__ == "__main__":
    main()
