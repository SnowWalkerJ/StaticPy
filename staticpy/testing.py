import unittest

from .common.options import get_option


def enable_if_cpp_std(standards):
    def _translate(v):
        special_versions = {
            "0x": "11",
            "1y": "14",
            "1z": "17",
            "2a": "20",
        }
        v = v.strip()
        return special_versions.get(v, v)
    standards = list(map(_translate, standards.split(",")))
    version = get_option("cpp_std")[3:]

    def decorator(wrapped):
        return unittest.skipIf(version not in standards, "c++ std not match")(wrapped)
    return decorator
