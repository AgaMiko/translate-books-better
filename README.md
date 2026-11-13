# translate-books-better

An agent skill for translating a whole book with Claude Code: a novel, short stories, or non-fiction such as essays, memoir, popular science or history, from any language into any other. It follows the workflow of the [Mneme app](https://github.com/AgaMiko/mneme-book-translator) without the app: no Docker, no database and no API keys of your own. Claude Code does the translation on your Claude plan.

## Why not just ask Claude to translate?

Claude translates a single chapter well when you just ask. The trouble starts when a book is translated chapter by chapter: each request decides names, terms and style on its own, nothing remembers what earlier chapters chose, and nobody tells the author what was changed. The skill writes those decisions down once and holds every chapter to them.

We compared the two on the same chapters: a plain request ("translate this chapter") against a full run of the skill, on one chapter of a novel and one chapter of a non-fiction book, both from Polish into English.

**The novel chapter (fantasy, into British English):**

| | Plain request | With the skill |
|---|---|---|
| Names and terms that differ from the chapters already translated | 6 | 0 |
| Sentences (the source has 353, mostly short) | 332: short sentences merged | 354 |
| Dialogue marks | single quotes | double, as in the chapters already translated |
| A teacher's mocking form of address | dropped | kept, as his voice brief asks |

Two of the plain version's six differences show why this matters: an invented herb got the English name of a real poison, and a character's name was changed into the mythological figure it resembles. The chapter also opens with a short rhyme. The skill writes down the rule a translation must keep (two lines, two rhyming pairs, the images it carries) and checks the translation against it.

**The non-fiction chapter (popular science, into American English):**

- The running example's key word switched between two synonyms in the plain version. The skill gives it a glossary row, so it is one word throughout.
- The source glosses its terms in English ("Polish term, *in English* term"). The skill drops the gloss, which has no job in an English book, and writes the term once.
- The plain version silently corrected one of the author's cross-references. The skill keeps the author's words and leaves a note, so the author decides.
- Each run ends with a notes file for the author: source typos, names that may be wrong, grammar the target language cannot show.

**What the plain request does well.** Its English is fluent, and sometimes it finds the more natural phrase (an idiom where a skill run chose a plainer word). The skill does not make the prose more beautiful. It makes a book consistent with itself, faithful to the author's habits, and open about every decision.

## How it works

The skill takes Claude through seven steps, the same ones as the Mneme app. Every decision is written to a plain file in the book folder, and the next steps read those files.

1. **Split.** A helper script splits the manuscript (`.docx`, `.md` or `.txt`) into chapters, and for non-fiction into sections, then into fragments of about 1,200 words. Each paragraph gets an id (`[p017]`), so every note and check can point to it. Claude then writes `style-sheet.md`: spelling variant, quotation and dialogue marks, numbers, address forms ("pan Nowak" → "Mr Nowak"), and the choices with two accepted variants ("data is" or "data are").
2. **Glossary.** Claude reads the book chapter by chapter and writes `glossary.md`: one row per name, place, invented word or field term, with the one form the translation uses and why. Then it **stops for your review**.

   | Source | Forms seen | Type | Target | Notes |
   |---|---|---|---|---|
   | Cienie | Cieni, Cieniami | organization | the Shadows | A guild of spies; the ordinary word "cień" (a shadow) is not this term. |

3. **Voices.** Claude writes a brief for the author's own voice and for each character (or quoted person) who speaks. Each brief counts what runs through that voice and names what belongs to it alone: "bare orders in 12 of 13 lines; calls his nephew by a pet name in 3", "a quarter of the author's sentences are five words or fewer; keep them short". It translates a short test passage per voice, then **stops for your review**.
4. **Special passages.** Verse, letters that hide a message in their first letters, plot wordplay, refrains and quotations from other works each get a written rule the translation must keep. A helper prints the first letters of a passage, so an acrostic is checked by the script, not by eye.
5. **Translate.** For each fragment the script prints the source, the end of the previous fragment in both languages, the glossary terms and footnotes it contains, and the voice briefs to read. Claude translates it in one pass and saves it; the save checks the paragraph ids and reports problems at once. Long books can be split between subagents, one per chapter.
6. **Check.** `check` writes a report per chapter (see below). Claude fixes the real problems, checks the special passages against their rules, and builds `notes.md` for the author.
7. **Export.** The book, or chosen chapters, to Markdown, and to DOCX and EPUB when pandoc is installed.

You can stop at any point, edit any file (the glossary, a voice brief, a translated paragraph), and continue later: your edits are treated as decisions and kept.

## What the checks catch

- paragraphs left untranslated, and source-language letters left in the translation (names the glossary keeps, such as "Kraków", are allowed);
- dialogue marked the wrong way for the target language;
- footnote markers, links and (in non-fiction) numbers missing from a paragraph;
- glossary terms whose agreed translation is missing, grouped per term;
- style numbers next to the source's own: sentences and rhetorical questions against the source, and for fiction sentences opened with "She/He", ellipses and em dashes. The numbers warn about habits of translated prose; where the author does the same on purpose, the skill keeps it.

## Install

```bash
npx skills add AgaMiko/translate-books-better
```

Or as a Claude Code plugin:

```
/plugin marketplace add AgaMiko/translate-books-better
/plugin install translate-books-better@translate-books-better
```

Or copy the skill folder into your skills folder:

```bash
git clone https://github.com/AgaMiko/translate-books-better
cp -r translate-books-better/skills/translate-books-better ~/.claude/skills/
```

The helper script needs Python 3.10 or later. With [`uv`](https://docs.astral.sh/uv/) it installs `python-docx` by itself; with plain Python, run `pip install python-docx` to read `.docx` files. For `.docx` and `.epub` export, install [pandoc](https://pandoc.org).

## Use

Start Claude Code in the folder with your manuscript and ask, for example:

- "Translate my-novel.docx from Polish into English."
- "Translate essays.docx from German into Spanish; it is non-fiction."
- "Translate chapters 1–2 of my-novel.md into British English."

The command is `/translate-books-better` (as a plugin, `/translate-books-better:translate-books-better`). To continue a run, open Claude Code in the book folder and ask it to continue the translation. To skip the two review stops, say so ("review the glossary and voices yourself").

A whole book uses a large share of a plan's limits: Claude reads the book about three times (glossary, voices, translation) and writes it once. Try one or two chapters first.

## The book folder

```
mneme.json                 progress: chapters, fragments, steps (written by the script)
source/chapter-NN.md       the source, one [id] block per paragraph
style-sheet.md             the target language's conventions for this book
glossary.md                names, places and terms, one agreed translation each
voices/                    _author.md, one brief per speaker, test passages
passages.md                special passages and their rules
translation/chapter-NN.md  the translation, same [id]s as the source
notes.md                   notes for the author (typos, ambiguities, choices to confirm)
check-report.md            the last check
export/                    the finished book
```

## Languages

The helper script knows the letters, chapter words, pronouns and dialogue marks of English, Polish, German, French, Spanish, Italian, Portuguese, Dutch, Swedish, Czech, Slovak, Hungarian, Russian, Ukrainian, Kannada, Japanese and Chinese. Other languages work too, with fewer automatic checks; add an entry to `LANGUAGES` in `skills/translate-books-better/scripts/mneme.py` for full checks.

The skill was tested most on Polish into English, fiction and non-fiction. Other pairs follow the same rules but have had less testing.

## Repository

```
skills/translate-books-better/   the skill: SKILL.md, references/, scripts/mneme.py
.claude-plugin/                  plugin and marketplace manifests
```

## Author

[Agnieszka Mikołajczyk-Bareła](https://github.com/AgaMiko)

## License

Apache-2.0
