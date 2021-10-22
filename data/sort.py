with open("mhyph.txt", "r") as f:
    lines = f.read().split("\n")

word_list = []
for i in range(len(lines)):
    word = lines[i].replace("\xa5", "").lower().strip()
    word_list.append([word, i])

word_list.sort()

new_lines = []
for word in word_list:
    new_lines.append(lines[word[1]])

with open("mhyph2.txt", "w") as f:
    f.write("\n".join(new_lines))
