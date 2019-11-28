import unittest

from staticpy import jit, Int


class TestExpression(unittest.TestCase):
    def test_iif(self):
        @jit
        def fn_iif(n: int) -> int:
            return 1 if n % 2 == 0 else 0

        self.assertEqual(fn_iif(2), 1)
        self.assertEqual(fn_iif(1), 0)
