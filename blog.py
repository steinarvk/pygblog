import pystache
import re
import os
import codecs
from slug import slugify
from collections import defaultdict

class BlogPost (object):
    def __init__(self, metadata, html):
        self.metadata = metadata
        self.html = html
        self._parse_metadata()

    def _meta(self, key):
        return self.metadata.get(key, "")
    
    def _parse_metadata(self):
        self.title = self._meta("title").strip()
        self.tags = self._meta("tags").split()
        self.slugs = self._meta("slug").split() or [slugify(self.title)]

    def template_args(self, blog):
        tags = []
        for tag in self.tags:
            tags.append({
                "name": tag,
                "url": blog.url("/tags/" + tag)
            })
        slug = self.slugs[0]
        url = blog.url("/posts/" + slug)
        return {
            "tags": tags,
            "slug": slug,
            "slugs": self.slugs,
            "url": url,
            "title": self.title,
            "html": self.html,
        }

class Blog (object):
    def __init__(self, title, templates, mmd):
        self.title = title
        self.templates = templates
        self.mmd = mmd
        self.posts = {}
        self.all_posts = []
        self.posts_tagged = defaultdict(lambda : [])
        self._canonical_post_key = id
        def comparator(a, b):
            return self._canonical_post_key(a) - self._canonical_post_key(b)
        self._canonical_post_comparator = comparator

    def _canonicalize_post_list(self, postlist):
        postlist.sort(key=self._canonical_post_key)

    def _add_tagged(self, tag, post):
        rv = self.posts_tagged[tag]
        if post not in rv:
            rv.append(post)
        self._canonicalize_post_list(rv)
        self.posts_tagged[tag] = rv

    def tag_size(self, tag):
        return len(self.posts_tagged[tag])

    def tag_fetch(self, tag, negate=False):
        if negate:
            for post in self.all_posts:
                if tag not in post.tags:
                    yield post
        else:
            for post in self.posts_tagged[tag]:
                yield post

    def tag_query(self, query):
        import tags
        pquery = tags.parse_tag_query(query)
        pquery = tags.reorder_query(pquery, self.tag_size)
        return tags.perform_query(pquery,
                                  self._canonical_post_comparator,
                                  self.tag_fetch)

    def url(self, suffix):
        url = suffix
        if not url.startswith("/"):
            url = "/" + url
        return url

    def template_args(self):
        return {
            "title": self.title,
        }

    def render_post(self, post):
        template = self.templates["blogpost"]
        return pystache.render(template, {
            "blog": self.template_args(),
            "post": post.template_args(self),
        })

    def render_index(self, posts):
        template = self.templates["blogindex"]
        return pystache.render(template, {
            "blog": self.template_args(),
            "posts": [post.template_args(self) for post in posts]
        })

    def load_post(self, markdown):
        post = BlogPost(*self.mmd.parse_all(markdown))
        self.all_posts.append(post)
        self._canonicalize_post_list(self.all_posts)
        for tag in post.tags:
            self._add_tagged(tag, post)
        for slug in post.slugs:
            self.posts[slug] = post
    
def read_directory_files(directory, pattern, by="pattern"):
    regex = re.compile(pattern)
    rv = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            m = regex.match(filename)
            if not m:
                continue
            path = os.path.join(root, filename)
            def key_by_path():
                return path
            def key_by_pattern():
                return m.groups()[0]
            key = {
                "path": key_by_path,
                "pattern": key_by_pattern,
            }[by]()
            name = m.groups()[0]
            with codecs.open(path, "r", "utf8") as f:
                rv[key] = f.read()
    return rv

def read_templates(templatedir):
    pattern = r"(.*)\.html$"
    return read_directory_files(templatedir, pattern)

def read_articles(articledir):
    pattern = r"(.*)\.mmd$"
    return read_directory_files(articledir, pattern)

if __name__ == '__main__':
    import sys, webbrowser
    from mmd import MultiMarkdown
    templates = read_templates("./template")
    mmd = MultiMarkdown("./MultiMarkdown-4/multimarkdown")
    mmd.global_headers["Base Header Level"] = 2
    blog = Blog("My Blog", templates, mmd)
    tempfile = "/tmp/mmd-test.generated.html"
    with codecs.open(sys.argv[1], "r", "utf8") as f:
        markdown = f.read()
    post = BlogPost(*mmd.parse_all(markdown))
    html = blog.render_post(post)
    with codecs.open(tempfile, "w", "utf8") as f:
        f.write(html)
    webbrowser.open(tempfile)
