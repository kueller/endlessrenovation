import io
import os

from app.rb.rb import DB_LIST


def _regenerate_db(db_lines):
    db_filename = DB_LIST["fr"]

    with io.open(f"{db_filename}_tmp", "w", encoding="utf-8") as f:
        f.write("\n".join(db_lines))

    os.rename(f"{db_filename}_tmp", db_filename)


def load_fr_db_lines() -> list:
    with io.open(DB_LIST["fr"], "r", encoding="utf-8") as f:
        text = f.read()
    return text.split("\n")


def fr_insert_word(word: str, hyphenation: str, db_lines: list):
    hyphenation = hyphenation.replace("-", "#")
    lower = 0
    exists = False
    upper = len(db_lines)
    i = 0

    while len(db_lines[lower:upper]) > 1:
        i = ((upper - lower) // 2) + lower
        if word.lower() > db_lines[i].split(" ")[0].lower().strip():
            lower = i
        elif word.lower() == db_lines[i].split(" ")[0].lower().strip():
            exists = True
            break
        else:
            upper = i

    if exists:
        db_lines[i] = word.lower() + " " + hyphenation.lower()
        effective_line = i + 1
    else:
        db_lines.insert(i + 1, word.lower() + " " + hyphenation.lower())
        effective_line = i + 2

    _regenerate_db(db_lines)

    return effective_line
