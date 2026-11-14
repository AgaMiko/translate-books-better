# Voices

A voice brief tells the translator how a voice should come across in the target language: the author's own voice, and each character's (fiction) or each quoted person's (non-fiction), so every voice keeps its register and sounds unlike the others. These rules come from the app's voice prompts (`build_voice_profile_prompt.py` and `cast_voices_prompt.py`) and from `docs/voice-pipeline-redesign.md`. Write the briefs in the language of these instructions; the samples in them are in the target language. The app's files named here are in the [Mneme app repository](https://github.com/AgaMiko/mneme-book-translator).

## 1. The author's voice (all books)

Write `voices/_author.md` first. `fragment` lists it for every fragment. It describes the narration (fiction) or the author's prose (non-fiction), from the source, with counts:

- sentence length and rhythm: how often a run of short sentences or fragments, how long the long ones get, where each is used (action, reflection, argument);
- register: plain or learned words, technical terms, archaic or regional words, how often;
- habits that make the prose the author's own: a kind of comparison, a dry aside, rhetorical questions (`inner` counts narration questions), lists of three, ending a scene or section on a short line, ellipses where a thought breaks off, parentheses, direct address to the reader;
- non-fiction: how the author speaks to the reader (I, we, you, the impersonal form), how sure the claims sound (hedges), how much humour, how examples and stories are introduced, how quotations are woven in;
- fragments used as punch lines ("Tym razem przynajmniej z mapą."): count them; in the translation they stay fragments, not full sentences;
- what to keep against the target's habits, and what is grammar only (in a language that drops the subject, verb-first sentences are grammar; the run of short action sentences is the habit).

Count from the text (`inner` lists italic passages and narration questions per chapter; for sentence length, read two or three whole chapters). Cite evidence by paragraph id: `find "<words>"` prints the id of the paragraph that contains them. Same format as below, about 150 words, with a short sample in the target language.

## 2. Collect each speaker's lines

Fiction, and non-fiction with interviews or long quoted speech. Run `mneme.py dialogue --skeleton` (or `dialogue 1-4 --skeleton` for some chapters) to write `work/lines-draft.md`: one line per paragraph that looks like dialogue, in book order, such as `- [03:p041] ? → ? | – Chodź tu…`. It finds paragraphs that start with a dash and paragraphs with quotation marks of any language. They are only candidates: many are titles, quoted phrases or thoughts. Plain `dialogue 3` prints the full paragraphs of a chapter when you need to read them.

For each line, replace `? → ?` with the speaker and the listener (the glossary's target names), for example `Kasia → Ola`, or with `thought` or `not dialogue`. Read the narration around it (in `source/`) for who is talking when there is no speech tag. A speaker with no name gets a short role that stays the same across their lines (`Fisherman 1`, `Older sailor`, `Girl at the well`), so their lines can get a brief of their own; use `Unknown` only when even the role is unclear. For a long book, use subagents per group of chapters, each on its own draft file, and join them. Then run `dialogue --group`: it writes `work/lines.md`, one section per speaker, each line with its id, listener and text, for example `[03:p041] to Ola: – Chodź tu…`, and under each heading a count of lines, of lines of four words or fewer, and of lines with `!`, `?` and `…`.

For a point-of-view character, also run `inner <chapters>` for the chapters in their point of view: it lists italic passages (direct thought, but also emphasis, titles and foreign words: decide which are thought) and narration paragraphs with a question.

## 3. Profile each voice (from all of its lines at once)

Read all of a character's lines in book order. Describe the voice across the book, not one scene: a feature seen once is a moment, not a voice. Every feature must be visible in lines you can cite. Do not project features from role, profession or class: a teacher who speaks with a village accent has a village voice.

Look for:
- emphatic particles, modal markers, sentence-final tags;
- deliberate non-standard spelling (eye-dialect) and non-standard grammar (a foreigner's broken cases, a child's syntax, dropped articles, tense confusion);
- signature patterns: tic phrases, hesitation markers, stutters, fragments, run-ons, repetitions;
- switching to other languages, and what it signals;
- stable sociolect by class, era, region or profession, in both vocabulary and sentence habits (the scientist hedges, the peasant is concrete, the soldier is terse, the courtier indirect);
- address forms (formal or familiar pronouns, titles, diminutives), and how others address them;
- changes of register with particular people or situations.

Describe speech from speech lines. Use thoughts to note where the inner voice differs in a way the translator should keep. For a point-of-view character, also describe the inner voice, however often they speak: their chapters are carried by free indirect thought, and what belongs to them alone (a self-command, an ironic aside, a habit of comparing people to things) is often found there and not in speech. Say which lines are thought. For a point-of-view character who rarely speaks, the inner voice is most of the brief.

For each feature, decide the move:
- **MIRROR**: carry it over directly (non-standard grammar, tics, signature phrases, stutters, fragments, repetition, switching language). The form may change (case errors in the source become article or preposition errors in English), but the brokenness carries over. Keep foreign phrases as they are, unglossed unless the original glosses them.
- **RECAST**: use an equivalent in the target language (source-specific particles and honorifics, archaic words, regional vocabulary).
- **WATCH**: name the trap (anachronisms, the wrong regional accent, stagey foreign accents, inline glosses, softening a sharp tone, expanding clipped orders, modern slang).

**Word order is not a marker.** In languages with free word order (Polish, Czech, Russian, Latin; verb-final clauses in German), an inverted order is ordinary speech or folk register, not broken grammar. Never mirror it as inverted syntax in a target with fixed word order ("itch it did", "Learned he is"): carry the register with the target's own country or old-fashioned grammar and words. Mirror word order only where the source speaker breaks the source language's own rules.

Eye-dialect is decided per character: sparse equivalent eye-dialect for a regional or class accent within the language (one or two marks per sentence); grammar errors, not phonetic spelling, for a foreign speaker's accent. Do not add tags the source does not carry ("…, he did", "as went").

## 4. Look at the whole cast, then write the briefs

First write `voices/_cast.md`: group the voices that could collapse into one in the target language (same register, rhythm and markers). For each group, say what separates them in the source lines, and name the target-language markers you will give each so they stay apart. Keep it short. Notes for one-scene speakers can go here too.

Then write one file per speaking character or quoted person: `voices/<target-name>.md`, where the file name is the glossary's target form in lower case with hyphens (`Old Marta` → `voices/old-marta.md`; other scripts are kept as they are). The script uses this name to list the briefs a fragment needs.

Before writing, read the character's lines word by word again and count how many lines carry each marker. `work/lines.md` gives a starting count of short lines and of `!`, `?` and `…`; count the voice's own markers yourself. What runs through most lines *is* the voice: the brief must say so plainly, with the count ("bare orders in 10 of 13 lines"), and the sample must show it. Do not describe a feature with "only", "always" or "nothing else" unless the count shows it. Keep apart what is occasional (eye-dialect in one scene) and what runs through most lines (dialect words and grammar).

Count a register (clinical, Latinate, archaic, rural vocabulary) by words, not by whole lines that sound like it: a speaker who uses one learned word in each of six lines has a learned register, even if no line reads like a lecture ("medical or Latinate words in 6 of 15 lines"). When a register shows in several lines, it is the character's register: the brief says it applies to all their lines, and the translator chooses that kind of word wherever the source line allows one. Do not tie it to the cited lines.

Give a target-language rendering ("X → Y") in a brief only for a feature that must come out the same every time: a pet word, an address form, a formula. Never translate a single real line in a brief, not even in the Voice text as an example: the translator copies such renderings as they are, mistakes included. The same applies to the sample: it shows a register, so it must not contain a tic or construction the character does not have in the source, must not paraphrase a real line, and must not add stage dialect that the source lines do not carry.

Format, about 100 words:

```markdown
# Old Marta

Source name: Marta (glossary). Lines: 34, chapters 2–11.

Voice: A village woman who speaks dialect in nearly every line (dialect words and non-standard agreement). In English, consistent country grammar and words in every sentence, readable, not phonetic spelling. Next to the healer she sounds plainer and older; never let her drift into neutral English.

In their voice (style only, don't reuse phrases):
"Them lot from the mill, they was never no good to nobody. You mind the goat and leave the talking to me."

Evidence: [02:p014] [05:p033] [09:p007]
```

- **Voice** (one or two sentences, then one or two tips): who this person sounds like (social position, education, profession, age, region), how plain or elevated the vocabulary is, how formal they are, the two or three source markers that carry the voice and what they become in the target language, what must not be lost, and how they differ from the nearest voice in their cast group. Then name what belongs to this voice alone and not to their type (a pet phrase, a tic, a way of joking, swearing or addressing people), with how it goes into the target language. A brief that would fit any other speaker of the same class or profession is not finished.
- **In their voice**: two or three sentences as this person would say them in the target language. Carry over what runs through their lines, at the same frequency (dense where they are dense). Something they could say in the book's world, but not a quote or paraphrase of their real lines, and no new plot facts. One sentence is enough for a voice with very few lines.
- **Evidence**: a few line ids, so the user can check the brief against the source.

The counts in a brief hold for the chapters it names (`Lines: 34, chapters 2–11`). When a later chapter has lines that do not fit a count (a statement from a speaker whose brief says every line is a question), the translator follows the source line and reports it; before the next chapters are translated, update the brief with the new lines and counts.

Leave out what applies to everyone (spoken forms in dialogue, natural idiom, no anachronisms).

**Minor speakers.** A speaker with no glossary name but a voice worth keeping (two village men in dialect, a guard who speaks in clipped orders) can get a brief too: `voices/village-men.md`, with a line `Matches: karczma, chłop, gospodarz` under the heading, listing source words that appear in their scenes. `fragment` lists the brief for any fragment that contains one of those words. `fragment` always lists `voices/_author.md` and `voices/_cast.md`, so short guidance for one-scene speakers can also go in `_cast.md`.

**Quoted pet words.** When another character quotes a character's pet word or phrase (Ola repeats Kasia's "Bajka" in her thoughts), add a line `Quoted in: 01:p020, 01:p022` under the brief's heading, with those paragraph ids. `fragment` then lists the brief for those paragraphs too, so the quote gets the same translation as the original.

**Non-fiction.** Most non-fiction needs only `_author.md`; a book with the author as its only voice needs no `_cast.md`. Add a brief for a person the book quotes at length or interviews (a witness, an expert, a historical figure whose letters are quoted), with the glossary type `person`, so `fragment` lists it. Short quotations need no brief.

## 5. Test the briefs, then stop for review

Translate one short passage per main voice with its brief, following `translation-rules.md`: for the author, a paragraph or two of narration or argument; for a character, 3–6 lines from a scene where they speak. Read the results together. Fix a brief when its passage is **flattened** (an educated speaker made casual, a plain speaker made literary, a rural voice made standard, an address form dropped, a pet phrase or tic lost, the author's short sentences joined or long periods chopped), **sounds like another voice**, or goes against the brief in another way. Never count it as a fault that the translation stays close to what the source says. Because the approved samples may be reused in the book, also check each one as a translation: nothing added, nothing lost, and every pronoun clearly pointing to the right person ("it has to fall on him" when two men are present is not clear). Read the one-scene speakers' notes in `_cast.md` against their source lines too, since they get no test passage.

Before you stop, read every brief once more for renderings of real lines (only pet words, address forms and formulas may have one) and for "N of M" counts that you have not checked against `work/lines.md`.

Put the test passages in `voices/_samples.md` (source, then translation) so the user can judge the briefs by their effect. If the user asked you to run straight through without stopping, review the briefs yourself instead: read each test passage against its source for the faults listed above (flattened, sounds like another voice, added or lost content), fix the brief where a fault comes from it, write one line per voice in `_samples.md` saying what you checked and changed, then run `mark voices reviewed` and go on. Otherwise stop: ask the user to read `voices/` and `voices/_samples.md` and edit or approve. When they approve, run `mark voices reviewed`. A brief the user edited is their decision: keep it faithful to their changes. The approved translations in `_samples.md` are translations of real lines: when you reach those paragraphs in the translation step, reuse them or improve them. This differs from the "In their voice" sample inside a brief, whose phrases are never copied. Do not change `voices/` while subagents are translating.
