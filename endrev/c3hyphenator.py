import sys
from num2words import num2words

BAD_CHARS = ['.',',','(',')','[',']']

def setup_moby(moby_file):
    moby = {}

    with open(moby_file, 'r') as f:
        text = f.read()

    for line in text.split('\n'):
        word = line.strip()
        moby[word.replace('\xa5','')] = word.split('\xa5')

    return moby

def hyph_word(moby, word):
    if word in moby:
        return '- '.join(moby[word])
    # This section preserves the casing of the original word
    elif word.lower() in moby:
        hyph = '- '.join(moby[word.lower()])
        s_word = list(word)
        s_hyph = list(hyph)
        j = 0

        for i in range(len(word)):
            if s_hyph[j] == '-': j += 1
            if s_hyph[j] == ' ': j += 1
            if s_word[i] != s_hyph[j]: s_hyph[j] = s_word[i]
            j += 1
        return ''.join(s_hyph)

    return word

def hyphenate(moby, word):
    if not word[0].isalpha(): return word
    
    toedit = word
    hyphenated = ''

    if word.endswith('='):
        toedit = word[0:len(word)-1]

    if '=' not in toedit:
        hyphenated = hyph_word(moby, word)
    else:
        h_list = []
        for tok in toedit.split('='):
            h_list.append(hyph_word(moby, tok))
        hyphenated = '= '.join(h_list)

    if word.endswith('='):
        hyphenated += '='

    return hyphenated

def convert_lyrics(text, moby, atsign):
    language = 'en'
    lines = []

    # Preprocessing
    for line in text.split('\n'):
        if line.strip() == '':
            lines.append(line)
            continue

        tok = []

        # Number translation
        for w in line.split():
            if w.isalpha():
                tok.append(w)
                continue
            
            try:
                x = int(w)
                n = num2words(x, lang=language)
                tok.append(n.replace('-', ' '))
            except ValueError:
                try:
                    f = float(w)
                    n = num2words(f, lang=language)
                    tok.append(n.replace('-',' '))
                except ValueError:
                    tok.append(w)

        line = ' '.join(tok)

        for c in BAD_CHARS: line = line.replace(c, '')

        line = line.replace('-', '=')
        line = line.replace('&', 'and')
        line = line[0:len(line)-1].replace('?', '') + line[len(line)-1]

        lines.append(line.strip())

    formatted = ''

    for line in lines:
        if line.strip() == '':
            formatted += '\n'
            continue

        tok = []
        for w in line.split():
            tok.append(hyphenate(moby, w))
            
        formatted += ' '.join(tok) + '\n'
        if atsign:
            formatted = '@' + formatted

    return formatted 
