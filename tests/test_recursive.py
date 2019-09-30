import unittest

from staticpy import jit, Int
from staticpy.common.options import set_option


class RecursiveTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        set_option("force_compile", True)

    def test_recursive_call(self):
        @jit
        def fn_recursive(n: Int) -> Int:
            if n == 0:
                return 1
            else:
                return n * fn_recursive(n - 1)

        self.assertEqual(fn_recursive(5), 120)
