import os


def stringify_arguments(args):
    from ..expression import cast_value_to_expression
    return ", ".join(map(str, map(cast_value_to_expression, args)))


def get_target_filepath(path, libname):
    suffix = os.popen("python3-config --extension-suffix")._stream.read().strip("\n")
    return os.path.join(path, libname + suffix)
