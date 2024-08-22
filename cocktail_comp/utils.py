

def split_names(names):
    name = names.split(', ')
    return name

def decode_name(name_string):
    names = name_string.split(", ")
    final = []
    for x in names:
        final.append(x.strip("''[]"))

    return name_string