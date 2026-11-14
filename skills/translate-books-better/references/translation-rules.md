# Translation rules

Read this file and the book's `style-sheet.md` before translating the first fragment of a session, and keep to them for every fragment. The rules come from the one-step translation prompt of the Mneme app (`backend/app/generation/prompt_manager/prompts/translate_fragment_prompt.py`: `RULES_CORE`, `STYLE_SHEET` and `ONE_STEP_TASK`), written for any target language. "The target language" is the one in `mneme.json`; "the author" is the writer of the source. The app's files named here are in the [Mneme app repository](https://github.com/AgaMiko/mneme-book-translator).

The "voice briefs" are the files in `voices/` (`_author.md` for the author, one file per character or quoted person). The "glossary" is the accepted rows of `glossary.md`.

## Translation rules (all books)

1. **Translate meaning, not words.** Every piece of content in the source (each event, image, fact, argument, line of dialogue and feeling) is in the translation, and the translation adds no content the source does not have. Wording and sentence structure are free: words, clauses and sentences do not need to match the source one to one. Do not add content to make the text flow (no "easy now", "trust me", "my friend", no "in other words" or "of course" unless the source has them), and no images, details, examples or stronger wording than the source has; better flow comes from restructuring what the source says.

2. **Idiom for idiom.** Use the target-language idiom that does the same job, not a word-for-word copy.

3. **Living images.** If a source image sounds old or odd in the target language, use the image its writers use today, unless the author's voice is old-fashioned on purpose.

4. **The target's own register habits.** Each language has its own balance of plain and learned words, of verbs and nouns, of short and long sentences. Follow what published books of this kind do in the target language, not the source's habits. (English fiction prefers short plain words where a Slavic or Romance source uses Latinate ones casually; German and French tolerate longer noun phrases than English.)
   **Exception:** when a voice brief names a register (Latinate, clinical, elevated, archaic, academic, broken), follow the brief for that voice: a character who speaks in clinical terms keeps them; an author who writes in long academic periods keeps them.

5. **Verbs over abstract nouns**, where the target language prefers them (English does). Break long abstract noun chains into verbs.

6. **Spoken forms in dialogue** that the target language uses in speech (contractions in English, colloquial forms in other languages), unless the voice brief says otherwise (formal, ritual or archaic speech).

7. **Names in their glossary form.** If the source changes a name's ending by case or adds a suffix to it, still write the glossary form, and inflect it as the target language does (English: possessive 's; Polish, German, Czech: the case endings the target grammar needs). Short forms the glossary lists are separate names; keep them as they are.

8. **Glossary terms.** For every glossary term in the source, use the glossary's target form exactly. Do not vary it. Keep a term's target word for the term: where the source means the everyday thing, choose another word, so the reader does not take it for the term (if "bind" is the magic, a nurse who ties a bandage does not "bind" it). A term's notes may say when an ordinary word is NOT the glossary term. For a new name or term in the same family as glossary terms, follow the same strategy, and report it as a term_choice note.

9. **Voices.** The source text comes first: translate what the author or the character says, with nothing added or lost. The voice brief guides *how* you say it: which words to reach for and how to build the sentence, so each voice keeps its register and sounds unlike the others. Do not add markers the source line does not carry. A brief may end with a short sample in the voice: use it to hear how the voice sounds, never copy its phrases. (Approved test translations in `voices/_samples.md` translate real lines and may be reused for those lines.)

10. **Author placeholders** (xxxxxxx, [xxxx]) are copied exactly and reported as placeholder notes.

11. **Source typos.** Translate an obvious typo as the word that was meant. If you had to guess what was meant, add a source_typo note. Do not report single-letter slips. A misspelt name ("Bartsoz" for Bartosz) is written in its glossary form, with no note.

12. **No anachronistic idiom** in narration ("light years", "on the same page", "reach out" in a pre-modern world), unless the source has the same.

13. **The style sheet.** Spelling, punctuation, quotation and dialogue marks, numbers, units, dates and headings follow `style-sheet.md`.

## Fiction

- **Free indirect thought** stays in the narrative tense. Only direct thought is in italics, as in the source.
- **Dialogue** uses the target language's marks from the style sheet (English: quotation marks; Polish, French, Spanish, Russian: dashes, as the style sheet says). Change the marks, never the order of speech and tag.
- **Units** in narration follow the style sheet (English fiction set in a pre-modern world: paces, feet, miles; elsewhere often metric). Measurements on charts, documents and instruments stay as in the source. Round converted numbers naturally ("a good five paces"), don't give false precision.
- **Chapter headings:** a `[title]` paragraph may hold the point-of-view name, the chapter line (number and title), and an epigraph with its attribution line. Translate all of it and keep its line breaks; the chapter word becomes the target's word from the style sheet. Epigraphs keep their own register; attribution lines start with a dash.
- **Scene breaks:** keep a "***" paragraph as "***". If a scene break carries a point-of-view name ("*** Ola"), write "***" and put the name in the same paragraph on a new line in italics: "***\n*Ola*".
- **Mind-to-mind speech:** the point-of-view character's words in the speech marks, the other speaker's words in italics, as in the source.
- **Letters, scripture and quoted documents** keep their own register and their italics.

## Non-fiction

- **Popular non-fiction reads like a native writer's prose.** A blog post or a science column in the target language uses that language's usual collocations and verbs, not the source's sentence structure: "potrzebują więcej danych", not "wymagają większej ilości danych"; "trening opierał się na…", not "z naciskiem na…". Read each paragraph as a reader of that language would; rebuild what sounds translated, without losing a fact or a hedge.
- **Argument first.** Each sentence keeps its job: a definition stays a definition ("which means that a human text is wrongly flagged" does not become a claim about how many texts are flagged), an example stays an example, a question stays a question. Every claim, qualification and hedge stays exactly as strong as in the source: "may", "often", "some studies suggest" do not become "does", "always", "studies show". Do not simplify, explain or correct the author's reasoning; if a statement is wrong or out of date, translate it and add an ambiguity or continuity note.
- **Terminology.** Use the established term of the field in the target language (from the glossary), not a literal translation. A term the author coins or defines keeps one form throughout.
- **The original term in brackets** ("(ang. reversal curse)") is an addition: give it only where the style sheet asks, once per term, for a field term a reader may want to look up, and never inside other brackets or quotation marks. Where the source already names the term in the target language, that counts.
- **The author's labels** ("My take:", "Note:", "TL;DR", "Paper:") stay labels, in the same place, translated as labels ("Moje zdanie:"), not turned into a sentence.
- **Quotations from other works.** If the quoted work has a published translation in the target language, use its wording when you know it, and add a note naming the edition; otherwise translate the quotation and say in a note that it is your translation. Never invent a published wording. Titles of works: the published title in the target language, if one exists; otherwise translate the title and keep the original in brackets the first time, as the style sheet says. A title that is the text of a link ("[Reverse Training to Nurse the Reversal Curse](…)") stays as written: the reader clicks through to that title.
- **Numbers, dates, names of people and places** stay exactly as in the source; write them in the target's format from the style sheet (decimal comma or point, date order, thousands separator). Convert units only if the style sheet says so, and then keep the original in brackets.
- **Glosses that name the target-language word.** When the source glosses a term in the target language ("uczenie nadzorowane, po angielsku supervised learning" in a book translated into English), the gloss has no job in the translation: write the target term once, as the term, and drop the source-language term and the "in English" phrase. Keep glosses that name a third language. Record the choice in the style sheet.
- **Footnotes, endnotes, links and references.** Keep every footnote marker (`[^1]`) in the same sentence, and translate the note itself; keep links unchanged; in bibliographic references translate only the words the target's citation style translates ("p." for "s.", "ed." for "red."), never the titles of works in other languages.
- **Code.** Code blocks, commands, file names and the prompts inside code stay exactly as written. Program output shown as an example (a transcript, a model's answer) stays in the language the program produced it in, so it still matches the code above it; list those paragraphs in `passages.md` as a `kept` passage, so `check` does not report them as untranslated; add a translated gloss after it only if the style sheet asks for one. A link whose address is missing in the source stays as text, with a note.
- **Groups that speak as "we"**, where the target marks gender in the plural (Polish "zebraliśmy" or "zebrałyśmy"): ask, as for the author; the mixed form is the default only when the user says the group is mixed.
- **Headings** (`## Section`) are translated as headings, short, in the target's own heading style; keep their level.
- **The author's address to the reader** (I, we, you, the impersonal form) stays what it is in the source, unless the target language's conventions for this kind of book differ and the style sheet records the choice.
- **Lists, tables and block quotes** keep their structure, one paragraph id each.

## Your task: translation (one pass)

Translate the source paragraphs into fluent, natural prose in the target language, the way this author would have written the passage if the target were their language, so it reads like a published book and not like a translation. The author's voice is what you carry over: do not replace it with a standard style of the target language. There is no editor after you: what you save is the final text, so it must survive two readings, one as a native reader with no source in sight, and one against the source. Account for every sentence of the source: nothing dropped, nothing added. Apply the rules, the style sheet and the glossary.

Work from the meaning, not the words. Read each source paragraph, understand what it says and how it says it, then write the best version of that in the target language. You may reorder, merge, split or rebuild sentences, change parts of speech, and replace any phrase that sounds translated with what a native writer would say. Keep:
- the meaning: every event, image, fact, argument, line of dialogue and feeling, with nothing added and nothing lost;
- the author's style, as `voices/_author.md` describes it: tone, register, pace, how plain or ornate the prose is, the point of view and the mood, and the habits that make the prose theirs (a favourite kind of comparison, a dry aside, the way they end a scene or a section, the way they use a fragment, a question or a list);
- each character's or quoted person's voice, as the briefs describe, including what is theirs alone: a pet phrase, a tic, a way of joking or of addressing people. Carry such a feature over every time the source has it.

The advice below fixes habits of translated prose. It never overrides the author's own habits: where the source does something on purpose (a run of short sentences, a repeated word, ellipses in narration, a long period in an argument), keep it, even if a style number then goes over its target. Tell a habit from grammar: in a language that drops the subject (Polish, Czech, Spanish, Italian, Japanese), a run of verb-first sentences is grammar, not a choice, and the habit to keep is the run of short action sentences, not the missing pronoun. Every point below that asks you to change something has this exception. Never meet a target by adding words or by dropping a verb the source has.

When the fragment is written, read it twice. First as a native reader, without the source: rewrite every sentence that sounds translated. Then against the source: nothing lost, nothing added, the author's habits kept.

- **Sentence openings.** Avoid runs of the same opener that the translation created ("She… She… She…", "Er… Er…", "The author… The author…"), unless the source repeats on purpose. Vary with the name, a participial or prepositional opener, object-first order, merging two short sentences, or starting with the action. Don't fall into a new pattern: at most one participial opener per paragraph, and keep simple "She did X" sentences where they read best. Every sentence keeps its verb, and its actor: do not turn "She shook the vial." into "A shake of the vial." or "The vial was shaken." unless the source does.
- **Sentence rhythm.** Translating sentence by sentence tends to give runs of sentences of the same length; mix short, medium and long ones as the author does in the source. Keep the author's deliberate effects (a run of fragments, a long breathless sentence, a build-up in an argument).
- **Word repetition.** Do not use the same word again within a few lines where the source does not repeat. A long phrase the source repeats ("newborn chicks", "Vision Transformers") may be shortened after its first mention in a paragraph, as a native writer would; the check accepts the short forms a glossary row lists, so list them. The source may avoid repetition through inflection; the target may need a synonym, a pronoun or a rebuilt sentence. Keep a repetition where the source repeats on purpose (anaphora, a refrain, emphasis, a defined term), and keep glossary terms and names exactly.
- **Meaning wins over variety.** A precise word used twice is better than a synonym that shifts the meaning: soldiers are not "guards", patients are not "sick men", a defined term is not paraphrased. Do not add images, details or intensity to vary a sentence.
- **Merge or split sentences** for the target's rhythm. Break up long chains of clauses carried over from the source, unless long periods are the author's style.
- **Fix stiff or word-for-word phrases.** No modern slang in narration unless the author writes that way.
- **Ellipses.** Keep them in dialogue where a speaker trails off or falters, where the point-of-view character's thought breaks off, and at a real moment of dread; trim them from neutral narration. Remove an ellipsis with punctuation only, never by adding words (": all of it", "wasn't it?"). Write the ellipsis as the style sheet says (in most languages one character, `…`).
- **Dashes.** Follow the style sheet. In English, em dashes only for interruptions and sharp asides; use commas, colons, semicolons or full stops elsewhere.
- **Dialogue tags.** Vary them and prefer action beats; don't repeat the same verb of speaking within a few lines.
- **Who speaks.** When two people of the same gender talk, make sure the reader can tell who speaks. You may add a minimal clarifying beat (a name, "he said"). Report every such addition as an added_clarification note, as well as any other added word that settles who or what is meant.
- **Stock phrases** of translated or machine prose (English: the weight of, a beat, ghost of a smile, a flicker of, a wave of, couldn't help but, suddenly; the same kind of filler in other languages): replace with something concrete, or cut.

Add a note only when the author needs to know or decide something, and report every added clarifying beat as an added_clarification note.

Return one paragraph for each source paragraph, with the same id, in the same order. Never merge or split paragraphs across ids.

## The style sheet

Write `style-sheet.md` in the book folder at step 1, in the language of these instructions, about one screen long. It records how the target language's conventions apply to this book, so every fragment and every subagent writes the same way. Cover:

- **Language and variant:** e.g. British English (-ise, -our, "towards"), American English, Brazilian Portuguese.
- **Dialogue and quotation marks:** the target's marks for speech and for quotations inside quotations (English: "…" and '…' or the reverse for British houses; German „…“ and ‚…‘ or »…«; French « … » with dialogue dashes; Polish „…” and dialogue dashes; Spanish and Russian dialogue dashes). Fiction: how speech and tags are punctuated.
- **Ellipsis and dashes:** one character `…`; which dash for asides and ranges.
- **Numbers, dates, units:** decimal and thousands separators, date order, numbers written as words or digits, units kept or converted (non-fiction: keep the source's numbers; fiction: what the narration uses).
- **Headings:** the chapter word ("Chapter", "Kapitel", "Rozdział") and whether chapters are numbered in words or digits; non-fiction: heading capitalisation.
- **The author's grammatical gender**, where the target language marks it in the first person (Polish "napisałam" or "napisałem"): ask the user; never guess it from a name.
- **Foreign names and acronyms:** whether they take the target language's endings ("ViT-y", "LLM-ów") or stay as they are ("ViT", "modele LLM"). Popular science often leaves model names and acronyms uninflected. An uninflected acronym needs a noun to carry the case ("modele ViT"); do not attach the same noun every time: after the first mention, vary it as a native writer would ("te modele", "transformery", a pronoun, the plain acronym where the case is clear). A glossary row records the term, not a fixed carrier phrase.
- **People in general:** how a generic person is referred to ("the doctor… they", "he", "he or she", alternating), decided once; a generic masculine in the source is grammar in many languages, not the author's choice.
- **Forms with two accepted variants:** decide each once for the whole book: "data is" or "data are", the serial comma, "OK" or "okay", "email" or "e-mail", spelled-out or digit numbers. A house style named in the sheet ("Chicago") must agree with these choices.
- **Address forms:** how titles and polite address come out, the reader included (Polish capitalises "Wy, Was, Wam" when an author or letter addresses readers directly), both with a name ("pan Nowak" → "Mr Nowak") and without one ("pan", "pani" alone, a formal verb form, "mistrzu"): which English word, or none.
- **Consistency with earlier work:** if chapters of this book are already translated (an earlier run, a sample), the style sheet records their choices (quotation marks, units, address) so new chapters match them.
- **Names and titles:** whether foreign names keep their diacritics (they do, unless the glossary says otherwise), how titles of works are written (italics, published titles).
- **Non-fiction:** citation and footnote style (abbreviations such as "p."/"S."/"s.", "ed.", "et al."), how the author addresses the reader, and whether terms are introduced with the original in brackets.

Example, for British English fiction:

```markdown
# Style sheet: The Stone Bridge (Polish → British English, fiction)

- Spelling: British (-ise, -our, colour, grey, towards). Words: "round" as well as "around".
- Dialogue: double quotation marks; single for a quote inside speech. Source dashes become quotes; tags keep their place.
- Ellipsis: one character, no space before. Em dash without spaces, only for interruptions and sharp asides.
- Units: narration in paces, feet, miles; documents and instruments as in the source (40°C).
- Numbers: words up to one hundred in narration; digits on documents.
- Headings: "Chapter 1"; epigraph attribution starts with an em dash.
- Names: as in the glossary; Polish names keep their letters unless the glossary changes them.
```

## Translator notes

The rules above ask for notes in some cases. Add each one as a line in `notes/chapter-NN.md` (the fragment's chapter), under a heading for the fragment, in paragraph order. `check` joins these files into `notes.md` for the author:

```
## 03-2
- [p014] source_typo: "…" read as "…" (the source has an obvious slip).
- [p020] added_clarification: added "Ola said" so the reader knows who speaks.
- [p031] quotation: Rilke quoted from the published translation by …; or: my translation, no published one found.
```

Kinds: `source_typo`, `continuity`, `ambiguity`, `wordplay`, `placeholder`, `added_clarification`, `term_choice`, `quotation`. Add a note only when the author needs to know or decide something.
