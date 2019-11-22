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
