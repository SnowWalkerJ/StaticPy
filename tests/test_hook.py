import inspect
import os
import unittest


class HookTest(unittest.TestCase):
    def setUp(self):
        import staticpy.hook
        self.hook_module = staticpy.hook
        with open("tests/myhook.py", "r") as fin:
            source = fin.read()
        with open("myhook.py", "w") as fout:
            fout.write(source)

    def test_hook_import(self):
        import myhook
        self.assertEqual(myhook.func(1), 1)
        self.assertTrue(inspect.isbuiltin(myhook.func))

    def tearDown(self):
        self.hook_module.remove_hook()
        os.remove("myhook.py")
