import unittest
from everai_autoscaler.builtin import SimpleAutoScaler


class TestSimple(unittest.TestCase):
    def test_simple(self):
        s = SimpleAutoScaler()

        print(s)

