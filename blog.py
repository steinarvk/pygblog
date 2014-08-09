import pystache
import re
import os
import codecs

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

    def template_args(self, blog):
        tags = []
        for tag in self.tags:
            tags.append({
                "name": tag,
                "url": blog.url("/tags/" + tag)
            })
        return {
            "tags": tags,
            "title": self.title,
            "html": self.html,
        }

class Blog (object):
    def __init__(self, title, templates, mmd):
        self.title = title
        self.templates = templates
        self.mmd = mmd

    def url(self, suffix):
        return "http://www.wikipedia.org/" + suffix

    def template_args(self):
        return {
            "title": self.title,
        }

    def render_post(self, markdown):
        post = BlogPost(*self.mmd.parse_all(markdown))
        template = self.templates["blogpost"]
        return pystache.render(template, {
            "blog": self.template_args(),
            "post": post.template_args(self),
        })

def read_directory_files(directory, pattern):
    regex = re.compile(pattern)
    rv = {}
    for filename in os.listdir(directory):
        m = regex.match(filename)
        if not m:
            continue
        path = os.path.join(directory, filename)
        name = m.groups()[0]
        with codecs.open(path, "r", "utf8") as f:
            rv[name] = f.read()
    return rv

def read_templates(templatedir):
    pattern = r"(.*)\.html$"
    return read_directory_files(templatedir, pattern)

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
    html = blog.render_post(markdown)
    with codecs.open(tempfile, "w", "utf8") as f:
        f.write(html)
    webbrowser.open(tempfile)
