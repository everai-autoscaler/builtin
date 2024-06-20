import unittest

from everai_autoscaler.builtin import BuiltinFactory
from everai_autoscaler.builtin.decorator.factors import FactorsFactory
from everai_autoscaler.builtin.decorator.arguments import ArgumentsFactory


class TestFactory(unittest.TestCase):
    def test_factory(self):
        print('------------- f1 -------------')
        f1 = BuiltinFactory()
        f1.dump()
        print('------------- f2 -------------')
        f2 = FactorsFactory()
        f2.dump()
        print('------------- f3 -------------')
        f3 = ArgumentsFactory()
        f3.dump()
