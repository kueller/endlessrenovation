# coding=utf-8
# File from syllabes https://github.com/short-edition/syllabes
# Edited by kueller

import os
import io

# RegexpTokenizer de nltk instancié aux règles du français écrit
from nltk import RegexpTokenizer

from app.config import SYLLABES_FR_WIKTIONARY_DIR

tokenizer = RegexpTokenizer(
    """(?x)
        \d+(?:\.\d+)?\s*%
        | \w'
        | \w+
        | [^\w\s]
        """
)

# ponctuations à supprimer après la tokenization par nltk
punctuations = ".,;:-»«'!?…()" + '"'

# wiktionary local stocké dans une variable
wiktionary_entries = "abcdefghijklmnopqrstuvwxyzéàâæçéèêîô"
wiktionary_lists = {}
aspirated_h_list = []


def load_wiki_db():
    global wiktionary_lists
    wiktionary_lists = {}
    for entry in wiktionary_entries:
        with io.open(
            os.path.join(SYLLABES_FR_WIKTIONARY_DIR, "phonetics_wiktionary_").encode(
                "utf-8"
            )
            + entry.encode("utf-8")
            + ".txt".encode("utf-8"),
            encoding="utf-8",
        ) as f:
            wiktionary_lists[entry] = [line.strip("\n").split(";") for line in f]


def load_single_wiki_db(c):
    wiktionary_list = {}
    if c in wiktionary_entries:
        with io.open(
            os.path.join(SYLLABES_FR_WIKTIONARY_DIR, "phonetics_wiktionary_").encode(
                "utf-8"
            )
            + c.encode("utf-8")
            + ".txt".encode("utf-8"),
            encoding="utf-8",
        ) as f:
            wiktionary_list[c] = [line.strip("\n").split(";") for line in f]
    return wiktionary_list


# h aspirés stockés dans une variable
with open(
    os.path.join(SYLLABES_FR_WIKTIONARY_DIR, "aspirated_h.txt"), encoding="utf-8"
) as f:
    aspirated_h_list = [line.strip("\n") for line in f]


def close_wiki_db():
    global wiktionary_lists
    wiktionary_lists = None


def get_wiki_lists():
    global wiktionary_lists
    return wiktionary_lists


# lettres utilisées en français écrit
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
accents = "ôàâéèêëîïûùü"
vowels = "aeiouœ"  # le y peut faire office de (semi-)consonne : cf. yoyo
consonants = "bcçdfghjklmnpqrstvwxz"
consonants_rl = "bcdfgknptv"  # consonnes pouvant être suivies par r ou l


# sons vocaliques et consonantiques du français oral extraits de l'Alphabet Phonétique International (API)
vocalic_sounds = "aɑəøœeɛoɔiuỹ"  # tilde pour les voyelles nasales
consonantal_sounds = "bskdfɡʒlmnɲpʁtvzʃwɥj"

# listes non-exhaustives de mots où le hiatus n'est pas possible (source : http://jocab.over-blog.com/pages/Dierese_et_synerese_les_diphtongues-3241024.html)
exceptions_j = [
    "diacre",
    "fiacre",
    "diabl",
    "milliard",
    "piaf",
    "ciel",
    "fiel",
    "miel",
    "biell",
    "niell",
    "viell",
    "relief",
    "fief",
    "avant-hier",
    "chienne",
    "pierr",
    "lierr",
    "vieil",
    "miett",
    "assiett",
    "bréviair",
    "concierg",
    "vierg",
    "fiol",
    "pioch",
    "mioch",
    "kiosqu",
    "mieux",
    "vieux",
    "cieux",
    "messieurs",
    "monsieur",
    "viand",
    "diancr",
    "faïenc",
]
exceptions_u = ["lui", "duègne", "juan"]
