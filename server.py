import web
import codecs
from blog import Blog, read_templates
from mmd import MultiMarkdown

urls = (
    "/post/(.*)", "Post",
)

# TODO get rid of all these globals
blogname = "My Blog"
templatedir = "./template"
test_filename = "./testdata/basic.mmd"

app = web.application(urls, globals())
mmd = MultiMarkdown("./MultiMarkdown-4/multimarkdown",
                    {"Base Header Level": 2})
templates = read_templates(templatedir)
blog = Blog(blogname, templates, mmd)

with codecs.open(test_filename, "r", "utf8") as f:
    test_markdown = f.read()

class Post (object):
    def GET(self, slug):
        return blog.render_post(test_markdown)

if __name__ == '__main__':
    app.run()
