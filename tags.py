import re

class InvalidQuery (Exception):
    pass

QueryComponentsLimit = 100

def parse_tag_query(query):
    """Parse a tag query into a list of tuples [(action,tag)].

       action is either "require" or "forbid".

       tag is the actual tag string.

       Tag queries are expressed like this:
         "required" or "+required"
         "required~forbidden"
         "~forbidden+required+required2"
    """
    if not query:
        return []
    if query[0] not in "+~":
        query = "+" + query
    separators = re.compile(r"([+~])")
    words = separators.split(query)[1:]
    if len(words) > QueryComponentsLimit:
        raise InvalidQuery()
    if len(words)%2 != 0:
        raise InvalidQuery()
    actions = {
        "+": "require",
        "~": "forbid",
    }
    return [(actions[a],t) for a, t in zip(words[::2], words[1::2])]

def reorder_query(pquery, get_tag_count=None):
    """Sort query components for optimal search.
       
       First require, then forbid.

       If the information is available, first require the smallest
       categories, proceed to require the larger categories, then
       forbid the largest categories, and proceed to the smaller ones.

       The basic idea is to reduce the set being queried as much
       as possible on every step.
    """
    requires = [(action,tag) for action, tag in pquery if action == "require"]
    forbids = [(action,tag) for action, tag in pquery if action == "forbid"]
    assert len(requires) + len(forbids) == len(pquery)
    def mass(action_tag):
        action, tag = action_tag
        return get_tag_count(tag)
    if get_tag_count:
        requires.sort(key=mass)
        forbids.sort(key=mass, reverse=True)
    return requires + forbids

def sorted_sequence_intersection(comparator, aseq, bseq):
    a = aseq.next()
    b = bseq.next()
    last_a = last_b = None
    while True:
        rv = comparator(a, b)
        if last_a is not None:
            assert comparator(last_a, a) <= 0
        if last_b is not None:
            assert comparator(last_b, b) <= 0
        last_a, last_b = a, b
        el = a
        if rv == 0:
            yield el
        if rv <= 0:
            a = aseq.next()
        if rv >= 0:
            b = bseq.next()

def perform_query(pquery, comparator, fetch):
    """Perform a query (the query will not be automatically reordered).

       fetch must be a function which returns a sequence of the
       elements in a consistent order according to the comparator.
       fetch should take one positional argument, "tag", and one
       keyword argument "negate" defaulting to False.

       Note that this can the order can often be object identity. The
       order only needs to be consistent within while a query is being
       processed.
    """
    seq = None
    def fetch_forbidden(tag):
        return fetch(tag, negate=True)
    actions = {
        "require": fetch,
        "forbid": fetch_forbidden,
    }
    for action, tag in pquery:
        newseq = actions[action](tag)
        if seq is None:
            seq = newseq
        else:
            seq = sorted_sequence_intersection(comparator, seq, newseq)
    for element in seq:
        yield element

