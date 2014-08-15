from tags import *

def test_parse_query_simple():
    assert parse_tag_query("tag1") == [("require", "tag1")]

def test_parse_query_explicit():
    assert parse_tag_query("+tag1") == [("require", "tag1")]

def test_parse_query_forbid():
    assert parse_tag_query("~tag1") == [("forbid", "tag1")]

def test_parse_query_multiple():
    assert parse_tag_query("tag1+tag2+tag3") == [
        ("require", "tag1"),
        ("require", "tag2"),
        ("require", "tag3"),
    ]

def test_parse_query_some_forbidden():
    assert parse_tag_query("tag1~tag2+tag3") == [
        ("require", "tag1"),
        ("forbid", "tag2"),
        ("require", "tag3"),
    ]

def test_parse_query_dash_separation():
    assert parse_tag_query("tag-one~tag-two+tag-three") == [
        ("require", "tag-one"),
        ("forbid", "tag-two"),
        ("require", "tag-three"),
    ]

TestCategorySizes =  {
    "python": 132,
    "kittens": 7,
    "politics": 3,
    "math": 12,
    "meta": 1,
}

def lookup_test_category_size(tag):
    return TestCategorySizes.get(tag, 0)

def test_query_reordering():
    query = parse_tag_query("kittens+politics~math~python")
    reordered = reorder_query(query, lookup_test_category_size)
    # first require the smallest categories, then forbid the largest ones
    assert reordered[0] == ("require", "politics")
    assert reordered[1] == ("require", "kittens")
    assert reordered[2] == ("forbid", "python")
    assert reordered[3] == ("forbid", "math")

def test_query_reordering_2():
    query = parse_tag_query("~python+politics~math+kittens")
    reordered = reorder_query(query, lookup_test_category_size)
    # first require the smallest categories, then forbid the largest ones
    assert reordered[0] == ("require", "politics")
    assert reordered[1] == ("require", "kittens")
    assert reordered[2] == ("forbid", "python")
    assert reordered[3] == ("forbid", "math")

def test_query_alphabetic():
    import operator
    tags = {
        "cold": sorted("ireland norway sweden bergen".split()),
        "rainy": sorted("ireland bergen tokyo".split()),
        "hot": sorted("japan tokyo".split()),
    }
    all_items = sorted(set(reduce(operator.add, tags.values())))
    def fetch(tag, negate=False):
        if negate:
            for item in all_items:
                if item not in tags[tag]:
                    yield item
        else:
            for item in tags[tag]:
                yield item
    def q(query):
        pquery = parse_tag_query(query)
        return perform_query(pquery, cmp, fetch)
    assert set(q("cold")) == set(["ireland", "norway", "sweden", "bergen"])
    assert set(q("cold+rainy")) == set(["ireland", "bergen"])
    assert set(q("rainy")) == set(["ireland", "bergen", "tokyo"])
    assert set(q("rainy+hot")) == set(["tokyo"])
    assert set(q("hot~rainy")) == set(["japan"])
    assert set(q("cold~rainy")) == set(["norway", "sweden"])
