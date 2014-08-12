import web
import codecs
from blog import Blog, read_templates
from mmd import MultiMarkdown

urls = (
    "/posts/(.+)", "Post",
    "/posts", "PostIndex",
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
    blog.load_post(f.read())

def not_found():
    return web.notfound("404!")

class Post (object):
    def GET(self, slug):
        try:
            post = blog.posts[slug]
        except KeyError:
            raise not_found()
        return blog.render_post(post)

class PostIndex (object):
    def GET(self):
        posts = blog.posts.values()
        return blog.render_index(posts)

if __name__ == '__main__':
    app.run()
