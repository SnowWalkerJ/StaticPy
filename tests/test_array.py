import array
import unittest

import numpy as np

from staticpy import jit, Int


class TestArray(unittest.TestCase):
    def test_simple_array(self):
        @jit
        def fn_simple_array(arr: Int[3]) -> Int:
            return arr[0]

        x = array.array('i', [1, 2, 3])
        self.assertEqual(fn_simple_array(x), 1)

    def test_complex_array(self):
        @jit
        def fn_complex_array(arr: Int[:, 2]) -> Int:
            s: Int
            i: Int
            s = 0
            for i in range(arr.shape[0]):
                s += arr[i, 0]
            return s

        x = np.arange(10).reshape(5, 2)
        self.assertEqual(fn_complex_array(x), 20)
