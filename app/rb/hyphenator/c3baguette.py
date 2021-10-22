import os
import io

# French database in the format of
#   word hy#phe#na#tion
# Single space in between.
from syllabes import consonants, accents
from syllabes.syllabes import syllabizer


def setup_fr_db(db_file):
    db = {}

    with io.open(db_file, "r", encoding=("utf-8")) as f:
        text = f.read()

    for line in text.split("\n"):
        if line.strip() == "":
            continue
        word, hyph = line.strip().split(" ")
        db[word] = hyph

    return db


# Similar to the add_word script.
def insert_fr_word(word, hyph, filename):
    hyph_tokens = hyph.split("- ")
    with io.open(filename, "r", encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    lower = 0
    exists = False
    upper = len(lines)
    i = 0

    while len(lines[lower:upper]) > 1:
        i = ((upper - lower) // 2) + lower
        if word.lower() > lines[i].split(" ")[0].lower().strip():
            lower = i
        elif word.lower() == lines[i].split(" ")[0].lower().strip():
            exists = True
            break
        else:
            upper = i

    if exists:
        lines[i] = word.lower() + " " + "#".join(hyph_tokens).lower()
    else:
        lines.insert(i + 1, word.lower() + " " + "#".join(hyph_tokens).lower())

    with io.open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# Looks for a consonant after sections followed by vowels.
def find_next_tok(word, i):
    tok = ""

    if word[i] in consonants:
        while (i < len(word)) and (word[i] in consonants):
            tok += word[i]
            i += 1

    while (i < len(word)) and (word[i] not in consonants) and (word[i] not in accents):
        tok += word[i]
        i += 1

    if ((i + 1) < len(word)) and (word[i + 1] in consonants):
        tok += word[i]
        i += 1

    return tok, i


# Uses the syllable count from syllabes to know how many breaks
# there should be.
def hyphenate_fr(word):
    sylb_count = syllabizer(word)

    if isinstance(sylb_count, list):
        sylb_count = sylb_count[0]

    if sylb_count == 1:
        return word
    else:
        tokens = []
        pos = 0

        for i in range(0, sylb_count - 1):
            if pos < len(word):
                tok, pos = find_next_tok(word, pos)
                tokens.append(tok)

        tokens.append(word[pos:])

        return "- ".join(tokens)


# Copied from hyph_word_en using French DB format.
# If word needs to be algorithmically hyphenated, the result
# is added to the DB.
def hyph_word_fr(moby: dict, filename: str, word: str) -> str:
    db = moby

    if word in db:
        return db[word].replace("#", "- ")
    elif word.lower() in db:
        hyph = db[word.lower()].replace("#", "- ")
        s_word = list(word)
        s_hyph = list(hyph)
        j = 0

        for i in range(len(word)):
            if s_hyph[j] == "-":
                j += 1
            if s_hyph[j] == " ":
                j += 1
            if s_word[i] != s_hyph[j]:
                s_hyph[j] = s_word[i]
            j += 1
        hyph_word = "".join(s_hyph)
    else:
        hyph_word = hyphenate_fr(word)
        insert_fr_word(word, hyph_word, filename)
        db[word.lower()] = hyph_word.lower().replace("- ", "#")
    return hyph_word
