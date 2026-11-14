---
name: translate-books-better
description: Translate a book manuscript (a novel, short stories, or non-fiction such as essays, memoir, popular science, history or self-help) from any language into any other with Claude Code itself, following the Mneme workflow. The manuscript is split into chapters and fragments of about 1,200 words, then come a style sheet for the target language, a reviewed glossary of names and terms, voice briefs for the author and the characters or quoted people, a fragment-by-fragment translation, checks and export. State is kept in plain files, so a run can stop and continue. Use when the user asks to translate a book, novel, manuscript or chapters, or to continue a Mneme translation in a folder that has mneme.json.
argument-hint: "<manuscript.docx|.md|.txt> [source language] [target language] [fiction|nonfiction]"
allowed-tools: Bash(uv run ${CLAUDE_SKILL_DIR}/scripts/mneme.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/mneme.py *)
---

# Mneme: translate a book with Claude Code

You translate the book yourself. No API keys, no database, no Docker. The helper script does only what needs exact counting: splitting, fragment boundaries, merging translated paragraphs, checks and export.

The workflow is the one of the [Mneme app](https://github.com/AgaMiko/mneme-book-translator). Its rules are in `references/`; read each one when you reach its step, not all at once. The rules work for any pair of languages and for fiction and non-fiction; where they differ, each file says so under a "Fiction" or "Non-fiction" heading.

## The helper script

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/mneme.py --dir <book folder> <command>
```

Without `uv`, use `python3` in place of `uv run` (reading a `.docx` then needs `pip install python-docx`). Run `--help` for all commands. The ones you use most: `status`, `fragment <id>`, `save <id> <file>`, `check`, and `find "<words>"` to get the paragraph id of a passage you want to cite.

The script knows the letters, chapter words, pronouns and dialogue marks of the languages in its `LANGUAGES` table (English, Polish, German, French, Spanish, Italian, Portuguese, Dutch, Swedish, Czech, Slovak, Hungarian, Russian, Ukrainian, Kannada, Japanese, Chinese). Any other language works too, with fewer automatic checks: `prepare` says which ones are missing.

## The book folder

Everything lives in one folder the user chooses (ask; default: a new folder named after the book, next to the manuscript). Never write into the manuscript itself. If the folder already has a `mneme.json` from another run, do not split into it: tell the user, and use a new folder name unless they say otherwise.

```
mneme.json               state: language pair, genre, chapters, fragments, step status (written by the script)
source/chapter-NN.md     source text, one [id] block per paragraph
source/front-matter.md   title page and other text before chapter 1 (not translated)
style-sheet.md           the target language's conventions for this book (you write it)
glossary.md              the glossary table (you write it; the user reviews it)
voices/_author.md        the author's voice; voices/<name>.md one brief per speaker; _cast.md, _samples.md
passages.md              special passages: rule, status, first translation
translation/chapter-NN.md  the translation, same [id]s as the source
notes/chapter-NN.md      translator notes for the author, one file per chapter
notes.md                 all notes in one file (built by `check`; do not edit)
work/                    your scratch files (glossary notepad, attributed lines, fragment drafts)
check-report.md          output of `check`
export/                  the finished book
```

Paragraph files use one format: a line `[p012]` (or `[title]` for the chapter heading), then the paragraph text. The translation of a paragraph keeps its id. Everywhere you cite text (glossary notes, voice evidence, passages, notes), cite these ids as `[01:p019]` (chapter and paragraph), never line numbers of the manuscript or of a source file.

## Starting or continuing

If the folder has `mneme.json`, run `status` and continue from the first step that is not done. Tell the user where you are in one or two lines. Otherwise ask the user once:
- the source and target language, if not clear (with the variant when it matters: British or American English, European or Brazilian Portuguese);
- whether the book is fiction or non-fiction, if not clear from the text;
- whether a reviewed glossary or an earlier translation of this book (or of an earlier book in the series, or a published translation of works it quotes) exists; if so, use it as [references/glossary.md](references/glossary.md) "Starting from an existing glossary" describes.

Then start with step 1. Follow the steps in order, and record each one with `mark <step> <state>`.

## Steps

### 1. Split, and write the style sheet

`prepare <manuscript> --source-language <code> --target-language <code or variant> --genre <fiction|nonfiction> --title "<title>" --target-title "<translated title>"`. Codes are ISO codes (`pl`, `de`, `en-GB`, `pt-BR`) or English names. The translated title is used by `export`; leave it out if it is not decided yet (`export --title` sets it later). If the manuscript has no title (an empty first heading, a file name such as "Untitled document"), ask the user; when running straight through, use the working title "Untitled" and say so in your report. Never invent a title.

For a source language the script does not list, pass `--letters "<letters that must not stay in the translation>"`. The script finds chapters by the Heading 1 style in a `.docx`, `#` or `##` lines in Markdown, and chapter words ("Rozdział 3", "Kapitel 3", "Chapter 3", prologue, epilogue, in the listed languages). For non-fiction, the top heading level that repeats is the chapter, and deeper headings stay in the chapter as section headings (`## Section`); fragments may end at a section heading. A file with one top heading that looks like a chapter ("I", "3", "Rozdział 3") is read as a single chapter; `prepare` says what it guessed, and `--chapter-level 1` or `2` overrides it. Text before the first chapter heading (title page, author, dedication) goes to `source/front-matter.md`.

Check the split before going on. Look at `status` and at `source/chapter-01.md` and one later chapter:
- chapter 1 is the book's real first chapter, and the number of chapters is right;
- each chapter starts with a `[title]` block holding its heading, one part per line (fiction: POV name, chapter line, epigraph lines, attribution; non-fiction: the chapter title, maybe a subtitle or epigraph);
- fiction: each scene break is a single `***` paragraph (or `*** Name`), with no leftover `#`, `\` or `**` marks;
- non-fiction: section headings are their own paragraphs starting with `##`; footnote definitions (`[^1]: …`) and block quotes are kept as paragraphs. If a chapter's heading is only a number ("I", "3") and its first section heading reads as the chapter's title, keep both as the source has them (the number as the chapter heading, the section heading under it) and do not move or merge headings; the author decides the book's heading scheme.

`prepare` removes markdown escapes such as `\!` from paragraph text; a `\*` left in a paragraph is fine, since the translation drops it and `check` flags any that stay.

If something is wrong, make a `.md` copy of the manuscript and fix it there: each chapter heading on its own `## ` line (non-fiction: `# Book title`, `## Chapter`, `### Section`), front matter removed, scene breaks written as `***`. Then run `prepare` on the copy with `--force`. `--force` refuses once `translation/` has files, because the paragraph ids may change; split before you write the glossary, the voices or any notes, since they cite paragraph ids.

Then write `style-sheet.md` for the target language, as [references/translation-rules.md](references/translation-rules.md) "The style sheet" describes: spelling variant, quotation and dialogue marks, numbers, units and dates, the chapter word, and (non-fiction) citations and footnotes. Keep it to one screen. Every fragment follows it.

### 2. Glossary, then stop for review

Follow [references/glossary.md](references/glossary.md). Build `glossary.md` chapter by chapter, review it yourself, then **stop**: show the user a short summary and ask them to review `glossary.md`. Do not start the voices until the user says the glossary is ready. Then set kept rows to `accepted` and run `mark glossary reviewed`.

### 3. Voices, then stop for review

Follow [references/voices.md](references/voices.md). Write `voices/_author.md` first: the author's own voice, with counts. Then, for fiction, collect each character's lines (`dialogue --skeleton`, then `dialogue --group`) and the point-of-view characters' thoughts (`inner`), profile them, write the cast notes and one brief per character. For non-fiction, add briefs only for people the book quotes at length or interviews. Translate a short test passage per main voice, then **stop** and ask the user to review `voices/`. Run `mark voices reviewed` when they approve.

### 4. Special passages: scan

Follow steps 1 and 2 of [references/special-passages.md](references/special-passages.md): list verse, documents that may hide a message, plot wordplay and (non-fiction) quotations from other works in `passages.md`, with their rules. Run `mark passages scanned`. Tell the user what you found in a few lines; no need to wait.

### 5. Translate

Read [references/translation-rules.md](references/translation-rules.md) and `style-sheet.md` once per session, and keep to them for every fragment. Then for each fragment in book order (`status` gives the next one):

1. `fragment <id>` prints the fragment: its source paragraphs, the footnotes whose markers it contains (when they stand elsewhere in the book), the end of the previous text (source and current translation), the start of the next one, the glossary terms it found (with a "Maybe" list of terms seen only at the start of a sentence, where you decide whether the term or the everyday word is meant), and the voice briefs to read.
2. Read the voice briefs it lists (always `_author.md`), and any brief of a person who speaks or is named in the fragment that the script missed. Use the glossary's target forms exactly, also for terms the script did not list.
3. Translate the fragment following the rules, and write it to `work/<id>.md` as the same `[id]` blocks, in the same order, one block per source block. Then read your translation on its own, without the source, as a reader of the target language would read a book or an article written in it. Mark every sentence that sounds translated: a calque of the source's sentence structure, a noun phrase where the language uses a verb, an unusual collocation, a word order the language would not choose, a foreign term or inflection a native writer would avoid, a long phrase repeated where a native writer would shorten it after the first mention ("pisklęta" for "nowo wyklute pisklęta", a pronoun, the short form the glossary lists), the same carrier noun attached to an acronym again and again ("modele ViT" five times). Rewrite those sentences as a native writer would. Last, compare each rewritten sentence with the source: every fact, hedge and image is still there, nothing is added, each sentence still does its job (a definition stays a definition, an example an example, a question a question), and the author's own habits (short sentences, questions, labels, repetitions on purpose) are kept.
4. `save <id> work/<id>.md` (the path is relative to the book folder). It refuses a fragment whose ids do not match, and prints problems it finds (leftover source letters, wrong dialogue marks, missing placeholders, footnote markers or links, `...` written as three full stops, and for non-fiction numbers that are missing) and the fragment's style numbers, each next to the source's own rate where one can be measured (sentences and questions for every book: fewer sentences or questions than the source means merged sentences or rhetorical questions turned into statements). Fix the problems and save again. The style numbers are warnings about translated prose, not goals: before you revise a sentence for them, compare it with the source, and keep what the author does on purpose (step 6.2 says more).
5. Add any translator notes to `notes/chapter-NN.md` under a `## <id>` heading for the fragment (format in the rules file).

Work through the book without stopping, unless the user asked for a part only ("translate chapters 1–3"). Every few chapters, give the user a one-line progress update. If the context grows long, finish the current fragment, save, and continue: all state is in files, so nothing is lost.

For a long book you may translate chapters in parallel with subagents. Finish and review `glossary.md` and `voices/` first, and do not edit them while subagents are working; if a brief must change, tell each running subagent. Give each subagent the book folder, the chapter's fragment ids, and tell it:
- read `references/translation-rules.md`, `style-sheet.md`, `glossary.md`, `voices/_author.md`, `voices/_cast.md` and the voice briefs, and use `fragment` and `save`;
- write notes only to its own chapter's `notes/chapter-NN.md`;
- do not run `check`, `mark`, `export` or `prepare`, and do not edit `glossary.md`, `style-sheet.md`, `voices/`, `passages.md` or other chapters; report new terms and brief problems back instead.

The first fragment of each chapter then has no translation for the previous chapter's end; that is acceptable. Run `check` yourself when the subagents are done, and read a few passages of each subagent's chapter against the briefs.

Run `mark translation done` when `status` shows every fragment translated. For a run of some chapters only, leave the step as it is: `status` shows which chapters are translated, and `check` records which chapters it last checked.

### 6. Check

1. `check` (or `check 1-3` for some chapters) writes `check-report.md`: untranslated paragraphs, leftover source-language letters, wrong dialogue marks, markdown escapes, missing placeholders, footnote markers and links, numbers (non-fiction), glossary terms whose agreed translation is missing (grouped per term; special passages that passed are left out), and style numbers per chapter against the app's targets and the source's own rates. It also builds `notes.md` from `notes/`.
2. Fix real problems in `translation/chapter-NN.md`. A glossary warning can be a false alarm (a pronoun, another name for the same person, the head word of a longer term, a verb form of a noun term, an everyday word that shares a form with a term): read the paragraph before changing it, and never rewrite a good sentence only to fit the term's full form; add the short form to the row instead. A term that gives false alarms in every chapter needs a better glossary row (see the Match column in the glossary rules). The style numbers are warnings, not goals. Before revising, compare with the source: where the author does the same thing on purpose (a run of short sentences, a repeated word, ellipses where a thought breaks off, long sentences in an argument), keep it and leave the number above the target. Preserving the author's and the characters' voices comes before passing a target. Revise only what the translation created: the report lists the paragraphs with the most pronoun openers; revise those runs first, rather than single sentences anywhere, and follow the rules file's advice against a new pattern (the same name or participle opening sentence after sentence). The sentence count next to the source's shows whether the translation merged or split many sentences; a large gap is worth a look at the author's rhythm.
3. Check the special passages: steps 3 and 4 of [references/special-passages.md](references/special-passages.md).
4. Run `check` again, then `mark check done` (for a partial run, leave it; `status` shows the last check). Report to the user: the problems fixed, what is left, the passages that were corrected or failed, and the notes in `notes.md` that need the author.

### 7. Export

`export` writes `export/<translated-title>.md`, plus `.docx` and `.epub` when `pandoc` is installed (on a Mac: `brew install pandoc`). Fiction chapters are headed with the target language's chapter word and number ("Chapter 3", "Kapitel 3"), with the POV name and epigraph under it; a non-fiction chapter is headed with its translated title, and its section headings stay headings. `--title "<translated title>"` sets the title if `prepare` did not. It refuses while paragraphs are untranslated; `export --draft` marks the gaps and adds `_DRAFT` to the file name. For a part of the book, `export --draft --chapters 1-3`. For a collection of posts or essays published one by one, `export --per-chapter` writes one file per chapter. Do not export a final version while a special passage has status `failed`, unless the user says so. Run `mark export done` and tell the user where the files are.

## Rules for working with the user

- Stop after the glossary and after the voices. These are the two review points, as in the app.
- Preserve the author's own voice, and each character's or quoted person's own voice, at every step: translating, revising after `check`, and fixing what the user flags. A fluent but generic version has failed, even if every check passes.
- The user's edits to `style-sheet.md`, `glossary.md`, `voices/` and `translation/` are their decisions. Do not overwrite them; if a later step seems to conflict with one, ask.
- If the user changes a glossary target form after translation started, replace the old form in `translation/` and run `check`.
- Keep messages to the user short and plain: what was done, what needs them, where the files are.
