import unittest

from staticpy import jit, Int
from staticpy.lib import cmath


class TestLib(unittest.TestCase):
    def test_ifelse(self):
        @jit
        def mycos(x: float) -> float:
            return cmath.cos(x)

        self.assertAlmostEqual(mycos(0.1), cmath.cos(0.1))
        self.assertAlmostEqual(mycos(0.2), cmath.cos(0.2))
        self.assertAlmostEqual(mycos(0.3), cmath.cos(0.3))
