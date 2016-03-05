import io

from six import u
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
            SimpleExpression('hour', r'([12]?\d)(am|pm)', time_12_to_24)
        )
        assert parser.line('1pm') == {'hour': 13}
        assert parser.line('10am') == {'hour': 10}
        assert parser.line('8pm') == {'hour': 20}

    def test_multiple_values_should_be_concatinated_a_list(self):
        parser = Parser(
            SimpleExpression('hour', r'([12]?\d)(am|pm)', time_12_to_24)
        )
        assert parser.line('1pm-4am') == {'hour': [13, 4]}

    def test_must_support_file_parsing(self):
        raw_data = u('8am - brekfast\n9am - work\n12am - lunch break\n')
        parser = Parser(
            SimpleExpression('hour', r'([12]?\d)(am|pm)', time_12_to_24)
        )
        data = parser.parse_file(io.StringIO(raw_data))
        assert set(data['hour']) == {8, 9, 12}

    def test_parser_is_able_to_merge_expresion_result(self):
        """Parser must be able to merge expresion results into one dict."""
        final_output = {}
        part_output = {'a': 3}
        parser = Parser()
        parser.merge_output(final_output, part_output)
        assert final_output == part_output

    def test_if_parser_is_callable(self):
        parser = Parser(SimpleExpression('numbers', r'\d+', int))
        result = parser('1 2 3')
        assert result['numbers'] == [1, 2, 3]
