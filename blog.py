import pystache
import mmd
import re
import os
import codecs

class Blog (object):
    def __init__(self, title, templates, mmd_path):
        self.title = title
        self.templates = templates
        self.mmd = mmd.MultiMarkdown(mmd_path)

    def render_post(self, markdown):
        template = self.templates["blogpost"]
        metadata = self.mmd.parse_metadata(markdown)
        html = self.mmd.render_html_snippet(markdown)
        args = {
            "blog_title": self.title,
            "post_title": metadata["title"].strip(),
            "post_html": html,
        }
        return pystache.render(template, args)

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
    templates = read_templates("./template")
    blog = Blog("My Blog",
                templates,
                "./MultiMarkdown-4/multimarkdown")
    tempfile = "/tmp/mmd-test.generated.html"
    with codecs.open(sys.argv[1], "r", "utf8") as f:
        markdown = f.read()
    html = blog.render_post(markdown)
    with codecs.open(tempfile, "w", "utf8") as f:
        f.write(html)
    webbrowser.open(tempfile)
