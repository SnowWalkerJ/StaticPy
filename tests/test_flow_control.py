import unittest

from staticpy import jit, Int


class TestCondition(unittest.TestCase):
    def test_ifelse(self):
        @jit
        def condition(x: Int) -> Int:
            n: Int = 0
            if x < 0:
                n = 1
            elif x < 5:
                n = 2
            else:
                n = 3
            return n

        self.assertEqual(condition(-1), 1)
        self.assertEqual(condition(4), 2)
        self.assertEqual(condition(6), 3)


class TestLoop(unittest.TestCase):
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
