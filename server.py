import web
import codecs
import config
from blog import Blog, read_templates, read_articles
from mmd import MultiMarkdown

urls = (
    "/posts/(.+)", "Post",
    "/posts/?", "PostIndex",
)

class Application (web.application):
    def run(self, port, *middleware):
        func = self.wsgifunc(*middleware)
        listener = "0.0.0.0", port
        return web.httpserver.runsimple(func, listener)

app = Application(urls, globals())

def not_found():
    return web.notfound("404!")

class Post (object):
    def GET(self, slug):
        blog = web.ctx.blog
        try:
            post = blog.posts[slug]
        except KeyError:
            raise not_found()
        return blog.render_post(post)

class PostIndex (object):
    def GET(self):
        blog = web.ctx.blog
        posts = blog.posts.values()
        return blog.render_index(posts)

def create_mmd(cfg):
    import mmd
    binary_path = cfg["mmd.path"]
    header_level = cfg["mmd.header-level"]
    args = {
        "Base Header Level": header_level,
    }
    return mmd.MultiMarkdown(binary_path, args)

def create_blog(cfg):
    blogname = cfg["blog.title"]
    templatedir = config.get_path(cfg, "templates.path")
    templates = read_templates(templatedir)
    articledir = config.get_path(cfg, "articles.path")
    articles = read_articles(articledir)
    mmd = create_mmd(cfg)
    blog = Blog(blogname, templates, mmd)
    for article in articles.values():
        blog.load_post(article)
    return blog

def main(cfg):
    blog = create_blog(cfg)
    def load_hook():
        web.ctx.blog = blog
    app.add_processor(web.loadhook(load_hook))
    app.run(cfg["server.port"])

if __name__ == '__main__':
    cfg = config.parse_args_to_config()
    main(cfg)
