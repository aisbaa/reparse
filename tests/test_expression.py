from unittest import TestCase
from deparse.expression import Expression, InvalidPattern


class TestExpression(TestCase):

    def test_raises_useful_exception(self):
        """Expression has to raise readable error message."""
        exp = Expression(r'inalid (\d]')
        with self.assertRaises(InvalidPattern):
            assert not exp.pattern
