# coding=utf-8

__author__ = 'Short-Edition (Fabien)'
__version__ = "0.1.6"

from key_lists import accents, vowels, consonants, consonants_rl, wiktionary_entries
from key_lists import tokenizer, punctuations
from key_lists import vocalic_sounds, consonantal_sounds, exceptions_j, exceptions_u
#from key_lists import wiktionary_lists as wiki_list
from key_lists import aspirated_h_list
from key_lists import get_wiki_lists

"""
    Implémentation du décompte des syllabes d'une chaîne de caractères donnée.
    Deux modes sont disponibles : default et extended.
    extended renvoie une plage de valeurs possibles, calculées à partir de règles supplémentaires (prose/poésie, hiatus).
    La langue doit être donnée sous la forme du code pays utilisé par le Wiktionary. (français par défaut)

    Usage:

    >>> from syllabes import syllabizer
    >>> syllabizer(chaîne, mode, langue)
"""


# pour remplacer des éléments en partant de la fin d'une chaîne
def replace_right(source, target, replacement, replacements=None):
    return replacement.join(source.rsplit(target, replacements))


# fonction principale du décompte des syllabes basée sur les transcriptions API du Wiktionnary.
# source : chaîne de caractères
# language : abréviation du code pays (fr,en...) en string
def syllabizer(source, mode="default", language="fr"):
    wiki_list = get_wiki_lists()

    # prétraitement du texte en entrée
    if type(source) != type(u""):
        source = source.decode("utf8")
    source = source.lower().replace(u"’", u"'")
    tokenized_source = [word for word in tokenizer.tokenize(source) if word not in punctuations]

    default_url = u"http://" + language + u".wiktionary.org/wiki/"
    counter = 0
    apis_list = []

    # nous avons arbitrairement choisi $ comme valeur par défaut pour que les variables aient un élement de comparaison
    for pos_token, token in enumerate(tokenized_source):
        try:
            next_token = tokenized_source[pos_token + 1]
        except(IndexError):
            next_token = u"$"
        token_api = u"$"

        # les pronoms et conjonctions élidées sont ignorées du point de vue phonétique
        if token[-2:] == u"qu":
            token += u"'"
        if (token[-1] == u"'" and len(token) < 4) or token == u"t":
            apis_list.append(u"stopwords")
            continue

        # on cherche le mot dans notre wiktionary
        elif token[0].lower() in wiktionary_entries:
            token_found = False
            for pair in wiki_list[token[0].lower()]:
                # mot trouvé dans le wiktionary -> on a pu récupérer sa transcription phonétique,
                # segmentée en syllabes par des .
                if pair[0] == token:
                    token_found = True
                    token_api = pair[1]
                    counter += token_api.count(u".") + 1
                    apis_list.append(token_api)
                    break
            # si le mot n'a pas été trouvé, on essaie avec une majuscule
            if not token_found:
                for pair in wiki_list[token[0].lower()]:
                    if pair[0] == token.capitalize():
                        token_found = True
                        token_api = pair[1]
                        counter += token_api.count(u".") + 1
                        apis_list.append(token_api)
                        break
                        # mot absent du wiktionary -> on bascule sur le système de règles
                if not token_found:
                    if language == "fr":
                        counter += syllabe_rules(token)
                        apis_list.append(u"syllabe_rules")
                    else:
                        print "notre système de règles ne marche que pour le français (language = 'fr')"
                        apis_list.append(u"unknown")

        wiki_list = None

        # gestion spécifique du e en fin de mot
        if token[-1] == u"e":
            if next_token.lower()[0] == u"h" and token_api[-1] != u"ə" and next_token.lower() in aspirated_h_list:
                    counter += 1
                    break
            if next_token[0] not in u"yh$" + vowels + accents and token_api[-1] != u"ə" and token[-2] not in u"éi":
                counter += 1
            elif token_api[-1] == u"ə" and next_token[0] in u"$" + vowels + accents:
                counter -= 1
        elif (len(token) > 3 and token[-2:] == u"es") or token[-3:] == u"ent":
            if token_api[-1] not in vocalic_sounds and next_token[0] != u"$":
                counter += 1
    counter += tokenized_source.count(u"&")

    # lorsque le mode est extended, on renvoie une liste de valeurs possibles, obtenues avec des règles supplémentaires
    if mode == "extended":
        new_value = counter
        counter = [counter]
        for pos_api, api in enumerate(apis_list):
            written_word = tokenized_source[pos_api]
            # prononciation prosaïque vs poétique
            if u"." in api and u"e" in written_word:
                pos_e = written_word.index(u"e")
                if 0 < pos_e < len(written_word) - 2 \
                        and written_word[pos_e + 1] in consonants \
                        and (written_word[pos_e - 1] in consonants or written_word[pos_e - 2] == u"q"):
                    for pos_phoneme, phoneme in enumerate(api):
                        try:
                            prev_phoneme_a = api[pos_phoneme - 1]
                        except(IndexError):
                            prev_phoneme_a = u"$"
                        try:
                            next_phoneme_a = api[pos_phoneme + 1]
                        except(IndexError):
                            next_phoneme_a = u"$"
                        if prev_phoneme_a in consonantal_sounds \
                                and next_phoneme_a in consonantal_sounds and phoneme == u".":
                            new_value -= api.count(u".") + 1
                            new_value += syllabe_rules(written_word)
                            if new_value not in counter:
                                counter.append(new_value)
            # possibilités de hiatus
            if api not in [u"syllabe_rules", u"stopwords"]:
                for pos_phoneme, phoneme in enumerate(api):
                    if pos_phoneme == 0:
                        prev_phoneme_b = u"$"
                    else:
                        prev_phoneme_b = api[pos_phoneme - 1]
                    if pos_phoneme == len(api) - 1:
                        next_phoneme_b = u"$"
                    else:
                        next_phoneme_b = api[pos_phoneme + 1]

                    if phoneme in u"jɥw":
                        if next_phoneme_b == u"$":
                            continue
                        elif phoneme in u"jɥ" and prev_phoneme_b == u"$":
                            continue
                        elif prev_phoneme_b == u"." or next_phoneme_b == u".":
                            continue
                        elif phoneme == u"ɥ" and tokenized_source[pos_api] not in exceptions_u:
                            new_value += 1
                            if new_value not in counter:
                                counter.append(new_value)
                        elif phoneme == u"w" \
                                and any(u"o" + va in tokenized_source[pos_api] for va in (vowels + accents)) \
                                and tokenized_source[pos_api] != u"oui":
                            try:
                                next_phoneme2_b = api[pos_phoneme + 2]
                            except(IndexError):
                                next_phoneme2_b = u"$"
                            if next_phoneme_b == u"a" and u"oua" not in tokenized_source[pos_api]:
                                continue
                            elif next_phoneme_b + next_phoneme2_b != u"ɛ̃":
                                new_value += 1
                                if new_value not in counter:
                                    counter.append(new_value)
                        elif phoneme == u"j" \
                                and not any(tokenized_source[pos_api].startswith(ex_j) for ex_j in exceptions_j) \
                                and any(u"i" + va in tokenized_source[pos_api] for va in (vowels + accents)):
                            new_value += 1
                            if new_value not in counter:
                                counter.append(new_value)
        return counter
    else:
        return [counter]


# fonction annexe du décompte des syllabes basée sur des règles à l'échelle du caractère.
# token : chaîne de caractères unicode
def syllabe_rules(token):
    inside_counter = 0

    for pos_letter, letter in enumerate(token):
        # gestion des indexErrors
        try:
            previous_token = token[pos_letter - 1]
        except(IndexError):
            previous_token = u"$"
        try:
            previous_token2 = token[pos_letter - 2]
        except(IndexError):
            previous_token2 = u"$"
        try:
            next_token = token[pos_letter + 1]
        except(IndexError):
            next_token = u"$"
        try:
            next_token2 = token[pos_letter + 2]
        except(IndexError):
            next_token2 = u"$"
        if pos_letter - 1 == -1:
            previous_token = u"$"
        if pos_letter - 2 == -1:
            previous_token2 = u"$"

        # décompte initial de TOUTES les voyelles
        if letter in vowels + accents:
            inside_counter += 1

        # règles de décrémentation du compteur des voyelles
        #cas spécial de la voyelle Y
        if letter == u"y":
            if previous_token not in vowels and next_token not in vowels + accents or next_token + next_token2 == u"on":
                inside_counter += 1

        #voyelle U
        elif letter in u"uùû":
            if previous_token in u"aeœ":
                inside_counter -= 1
            elif previous_token2 in consonants_rl and previous_token in u"rl" and next_token in u"aeou":
                inside_counter += 1
            elif previous_token == u"o":
                inside_counter -= 1
                if pos_letter - 3 > 0:
                    if token[pos_letter - 3] in consonants_rl \
                            and previous_token2 in u"rl" and next_token in vowels + accents:
                        inside_counter += 1
            elif previous_token in u"qg" and next_token in u"aou" + accents:
                inside_counter -= 1

        #voyelle O
        elif letter == u"o":
            if previous_token in u"io":
                inside_counter -= 1
            elif next_token == u"e":
                inside_counter -= 1

        #voyelle I
        elif letter in u"iî":
            if previous_token in u"aeouœ":
                inside_counter -= 1
            elif previous_token2 in consonants_rl and previous_token in u"rl" and next_token in vowels + u"é":
                inside_counter += 1
            if next_token in u"éè":
                inside_counter -= 1

        #voyelle E
        elif letter == u"e":
            if pos_letter == len(token) - 1 or previous_token in u"éi" or (
                    previous_token == u"u" and next_token != u"u"):
                inside_counter -= 1
            elif previous_token2 not in u" $" and next_token == u" " and next_token2 in u"h" + vowels + accents:
                inside_counter -= 1

        #voyelle A
        elif letter == u"a":
            if previous_token == u"e" and next_token == u"u":
                inside_counter -= 1
            elif previous_token == u"i":
                inside_counter -= 1

        #cas spécial du E muet pluriel
        elif previous_token + letter == u"es" and previous_token2 not in u"éiu$" and pos_letter == len(token) - 1:
            inside_counter -= 1
    return inside_counter
