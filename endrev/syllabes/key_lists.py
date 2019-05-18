# coding=utf-8
# File from syllabes https://github.com/short-edition/syllabes
# Edited by kueller

import os
import io

# RegexpTokenizer de nltk instancié aux règles du français écrit
from nltk import RegexpTokenizer
tokenizer = RegexpTokenizer('''(?x)
        \d+(?:\.\d+)?\s*%
        | \w'
        | \w+
        | [^\w\s]
        ''')

# ponctuations à supprimer après la tokenization par nltk
punctuations = u".,;:-»«'!?…()" + u'"'

# wiktionary local stocké dans une variable
wiktionary_entries = u"abcdefghijklmnopqrstuvwxyzéàâæçéèêîô"
wiktionary_lists = {}
aspirated_h_list = []

def load_wiki_db():
    global wiktionary_lists
    wiktionary_lists = {}
    for entry in wiktionary_entries:
        with io.open('/var/www/endrev/endrev/data/fr_wiktionary/phonetics_wiktionary_' + entry.encode('utf-8') + ".txt", encoding='utf-8') as f:
            wiktionary_lists[entry] = [line.strip(u"\n").split(u";") for line in f]

def load_single_wiki_db(c):
    wiktionary_list = {}
    if c in wiktionary_entries:
        with io.open('/var/www/endrev/endrev/data/fr_wiktionary/phonetics_wiktionary_' + c.encode('utf-8') + ".txt", encoding='utf-8') as f:
            wiktionary_list[c] = [line.strip(u"\n").split(u";") for line in f]
    return wiktionary_list

# h aspirés stockés dans une variable
with open(u'/var/www/endrev/endrev/data/fr_wiktionary/aspirated_h.txt') as f:
    aspirated_h_list = [line.decode("utf8").strip(u"\n") for line in f]

def close_wiki_db():
    global wiktionary_lists
    wiktionary_lists = None

def get_wiki_lists():
    global wiktionary_lists
    return wiktionary_lists

# lettres utilisées en français écrit
alphabet = u"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
accents = u"ôàâéèêëîïûùü"
vowels = u"aeiouœ"  # le y peut faire office de (semi-)consonne : cf. yoyo
consonants = u"bcçdfghjklmnpqrstvwxz"
consonants_rl = u"bcdfgknptv"  # consonnes pouvant être suivies par r ou l


# sons vocaliques et consonantiques du français oral extraits de l'Alphabet Phonétique International (API)
vocalic_sounds = u"aɑəøœeɛoɔiuỹ"  # tilde pour les voyelles nasales
consonantal_sounds = u"bskdfɡʒlmnɲpʁtvzʃwɥj"

# listes non-exhaustives de mots où le hiatus n'est pas possible (source : http://jocab.over-blog.com/pages/Dierese_et_synerese_les_diphtongues-3241024.html)
exceptions_j = [u"diacre", u"fiacre", u"diabl", u"milliard", u"piaf", u"ciel", u"fiel", u"miel", u"biell", u"niell",
                u"viell", u"relief", u"fief", u"avant-hier", u"chienne", u"pierr", u"lierr", u"vieil",
                u"miett", u"assiett", u"bréviair", u"concierg", u"vierg", u"fiol", u"pioch", u"mioch",
                u"kiosqu", u"mieux", u"vieux", u"cieux", u"messieurs", u"monsieur", u"viand", u"diancr", u"faïenc"]
exceptions_u = [u"lui", u"duègne", u"juan"]
