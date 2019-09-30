import unittest

from staticpy import jit, Int


class LoopTest(unittest.TestCase):
    def test_for(self):
        @jit
        def fn(n: Int) -> Int:
            i: Int
            s: Int = 0
            for i in range(n):
                s += i
            return s

        self.assertEqual(fn(5), 10)

    def test_while(self):
        @jit
        def fn(n: Int) -> Int:
            i: Int = 0
            s: Int = 0
            while i < n:
                s += i
                i += 1
            return s

        self.assertEqual(fn(5), 10)
