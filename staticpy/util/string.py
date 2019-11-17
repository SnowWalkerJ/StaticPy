import os


def stringify_arguments(args):
    from ..lang.expression import cast_value_to_expression
    return ", ".join(map(str, map(cast_value_to_expression, args)))


def get_target_filepath(path, libname):
    with os.popen("python3-config --extension-suffix") as f:
        suffix = f.read().strip("\n")
    return os.path.join(path, libname + suffix)


def function_pointer_signature(inputs, output):
    args = ", ".join(str(t) for t, n in inputs)
    return f"{output} (*)({args})"
