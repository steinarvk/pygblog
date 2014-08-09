from subprocess import Popen, PIPE
import re

class MMDParseError (Exception):
    pass

ValidKeyRegex = re.compile("^[\w\d\-]+$")
def valid_key_name(s):
    return ValidKeyRegex.match(s)

class MultiMarkdown (object):
    def __init__(self, path):
        self.path = path

    def call(self, text, *args):
        cmdline = [self.path]
        cmdline.extend(args)
        p = Popen(cmdline, stdin=PIPE, stdout=PIPE)
        data = text.encode("utf8")
        rv, _ = p.communicate(data)
        if p.returncode:
            raise MMDParseError()
        return rv.decode("utf8")

    def parse_metadata(self, data):
        """Parse MMD string and return a metadata dictionary."""
        keys = self.call(data, "-m").splitlines()
        rv = {}
        for key in keys:
            if not valid_key_name(key):
                raise MMDParseError()
            rv[key] = self.call(data, "-e", key)
        return rv

    def render_html_snippet(self, data):
        """Parse MMD string and return a HTML snippet."""
        return self.call(data, "--snippet")
    
if __name__ == '__main__':
    import webbrowser
    import sys
    mmd = MultiMarkdown("./MultiMarkdown-4/multimarkdown")
    with open(sys.argv[1], "r") as f:
        data = f.read()
    metadata = mmd.parse_metadata(data)
    html = mmd.render_html_snippet(data)
    for key, value in metadata.items():
        print key, "=", value.replace("\n", " ")
    tempfile = "/tmp/mmd-test.generated.html"
    with open(tempfile, "w") as f:
        f.write(html)
    webbrowser.open(tempfile)
