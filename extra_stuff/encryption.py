import random

ascii_string = "!#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"


def encrypt(str):
    # making a key and the shuffling list
    shuffled = ascii_string
    key = random.choices(ascii_string, k=3)
    str_index = 0
    for i in range(3):
        a=ascii_string[str_index:ascii_string.index(sorted(key)[i])]
        b=''.join(reversed(list(shuffled[str_index:ascii_string.index(sorted(key)[i])])))
        shuffled = shuffled.replace(a,b)
        str_index = ascii_string.index(sorted(key)[i]) + 1
    x=ascii_string[str_index:len(ascii_string)]
    y=''.join(reversed(list(shuffled[str_index:len(ascii_string)])))
    shuffled = shuffled.replace(x,y)
    #all of the above was to make the key and shuffling list
    word_list = [ascii_string, shuffled]
    new_string = ''.join(key)  # making return string
    for i in str:
        if i not in word_list[0]:
            new_string += i
        else:
            new_string += word_list[1][
                word_list[0].index(i)]
    print(new_string)
    return new_string


def decrypt(str):
    # making the shuffling list from the key
    shuffled = ascii_string
    key = str[0:3]
    str_index = 0
    for i in range(3):
        a = ascii_string[str_index:ascii_string.index(sorted(key)[i])]
        b = ''.join(reversed(list(shuffled[str_index:ascii_string.index(sorted(key)[i])])))
        shuffled = shuffled.replace(a, b)
        str_index = ascii_string.index(sorted(key)[i]) + 1
    x = ascii_string[str_index:len(ascii_string)]
    y = ''.join(reversed(list(shuffled[str_index:len(ascii_string)])))
    shuffled = shuffled.replace(x, y)
    # all of the above was to make the shuffling list from the key
    word_list = [ascii_string, shuffled]
    new_string = ""
    for i in str[3:]:
        if i not in word_list[0]:
            new_string += i
        else:
            new_string += word_list[0][word_list[1].index(i)]
    return new_string
