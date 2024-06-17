import unittest
from everai_autoscaler.builtin import SimpleAutoScaler
from everai_autoscaler.builtin.is_builtin import is_builtin


class M(SimpleAutoScaler):
    ...


class TestIsBuiltin(unittest.TestCase):
    def test_builtin(self):
        s = SimpleAutoScaler()

        result = is_builtin(s)
        self.assertEqual(True, result)

    def test_not_builtin(self):
        s = M()

        result = is_builtin(s)
        self.assertEqual(False, result)

