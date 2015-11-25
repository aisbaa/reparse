from unittest import TestCase

from reparse import Parser, SimpleExpression


def time_12_to_24(*args):
    """Converts 12 hour time to 24 hour time."""
    hour, am_pm = args
    hour = int(hour)
    if am_pm == 'pm':
        hour += 12
    return hour


class TestParserClass(TestCase):

    def test_minimal_constructor(self):
        """Parser API has to be simple enough to construct it on a fly."""
        parser = Parser(
            SimpleExpression('hour', '([12]?\d)(am|pm)', time_12_to_24)
        )
        assert parser.line('1pm') == {'hour': 13}
        assert parser.line('10am') == {'hour': 10}
        assert parser.line('8pm') == {'hour': 20}
