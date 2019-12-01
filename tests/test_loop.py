import unittest

from staticpy import jit, Int
from staticpy.common.options import set_option


class LoopTest(unittest.TestCase):
    def test_for(self):
        @jit
        def fn_for(n: Int) -> Int:
            s: Int = 0
            for i in range(n):
                s += i
            return s

        self.assertEqual(fn_for(5), 10)

    def test_while(self):
        @jit
        def fn_while(n: Int) -> Int:
            i: Int = 0
            s: Int = 0
            while i < n:
                s += i
                i += 1
            return s

        self.assertEqual(fn_while(5), 10)
