# Algorithm by Nick F.
# Submitted by SuperRiderTH
# Translated to Python by kueller

def isvowel(c):
    return c.lower() in "aeiou"

def isconsonant(c):
    return not isvowel(c)

def isdigraph(c1, c2):
    c1 = c1.lower()
    c2 = c2.lower()
    if (c1 + c2) in ('ts', 'dz'):
        return True
    elif (c1 in 'cs') and c2 == 'h':
        return True
    elif c2 == 'y':
        return True
    
    return False

def istrigraph(c1, c2, c3):
    c3 = c3.lower()
    return isdigraph(c1, c2) and (c3 == 'y')

def hyphenate(word):
    appends = ""

    if not word[len(word)-1].isalpha():
        appends = word[len(word)-1]
        word = word[0:len(word)-1]

    # Replace macrons, should be fine most of the time.
    word = word.replace("ā","aa")
    word = word.replace("ē","ee")
    word = word.replace("ī","ii")
    word = word.replace("ō","ou")
    word = word.replace("ū","uu")
        
    hyph = ""
    skipindex = set([len(word)])
    for i in range(len(word)):
        
        if i in skipindex:
            continue
        
        hyph += word[i]

        if isvowel(word[i]):
            if (i + 1) < len(word):
                hyph += '- '
        else:
            if (i + 1) < len(word):
                if isvowel(word[i+1]): continue
                else:
                    if (i + 2) < len(word):
                        if istrigraph(word[i], word[i+1], word[i+2]):
                            hyph += word[i+1] + word[i+2]
                            skipindex.add(i+1)
                            skipindex.add(i+2)
                            continue
                    if (i + 1) < len(word):
                        if isdigraph(word[i], word[i+1]):
                            hyph += word[i+1]
                            skipindex.add(i+1)
                            continue
                        else:
                            hyph += '- '

    return hyph + appends

