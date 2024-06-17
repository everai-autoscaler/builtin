import unittest

from everai_autoscaler.builtin import BuiltinManager


class TestBuiltinManager(unittest.TestCase):
    def test_builtin_manager(self):
        builtin_manager = BuiltinManager()
        print(builtin_manager.builtins)

        s = builtin_manager.create_autoscaler('simple', {'max_workers': '3'})
        self.assertIsNotNone(s)

        builtin_manager.dump()
