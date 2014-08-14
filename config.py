import yaml
import codecs
import argparse
import os.path

Defaults = {
    "server": {
        "port": 8080,
    },
    "articles": {
        "path": "articles/",
    },
    "templates": {
        "path": "templates/",
    },
    "mmd": {
        "path": "./MultiMarkdown-4/multimarkdown",
        "header-level": 1,
    },
}

Description = "Simple blogging engine based on multimarkdown."

CommandLineSwitches = {
    "server.port": {
        "type": int,
        "help": "port for the server to listen on",
    },
    "templates.path": {
        "help": "path under which to search for templates",
    },
    "articles.path": {
        "help": "path under which to search for articles",
    },
    "blog.title": {
        "help": "blog title",
    },
}

def deep_get_in_configs(configs, keys):
    for config in configs:
        try:
            return deep_get_in_config(config, keys)
        except KeyError:
            pass
    raise KeyError(keys)

def split_composite_key(composite_key):
    return composite_key.split(".")

class CookedConfig (object):
    def __init__(self, config={}):
        self.config = config

    def __getitem__(self, composite_key):
        keys = split_composite_key(composite_key)
        node = self.config
        for key in keys:
            node = node[key]
        return node

class ConfigCascade (object):
    def __init__(self, defaults):
        self.configs = [defaults]

    def __getitem__(self, key):
        for config in reversed(self.configs):
            try:
                return config[key]
            except KeyError:
                pass
        raise KeyError(key)

    def add_overrides(self, config):
        self.configs.append(config)

class YamlConfig (CookedConfig):
    def __init__(self, stream_or_string):
        self.config = yaml.load(stream_or_string)

    @staticmethod
    def load_file(filename):
        with codecs.open(filename, "r", "utf8") as f:
            return YamlConfig.load_string(f.read())

    @staticmethod
    def load_string(string):
        return YamlConfig(string)

class ArgparseConfig (object):
    def __init__(self, parsed_args):
        self.config = parsed_args.__dict__

    def __getitem__(self, key):
        rv = self.config[key]
        if rv is None:
            raise KeyError(key)
        return rv

def config_basename(composite_key):
    try:
        i = composite_key.rindex(".")
    except ValueError:
        return composite_key
    return composite_key[i+1:]

def parse_args_to_config(cmdargs=None,
                         defaults=Defaults,
                         default_config_filename="blog.yaml",
                         description=Description,
                         switches=CommandLineSwitches):
    parser = argparse.ArgumentParser(description=description)
    cc = ConfigCascade(CookedConfig(defaults))
    parser.add_argument("configs",
                        metavar="CFG",
                        type=str,
                        nargs="*",
                        help="configuration files to load (searched in order)")
    for dest, data in switches.items():
        helpmessage = "{} ({})".format(data["help"], dest)
        metavar = config_basename(dest).upper()
        arg = "--" + "-".join(split_composite_key(dest))
        parser.add_argument(arg,
                            dest=dest,
                            metavar=metavar,
                            type=data.get("type",str),
                            help=helpmessage)
    args = parser.parse_args(cmdargs)
    configs = args.configs or [default_config_filename]
    for config_filename in configs:
        cc.add_overrides(YamlConfig.load_file(config_filename))
    cc.add_overrides(ArgparseConfig(args))
    if args.configs:
        primary_config = args.configs[0]
        basepath, _ = os.path.split(os.path.abspath(primary_config))
        cc.add_overrides({"basepath": basepath})
    return cc

def get_path(cfg, key):
    relpath = cfg[key]
    if relpath.startswith(".") or relpath.startswith("/"):
        return relpath
    basepath = cfg["basepath"]
    joined = os.path.join(basepath, relpath)
    return os.path.abspath(joined)

if __name__ == '__main__':
    import sys
    cfg = parse_args_to_config()
    keys = ["server.port"]
    for key in keys:
        sys.stdout.write("{}\t\t".format(key))
        sys.stdout.flush()
        rv = cfg[key]
        sys.stdout.write(str(cfg[key])+"\n")
