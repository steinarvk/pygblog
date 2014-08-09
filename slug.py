# coding=utf8

import re
from unidecode import unidecode

def asciify(string):
    special_cases = {
        u"æ": u"ae",
        u"ø": u"oe",
        u"å": u"aa",
        u"ä": u"ae",
        u"ö": u"oe",
    }
    for to_be_replaced, replacement in special_cases.items():
        string = string.replace(to_be_replaced, replacement)
        string = string.replace(to_be_replaced.upper(), replacement.upper())
    return unidecode(string)

def slugify(title):
    string = asciify(title).lower()
    string = re.sub(r'[^\w\s]', '', string)
    words = string.split()
    return "-".join(words)
