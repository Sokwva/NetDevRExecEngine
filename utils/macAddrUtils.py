def macAddFormater(macAdd: str):
    if macAdd.find("-") != -1:
        return fourPartToEight("-", macAdd)
    if macAdd.find(".") != -1:
        return fourPartToEight(".", macAdd)
    return macAdd


def fourPartToEight(split: str, raw: str):
    x = raw.replace(split, "")
    y = []
    e = 0
    for t in x:
        if e % 2 == 0 and e != 0:
            y.append(":")
        y.append(t)
        e += 1
    return "".join(y)


def eightToFourPart(split: str,raw: str):
    x = raw.replace(split, "")
    y = []
    e = 0
    for t in x:
        if e % 4 == 0 and e != 0:
            y.append("-")
        y.append(t)
        e += 1
    return "".join(y)
