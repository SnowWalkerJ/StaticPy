import math
import unittest

from staticpy import jit, Int
from staticpy.lib import cmath
from staticpy.util.extern import ExternalFunction


class TestLib(unittest.TestCase):
    def test_math_cos(self):
        @jit
        def mycos(x: float) -> float:
            return cmath.cos(x)
        self.assertAlmostEqual(mycos(0.1), cmath.cos(0.1))
        self.assertAlmostEqual(mycos(0.2), cmath.cos(0.2))
        self.assertAlmostEqual(mycos(0.3), cmath.cos(0.3))

    def test_external_function(self):
        cos = ExternalFunction("cos", "<cmath>", "std")
        @jit
        def mycos2(x: float) -> float:
            return cos(x)

        self.assertAlmostEqual(mycos2(0.1), math.cos(0.1))
