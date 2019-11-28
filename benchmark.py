import timeit
import inspect
import numpy as np
import numba as nb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from staticpy import jit, Double, Long, Int
from staticpy.lang import type as T

sns.set()


class Experiment:
    def __init__(self):
        self.sp_func = None
        self.nb_func = None

    @property
    def python(self):
        return self.function

    @property
    def staticpy(self):
        if self.sp_func is None:
            self.sp_func = jit(self.function)
            self.sp_func(self.x)
        return self.sp_func

    @property
    def numba(self):
        if self.nb_func is None:
            signature = self._get_nb_signature(self.function)
            self.nb_func = nb.jit(signature)(self.function)
            self.nb_func(self.x)
        return self.nb_func

    @staticmethod
    def _get_nb_signature(function):
        mapping = {
            T.Int: nb.int32,
            T.Long: nb.int64,
            T.Float: nb.float32,
            T.Double: nb.float64,
        }
        signature = inspect.signature(function)
        output = mapping[signature._return_annotation]
        inputs = []
        for t in signature.parameters.values():
            t = t.annotation
            if isinstance(t, T.ArrayType):
                base = mapping[t.base]
                if t.is_continuous:
                    inputs.append(base[::1])
                else:
                    inputs.append(base[:])
            else:
                inputs.append(mapping[t])
        sig = output(*inputs)
        return sig

    def run(self):
        names = ["Python", "Numba", "StaticPy"]
        funcs = [self.python, self.numba, self.staticpy]
        time = []
        for func in funcs:
            t = timeit.timeit("func(x)", number=10000, globals={"x": self.x, "func": func})
            time.append(t)
        speed = [time[0] / x for x in time]
        return pd.Series(speed, index=names)


def sum(x: Double[:, True]) -> Double:
    s: Double = 0.0
    i: int
    for i in range(x.shape[0]):
        s += x[i]
    return s


def recursive(n: Long) -> Long:
    if n <= 1:
        return 1
    else:
        return n * recursive(n-1)


def iteration(n: Long) -> Long:
    s: Long = 1
    while n > 1:
        s *= n
        n -= 1
    return s


def sim_trade(data: Double[:, True]) -> Double:
    ma: Double = 0.0
    i: Int
    L: Int = 5
    profit: Double = 0.0
    position: Int = 0
    for i in range(data.shape[0]):
        ma += data[i] / L
        if i >= L:
            ma -= data[i-L] / L
        if position != 0:
            profit += (data[i] - data[i-1]) * position
        position = 1 if data[i] > ma else -1
    return profit


class Sum(Experiment):
    def __init__(self):
        super().__init__()
        self.function = sum
        self.x = np.random.randn(10000)


class Recursive(Experiment):
    def __init__(self):
        super().__init__()
        self.function = recursive
        self.x = 1000


class Iteration(Experiment):
    def __init__(self):
        super().__init__()
        self.function = iteration
        self.x = 1000


class SimTrade(Experiment):
    def __init__(self):
        super().__init__()
        self.function = sim_trade
        self.x = np.cumsum(np.random.randn(1000))


class Suite:
    experiments = [Sum, Recursive, Iteration, SimTrade]
    @classmethod
    def run(cls):
        df = {}
        for exp in cls.experiments:
            name = exp.__name__
            df[name] = exp().run()
        return pd.DataFrame(df)


data = Suite.run().T

data.plot.bar(rot=0)
plt.title("Relative speed of different tasks")
plt.show()

print(data)
