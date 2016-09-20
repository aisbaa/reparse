from unittest import TestCase
from deparse.expression import Expression, InvalidPattern


class TestExpression(TestCase):

    def test_raises_useful_exception(self):
        try:
            expression = Expression(r'inalid (\d]')
            assert not expression.pattern
        except InvalidPattern as exp:
            assert '"inalid (\d]"' in str(exp)
