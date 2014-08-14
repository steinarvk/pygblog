import yaml
import codecs
import argparse

Defaults = {
    "server": {
        "port": 8080,
    },
}

Description = "Simple blogging engine based on multimarkdown."

CommandLineSwitches = {
    "server.port": {
        "arg": "--port",
        "type": int,
        "help": "port for the server to listen on",
    },
}

def deep_get_in_configs(configs, keys):
    for config in configs:
        try:
            return deep_get_in_config(config, keys)
        except KeyError:
            pass
    raise KeyError

class CookedConfig (object):
    def __init__(self, config={}):
        self.config = config

    def __getitem__(self, composite_key):
        keys = composite_key.split(".")
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
        raise KeyError

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
            raise KeyError
        return rv

def config_basename(composite_key):
    try:
        i = composite_key.rindex(".")
    except ValueError:
        return composite_key
    return composite_key[i+1:]

def parse_args_to_config(cmdargs=None,
                         defaults=Defaults,
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
        parser.add_argument(data["arg"],
                            dest=dest,
                            metavar=metavar,
                            type=data["type"],
                            help=helpmessage)
    args = parser.parse_args(cmdargs)
    for config_filename in args.configs:
        cc.add_overrides(YamlConfig.load_file(config_filename))
    cc.add_overrides(ArgparseConfig(args))
    return cc

if __name__ == '__main__':
    import sys
    cfg = parse_args_to_config()
    keys = ["server.port"]
    for key in keys:
        sys.stdout.write("{}\t\t".format(key))
        sys.stdout.flush()
        rv = cfg[key]
        sys.stdout.write(str(cfg[key])+"\n")
