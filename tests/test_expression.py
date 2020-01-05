import unittest

from staticpy import jit, Int
from staticpy.testing import enable_if_cpp_std


class TestExpression(unittest.TestCase):
    def test_iif(self):
        @jit
        def fn_iif(n: int) -> int:
            return 1 if n % 2 == 0 else 0

        self.assertEqual(fn_iif(2), 1)
        self.assertEqual(fn_iif(1), 0)

    def test_const(self):
        @jit
        def fnconst(n: int) -> int:
            x: "const" = 1
            return n + x
        self.assertEqual(fnconst(10), 11)

    def test_multiple_comparation(self):
        @jit
        def within_one(n: float) -> bool:
            return 0 < n <= 1

        self.assertTrue(within_one(0.1))
        self.assertFalse(within_one(-0.1))
        self.assertFalse(within_one(1.1))

    @enable_if_cpp_std("20")
    def test_string(self):
        @jit
        def startswith_underline(x: str) -> bool:
            return x.startswith("_")

        self.assertFalse(startswith_underline("this"))
        self.assertTrue(startswith_underline("_this"))
