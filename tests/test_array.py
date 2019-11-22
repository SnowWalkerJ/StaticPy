import unittest

import numpy as np

from staticpy import jit, Int


class TestArray(unittest.TestCase):
    def setUp(self):
        @jit
        def fn_complex_array(arr: Int[:, 2]) -> Int:
            s: Int
            i: Int
            s = 0
            for i in range(arr.shape[0]):
                s += arr[i, 0]
            return s
        self.fn = fn_complex_array
        self.x = np.arange(10, dtype=np.int32).reshape(5, 2)

    def test_simple_array(self):
        x = self.x
        self.assertEqual(self.fn(x), x[:, 0].sum())

    def test_reversed_array(self):
        x = self.x[::-1, :]
        self.assertEqual(self.fn(x), x[:, 0].sum())

    def test_strided_array(self):
        x = self.x[::2, :]
        self.assertEqual(self.fn(x), x[:, 0].sum())

    def test_skip_array(self):
        x = self.x[2:, :]
        self.assertEqual(self.fn(x), x[:, 0].sum())
