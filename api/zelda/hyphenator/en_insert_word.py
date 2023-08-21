import os

from app.rb.rb import DB_LIST


def _regenerate_db(db_lines):
    db_filename = DB_LIST["en"]

    with open(f"{db_filename}_tmp", "w") as f:
        f.write("\n".join(db_lines))

    os.rename(f"{db_filename}_tmp", db_filename)


def load_en_db_lines() -> list:
    with open(DB_LIST["en"], "r") as f:
        text = f.read()

    return text.split("\n")


def en_insert_word(word: str, hyphenation: str, db_lines: list):
    hyphenation = hyphenation.replace("-", "#")
    lower = 0
    exists = False
    upper = len(db_lines)
    i = ((upper - lower) // 2) + lower

    while len(db_lines[lower:upper]) > 1:
        i = ((upper - lower) // 2) + lower
        if word.lower() > db_lines[i].replace("#", "").lower().strip():
            lower = i
        elif word.lower() == db_lines[i].replace("#", "").lower().strip():
            exists = True
            break
        else:
            upper = i

    if exists:
        db_lines[i] = hyphenation.lower()
        effective_line = i + 1
    else:
        db_lines.insert(i + 1, hyphenation.lower())
        effective_line = i + 2

    _regenerate_db(db_lines)

    return effective_line
