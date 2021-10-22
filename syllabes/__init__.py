# coding=utf-8
# Created from syllabes https://github.com/short-edition/syllabes
# Edited by kueller

__author__ = "Short-Edition (Fabien)"


"""
    Ce package propose un algorithme de décompte des syllabes pour une chaîne de caractères donnée.
"""

__version__ = "0.1.6"

from syllabes.syllabes import syllabizer
from syllabes.key_lists import consonants, vowels, accents
from syllabes.key_lists import load_single_wiki_db
