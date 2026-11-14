# Special passages

A special passage is a run of paragraphs whose wording follows a rule, so a translation of the meaning alone breaks it. These rules come from the app's `special_passages_prompt.py` and `docs/step6-special-passages.md`. The app's files named here are in the [Mneme app repository](https://github.com/AgaMiko/mneme-book-translator).

| Kind | Rule the translation must keep |
|---|---|
| `verse` | Poem, song, rhyme, chant, prayer, spell or riddle: number of lines, rhyme scheme, line length. |
| `hidden_message` | Letters or words spell a message (often the first letters of sentences, lines, paragraphs, words or marked words). |
| `wordplay` | A pun, anagram, riddle or play on a name that the plot, a joke, an argument or a later line depends on. Ordinary figures of speech do not count. |
| `kept` | Text that stays in the source language on purpose: program output shown next to its code, a quotation the author gives in the original, a label of a user interface. The rule is "leave as written"; `check` does not report these paragraphs as untranslated. |
| `refrain` | A phrase the text repeats on purpose (a title question asked again at the end of the chapter, a motto, a catchphrase), maybe reworded the second time: the same wording wherever it repeats exactly, and a recognisable echo where it comes back reworded or as reported speech. |
| `quotation` | A quotation from another published work (a poem, scripture, a philosopher, a law): the published translation in the target language if one exists, or the translator's own, said in a note. Mostly non-fiction; fiction that quotes real works too. |

## 1. Scan (before translating)

Go through the chapters and list candidates in `passages.md`:

- **verse**: set in lines, as separate paragraphs or line breaks inside one paragraph. An epigraph in the chapter heading counts.
- **document**: a letter, note, inscription or list quoted in the story that could hide a message. Signs: the story says it is coded, strange or worth reading twice; a character studies it or counts letters; its sentences are oddly regular; some words are marked. List every quoted letter or note of several sentences even without such signs: a reader looking at meaning does not notice an acrostic.
- **wordplay** as above.
- **quotation**: a quoted passage from a real work longer than a phrase, a quoted poem or song, a motto from a real author. Note the work, the author and, if you know it, a published translation in the target language. Never invent a published wording: if you do not know it, the rule is "translate, and add a quotation note saying so".
- **refrain**: a phrase that comes back, word for word or reworded ("Po co ci to?" as a heading, then "zapytał mnie, po co mi to" at the end). Do not put a refrain in the glossary: its reworded returns would give false warnings. List the first use and its returns as Dependent paragraphs.
- **reported hidden message**: the narration describes a code without printing it ("he underlined the M of 'morze', then the A…"). The example words, the letters and the message the narration spells out are the passage.

Most chapters have none.

## 2. State the rule

For each document candidate (a possible hidden message), run `mneme.py letters <chapter> <first-id> <last-id>`; verse, wordplay, refrains and quotations need no letters. For a passage that starts or ends inside a paragraph (a quoted note in a longer paragraph), add `--from "<its first words>"` and `--to "<its last words>"`. Give only the part that carries the message: leave out a salutation and a sign-off that stand outside it (start the range after them, or use `--from`), or the first sentence letter will include them. It prints the first letters of the passage's sentences, lines, paragraphs, words and marked words. Read them as words in the source language, and read what the chapter says about the passage (a character who decodes it, a stated message). A letter string that spells nothing is the normal case: do not read a message into it. Drop candidates with no rule.

For each kept passage, write in `passages.md`:

```markdown
## 04: p031–p036 (hidden_message)

Rule: the first letters of the sentences of the letter body spell the message. The salutation and the signature stand outside it.
Source message: …
Target message: THEY'RE WATCHING ME (same meaning, as short as possible)
Dependent paragraphs: p052 (Ola reads the letters out)
Status: todo
```

- verse: number of lines, the rhymes as heard (which words rhyme with which, as letters: AABB; say if the rhymes fall inside the lines), what the metre is like, and the central images. When the source's line breaks are only typographic (a couplet with internal rhymes is the same jingle as four short rhymed lines), say so: the target may place the rhymes where its rhythm needs them, as long as the number of rhymes and of lines stays.
- hidden_message: the unit, the message in the source, the same message in the target language, and which part carries it. If the target message has a different number of letters, say so: the passage then needs that many units (merge or split sentences). If the rule is not "first letters of units", describe it exactly, with the steps to read it.
- wordplay: the two meanings or forms, and what depends on them.
- quotation: the work, the author, the published translation to use (title, translator, edition) or "none known: own translation, with a note".
- reported hidden message: the example words and letters the narration gives, the message, and the rule the narration states ("a letter from the middle of a word"). In the target, choose example words whose letters spell the target message; if the source gives a reason that does not carry over (no Polish word starts with Y), either find a reason that does or drop it, and say which in a wordplay note. `letters --translation` cannot check it: check by reading.
- **Dependent paragraphs**: paragraphs that quote the passage (in the same chapter as `p052`, in another as `02:p005`), explain its rule, give worked examples of it, or state what it hides. They must stay consistent with the translation.

If no candidate is kept, `passages.md` still lists what was checked, one line each, so a later session does not scan again:

```markdown
# Special passages

Scanned chapters 1–2. Nothing kept.
- 01: title (verse): two-line prayer epigraph, no rhyme or metre to keep.
- 02: p126 (document): execution order; letters spell nothing.
```

## 3. Check (after the passage's fragment is translated)

Check only the rule, not style:

- verse: compare line count, rhyme scheme and metre with the source. A rhyme must be heard in the target language; near-rhymes count only where the source uses them. Correct prose set in lines, without the rhyme the source has, breaks the rule.
- hidden_message: run `letters … --translation` and compare with the target message. Use the script's letters; do not recount by eye. Letters before and after the message are fine when they come from a salutation or sign-off, as in the source.
- wordplay: both meanings must be readable, and what depends on them must still make sense.
- Dependent paragraphs agree with the translation: quoted words match, and a stated message is the one the passage spells.
- quotation: the wording is the published translation named in `passages.md`, or there is a quotation note saying it is the translator's own.
- reported hidden message: read the example words: their letters spell the target message in order, and the rule the narration states still holds.

`check` does not report missing glossary terms in the paragraphs of a passage whose status is `passed` or `corrected`, since the rule may have changed their words. It reads the ids from the `## NN: pXXX–pYYY` headings, so keep that form.

## 4. Correct

When the rule is broken, translate the passage again:

- The rule comes first, then the meaning, then the exact wording. Keep everything the source says that the rule allows; change wording, word order and sentence breaks freely.
- Keep the voice and register: a letter still sounds like its writer, a folk song still sounds like one. Use names and terms as the current translation has them.
- **Hidden message**: plan first, one unit per letter of the target message. Keep the message's word breaks where the source keeps them: if the source starts a new paragraph between two words of the message (SPOTKAJMY | SIĘ), start it between two words in the target (MEET | ME), never inside a word. The part that carries the message must have exactly as many units as the message has letters, so merge or split sentences where needed. After writing, check the letters with the script and fix any mismatch. The text must still read as a natural letter, with no sign that it was built around letters.
- **Verse**: keep the number of lines and the rhyme scheme, with rhymes heard in the target language, and a line length close to the source. Keep the central images (the mud, the sleeping gods): a rhyme bought by changing an image or adding a phrase ("clay" for mud, "all day") is a last resort. Write at least two versions, keep the one that keeps the images and sounds most like the kind of verse it is (a nursery rhyme, a hymn, a soldiers' song), and add a wordplay note for any image you had to change.
- **Wordplay**: find a pair of words in the target language that carries both meanings, or the closest play that keeps what depends on it.
- Keep the paragraph ids and count. Update the dependent paragraphs only as much as needed.

Before replacing anything, copy the current translation of the passage into `passages.md` under "First translation". Save the new text with the same `save` route (write the whole fragment, or edit the paragraphs in `translation/chapter-NN.md` directly), and check again. Try up to three times; give each new attempt the problems of the last one.

Record the result in the passage's Status:

| Status | Meaning |
|---|---|
| `passed` | The normal translation keeps the rule. Nothing changed. |
| `corrected` | It broke the rule; a new translation passed and replaced it. The author should look at it. |
| `failed` | No attempt passed. The first translation stays. The author must decide before export. |

Show the user every `corrected` and `failed` passage with the source, the first translation, the new text and a note on what changed. Dependent paragraphs in other chapters are not patched: name them for the user.
