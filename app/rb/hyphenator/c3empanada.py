from syltippy import syllabize


def setup_es_db(db_file: str) -> dict:
    db = {}

    with open(db_file, "r") as f:
        text = f.read()

    for line in text.split("\n"):
        if line.strip() == "":
            continue
        word, hyph = line.strip().split(" ")
        db[word] = hyph

    return db


# Similar to the add_word script.
def insert_es_word(word: str, syllables: list, filename: str) -> None:
    with open(filename, "r") as f:
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
        lines[i] = word.lower() + " " + "#".join(syllables).lower()
    else:
        lines.insert(i + 1, word.lower() + " " + "#".join(syllables).lower())

    with open(filename, "w") as f:
        f.write("\n".join(lines))


def hyph_word_es(moby: dict, filename: str, word: str) -> str:
    if word in moby:
        hyph_word = moby[word].replace("#", "- ")
    elif word.lower() in moby:
        hyph = moby[word.lower()].replace("#", "- ")
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
        syllables, stress = syllabize(word)
        insert_es_word(word, syllables, filename)
        hyph_word = "- ".join(syllables)

    return hyph_word
