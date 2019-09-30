import unittest

from staticpy import jit, Int


class RecursiveTest(unittest.TestCase):
    def test_recursive_call(self):
        @jit
        def fn(n: Int) -> Int:
            if n == 0:
                return 1
            else:
                return n * fn(n) - 1

        self.assertEqual(fn(5), 120)
