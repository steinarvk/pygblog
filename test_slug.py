# coding=utf8

from slug import *

def test_slugify_accented():
    assert slugify(u"naïvé") == "naive"

def test_slugify_nordic():
    assert slugify(u"ærlig øvelse ål") == "aerlig-oevelse-aal"
    assert slugify(u"ä ö å") == "ae-oe-aa"

def test_slugify_lowercase():
    assert slugify("CrAzYCasE") == "crazycase"

def test_slugify_spaces_to_dashes():
    assert slugify("it happens all the time") == "it-happens-all-the-time"

def test_slugify_multiple_spaces_to_dash():
    assert slugify("ill\t\tbehaved    string") == "ill-behaved-string"

def test_slugify_keep_numbers():
    assert slugify("012345") == "012345"

def test_slugify_strip_nonalphanumeric():
    assert slugify("now: foo bar!") == "now-foo-bar"

def test_slugify_keep_stopwords():
    # I believe keeping all the words makes for more human-readable URLs,
    # even if they are longer.
    assert slugify("the fox and the cat") == "the-fox-and-the-cat"
