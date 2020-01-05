_options = {
    "cpp_std": "c++11",
    "optimize": "3",
}


def set_option(name, value):
    global _options
    _options[name] = value


def get_option(name, default=None):
    global _options
    return _options.get(name, default)
