import sys
from num2words import num2words

from app.rb.hyphenator import c3baguette, c3weebhyphens, c3empanada
from app.rb.hyphenator.c3baguette import hyph_word_fr
from app.rb.hyphenator.c3empanada import setup_es_db, hyph_word_es

BAD_CHARS = [".", ",", "(", ")", "[", "]", '"']
num_langs = ["en", "fr", "es"]


def setup_moby(moby_file):
    moby = {}

    with open(moby_file, "r") as f:
        text = f.read()

    for line in text.split("\n"):
        word = line.strip()
        moby[word.replace("#", "")] = word.split("#")

    return moby


# French will need the filename to write back to the database.
# So it is returned with the DB. Be aware.
def setup_db(lang, filename) -> (str, str):
    if lang == "en":
        return setup_moby(filename)
    elif lang == "fr":
        return c3baguette.setup_fr_db(filename)
    elif lang == "es":
        return setup_es_db(filename)
    else:
        return None


def hyph_word_en(moby, word):
    if word in moby:
        return "- ".join(moby[word])
    # This section preserves the casing of the original word
    elif word.lower() in moby:
        hyph = "- ".join(moby[word.lower()])
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
        return "".join(s_hyph)
    elif word.lower().endswith("'s"):
        word = hyph_word_en(moby, word[0 : len(word) - 2]) + word[-2] + word[-1]
    elif word.lower().endswith("s"):
        word = hyph_word_en(moby, word[0 : len(word) - 1]) + word[-1]

    return word


def hyph_word(moby, filename, word, lang):
    if lang == "en":
        return hyph_word_en(moby, word)
    elif lang == "fr":
        return hyph_word_fr(moby, filename, word)
    elif lang == "jp":
        return c3weebhyphens.hyphenate(word)
    elif lang == "es":
        return hyph_word_es(moby, filename, word)
    else:
        return word


def hyphenate(moby, filename, word, lang):
    if len(word) == 0:
        return word

    if not word[0].isalpha():
        return word

    toedit = word
    hyphenated = ""

    if word.endswith("="):
        toedit = word[0 : len(word) - 1]

    if "=" not in toedit:
        hyphenated = hyph_word(moby, filename, word, lang)
    else:
        h_list = []
        for tok in toedit.split("="):
            h_list.append(hyph_word(moby, tok, lang))
        hyphenated = "= ".join(h_list)

    if word.endswith("="):
        hyphenated += "="

    return hyphenated


def convert_lyrics(text, lang, atsign, db_filename):
    lines = []

    start = "@" if atsign else ""

    moby = setup_db(lang, db_filename)

    # Preprocessing
    for line in text.split("\n"):
        if line.strip() == "":
            lines.append(line)
            continue

        tok = []

        # Number translation
        for w in line.split():
            if w.isalpha():
                tok.append(w)
                continue

            if lang not in num_langs:
                tok.append(w)
                continue

            try:
                x = int(w)
                if x in range(1000, 9999 + 1):
                    n = num2words(x, lang=lang, to="year")
                else:
                    n = num2words(x, lang=lang)
                tok.append(n.replace("-", " "))
            except ValueError:
                try:
                    f = float(w)
                    n = num2words(f, lang=lang)
                    tok.append(n.replace("-", " "))
                except ValueError:
                    tok.append(w)

        line = " ".join(tok)

        for c in BAD_CHARS:
            line = line.replace(c, "")

        line = line.replace("-", "=")
        line = line.replace("&", "and")
        line = line[0 : len(line) - 1].replace("?", "") + line[len(line) - 1]
        line = line[0 : len(line) - 1].replace("!", "") + line[len(line) - 1]

        lines.append(line.strip())

    formatted = ""

    for line in lines:
        if line.strip() == "":
            formatted += "\n"
            continue

        tok = []
        for w in line.split():
            if all([not c.isalnum() for c in w]):
                continue

            if not w[-1].isalnum():
                w_format = w[: len(w) - 1]
                endchar = w[-1]
            else:
                w_format = w
                endchar = ""

            hyphenated = hyphenate(moby, db_filename, w_format, lang)
            tok.append(hyphenated + endchar)

        formatted += start + " ".join(tok) + "\n"

    return formatted
