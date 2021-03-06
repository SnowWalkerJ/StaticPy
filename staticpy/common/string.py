import os


def get_target_filepath(path, libname):
    with os.popen("python3-config --extension-suffix") as f:
        suffix = f.read().strip("\n")
    return os.path.join(path, libname + suffix)


def function_pointer_signature(inputs, output, namespace):
    from ..lang import expression as E
    args = ", ".join(str(t) for t, n in inputs)
    sig = "*" if namespace is None else E.ScopeAnalysis(namespace, "*")
    return f"{output} ({sig})({args})"
