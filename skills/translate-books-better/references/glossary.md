# Glossary

The glossary gives every name, place, term and invented word one agreed form in the target language, so the translation uses it the same way every time. It works for any pair of languages; the examples below are Polish → English. These rules come from the app's glossary prompts (`extract_glossary_prompt.py` and `review_glossary_prompt.py`). The app's files named here are in the [Mneme app repository](https://github.com/AgaMiko/mneme-book-translator).

## File format

`glossary.md` in the book folder holds one Markdown table. Keep the header exactly as below, because `mneme.py` reads the table by these column names. Do not put a `|` inside a cell.

```markdown
# Glossary

| Source | Forms seen | Type | Target | Alternatives | Notes | Status | Match |
|---|---|---|---|---|---|---|---|
| Kasia | Kasi, Kasię, Kaśka | character_name | Kasia | Kate | Ola's sister; Kaśka is a fond short form. | proposed | |
| Kamienny Most | Kamiennym Moście, Kamiennego Mostu | place_name | Stone Bridge | Stonebridge | Descriptive name: translate the image. | proposed | |
| Cienie | Cieni, Cieniami | organization | the Shadows | | A guild of spies. The ordinary word cień (a shadow) is NOT this term. | proposed | case |
```

- **Source**: the canonical form, the one the book settles on.
- **Forms seen**: other spellings, inflected forms, epithets and nicknames of the same thing, comma separated. Only names and forms of the term itself: not common nouns that refer to the character ("wuj", uncle, is not a form of Bartosz), because the check then expects the name wherever the word appears. The script matches each word of a form with case endings (a word of six letters or more may change its last letter and add up to four letters; a word of four or five letters may add up to two), so list irregular forms that change more than that (Polish "dzień" → "dnia", "sen" → "snu"). For a term of two or more words, list multi-word forms; list a single word alone ("sieci" for "sieć neuronowa") only where the text uses it alone for the term, and then give the row `exact`, or the word will match other terms that start with it ("Sieć drogowa").
- **Type**: fiction: `character_name`, `place_name`, `organization`, `lore_term` (invented magic, technology, artefacts, named creatures and events, in-world religion), `cultural_term` (real-world customs, food or dress a reader may not know), `specialized_usage` (an ordinary word with a special in-world sense), `other`. Non-fiction: `person`, `place_name`, `organization`, `technical_term` (a term of the field), `concept` (a term the author coins or defines), `work_title` (a book, article, film or law the text names), `event`, `cultural_term`, `other`. A `character_name` or `person` row calls up the voice brief of the same name.
- **Target** (older glossaries call this column **English**; both work): the one form the translation uses: the bare name or word, without a title or "House" ("Morwen", not "House Morwen"; put the title in Notes), so the check finds it in "the Morwens' seat". For a word whose target form changes irregularly, list the forms with `/`: `bind/bound`. Use `/` also for an accepted short form of a long name: `Common Redcap/Redcap`. For a target of two or more words, add the head word the text will often use alone (`neural network/network`, `research team/team`); otherwise `check` reports every "the network", and a translator may rewrite good sentences to fit the full form. The first is the main form; the check accepts any of them, with the target language's endings.
- **Alternatives**: other good options, so the reviewer can choose.
- **Notes**: what it is, in one sentence, and why this target form. Say when an ordinary word is NOT the glossary term (a literal object that shares a name with a lore term), and name near-synonyms in the source that must not take the term's target form (for "spell": "urok" is "charm"; for "guard": "warta" is "watch").
- **Status**: `proposed`, then `accepted` or `rejected` after review. Rejected rows are ignored by the script.
- **Match** (optional last column; leave it empty in most rows): `case` matches the forms only with the capitals as written, `exact` matches them without case endings, `case exact` does both. Use it for a term that is also an everyday word ("Cienie", the Shadows, a guild, against "cienie", shadows), so the script does not list the term in every fragment and the check does not flag every shadow. After building the glossary, run `terms <chapter>` on two or three chapters (on the only chapter, for a one-chapter text) and read where each short or single-word form matched: a term listed where it does not appear is matching an everyday word or another term, and needs `exact` or `case`. With `case`, a capitalised form that opens a sentence or a line is not counted, since the capital says nothing there: `fragment` lists it under "Maybe" for you to decide, and the check does not ask for it. The check wants the target form with its capitals too ("the Shadows", not "shadows"). A form inside a longer glossary term ("Most" in "Kamienny Most") counts only for the longer term.

## Starting from an existing glossary

If the user has a reviewed glossary from another book (the next book in a series, an earlier version of this manuscript, or a term base of the field for non-fiction), copy it to `glossary.md` in the book folder before this step, in the format above. Then build as below, with one difference: rows already marked `accepted` or `rejected` are the author's decisions. Never rename, rewrite or merge them away. Only add missing terms as `proposed`, and add new forms seen to existing rows. Read the new chapters for every name and nickname they add, including what one character calls another (a maid who calls the cook "Chochla", Ladle): such nicknames are names and get a row.

## Building it

Read the manuscript chapter by chapter (`source/chapter-NN.md`), whole chapters and not shortened previews: a name cut off by a preview ("Ola" from "Olimpia") becomes a false form. After each chapter, update `glossary.md` with what that chapter adds: new terms, new forms of existing terms, merges, and corrections. Keep a short private notepad in `work/glossary-notes.md` for things to watch (a spelling to confirm, a name whose role is not clear yet). For a long book, read several chapters in parallel with subagents and merge their rows; check the merged table for duplicates.

What to find: every surface form a reader of the target language needs a stable decision on. Fiction: proper names, invented or world-specific vocabulary, culturally loaded labels, and ordinary words used in a special in-world sense. Non-fiction: names of people, places, institutions and works; terms of the field; terms the author coins or defines; recurring key phrases of the argument. Skip generic description and words used in their everyday meaning.

- **Canonical form.** Prefer the form the manuscript settles on as the usual reference, even when the first occurrence was longer (a titled introduction, then the short name used afterwards).
- **Deduping.** If a spelling, epithet or nickname clearly belongs to a term already in the table, add it to Forms seen instead of opening a new row. When two rows are the same entity, merge them and keep the steadier heading.
- **Substantive updates only.** Change a row only when a later chapter changes its meaning or the translation strategy.
- **For readers who do not know the source language.** Descriptive place names and faction labels usually carry meaning first: give their image or role in the target language rather than keeping opaque source-language strings, except where the story clearly needs the exact source form on the page.
- Invented names (made up for the story) with letters the target language does not use may be adapted (an invented "Żmirk" → "Zhmirk"). Real names keep their own spelling, first names and their diminutives included (Polish "Zośka", "Jaś" stay as written, letters and all), and so do real places, or the established exonym of the target language (Warszawa → Warsaw, Varsovie). For names in another script, use the target language's standard transliteration and say which in Notes.
- When the source register is archaic, folkloric or slangy, let a matching texture show in the target where it fits the narrative voice.
- Titles of songs, chapters and in-world works should read like credible titles in the target language with the same emotional cue.
- **Non-fiction:** a term of the field takes the established term of the target language's field (check how standard references or textbooks in that language name it), not a calque; put a calque or the original in Alternatives. A real work with a published translation takes its published title; note the edition. A term the author coins keeps one translation, chosen so its parts carry the author's meaning; note whether the original should appear in brackets at first use. When the source names a concept with no established term in the target language (the author's own label), translate it descriptively, write "descriptive, no established term" in Notes, and add a term_choice note so the author can check it; never present an invented label as the field's term. A label that appears once, in one footnote, needs a row only if it has no established term or comes back elsewhere.
- **Non-fiction: key words of the running examples.** The words a chapter keeps returning to in its examples and argument (the bees a beekeeper counts, the hives, the samples) get a row even when they are everyday words, so the translation calls one thing by one name ("hive" throughout, not "hive" and "beehive"). Mark such a row `exact` or `case` if the word is short.
- When related word families appear (shared roots across roles or processes), line up the target forms so the kinship stays visible, and fix earlier rows if a later chapter shows a link you missed.
- When several target options are all defensible, pick one default, put the others in Alternatives, and say briefly in Notes how they differ.

## Reviewing it (before showing it to the user)

Go through the proposed rows once more and decide each the way the author would. A term belongs in the glossary when the translation needs one fixed decision for it.

**Keep:** names of people, places, organisations, factions and creatures, and the nicknames characters use for each other; terms of the field and terms the author defines (non-fiction); invented words and coinages; titles of in-world books, songs and works, and quoted sayings, prayers or mottos, even when they appear only once; words a character uses to name what they are, and recurring slurs or labels for a group ("przybłęda", stray; "Bezimienni"); words used in a special in-world sense, and named concepts where several renderings are possible and consistency matters.

**Remove:** descriptive phrases, adjectives and verb phrases ("data-hungry", "easy to spot"): they change form with the sentence, so a fixed target gives false warnings; everyday words whose translation is simply the dictionary word (a sword, darkness), except the key words of a non-fiction chapter's running examples (see above); descriptive phrases and sensory descriptions that are not names; ordinary objects, foods and actions; generic ranks and roles used as common nouns (a general).

**Merge** only when two rows refer to the same person, place or thing: another name, an epithet, a short form, or the same term in another grammatical form. Similar meaning is not enough.

Also remove forms that do not belong to the term (another character's nickname), and fix a target form that is clearly wrong.

Also decide the translated title of the book with the user if it is not set; it goes to `export --title`. The book's own title needs no glossary row when the title is set there.

Then show the user a short summary: how many terms by type, the rows you are least sure about (titles of in-world works, named abilities that read like descriptions, everyday words that might carry a special sense, merges of a name with an epithet; non-fiction: terms where the field has competing translations, and published titles you could not confirm), and the choices with strong alternatives. The user edits `glossary.md` directly or tells you what to change. When the user is happy, set the kept rows to `accepted` and run `mark glossary reviewed`.

## Changing a term later

If the user changes a target form after fragments are translated, search `translation/` for the old form and replace it, then run `check` again.
