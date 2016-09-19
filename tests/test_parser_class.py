import datetime
import io

from six import u
from unittest import TestCase

from deparse import D, Parser


class TestAWSParser(TestCase):

    class AWSParser(Parser):
        price = D(r'\$(\d+)', func=int)
        service = D(r'(aws-[\w-]+)', func='f_echo')
        date = D(
            r'(\d{4}-\d{2}-\d{2})',
        )

        @staticmethod
        def f_echo(arg):
            return arg

        @staticmethod
        def f_date(arg):
            return datetime.datetime.strptime(arg, '%Y-%m-%d').date()

    def test_aws_parser(self):
        assert self.AWSParser.line('aws-s3-bucket 6GB $10 2015-01-14') == {
            'service': 'aws-s3-bucket',
            'price': 10,
            'date': datetime.date(2015, 1, 14)
        }


class TestParserClass(TestCase):

    class TimeParser(Parser):
        hours = D(
            r'([12]?\d)(am|pm)',
        )

        @staticmethod
        def f_hours(hour, am_pm):
            """Converts 12 hour time to 24 hour time."""
            hour = int(hour)
            if am_pm == 'pm':
                hour += 12
            return hour

    def test_parse_one_line(self):
        assert self.TimeParser.line('1pm') == {'hours': 13}
        assert self.TimeParser.line('10am') == {'hours': 10}
        assert self.TimeParser.line('8pm') == {'hours': 20}

    def test_multiple_values_should_be_concatinated_a_list(self):
        assert self.TimeParser.line('1pm-4am') == {'hours': [13, 4]}

    def test_must_support_file_parsing(self):
        raw_data = u(
            '8am - brekfast\n'
            '9am - work\n'
            '12am - lunch break\n'
            '5pm - end of work\n'
        )
        result = self.TimeParser.parse_file(io.StringIO(raw_data))
        assert set(result['hours']) == {8, 9, 12, 17}

    def test_parser_is_able_to_merge_expresion_result(self):
        """Parser must be able to merge expresion results into one dict."""
        final_output = {}
        part_output = {'a': 3}
        Parser.merge_output(final_output, part_output)
        assert final_output == part_output


class TestNumberParserClass(TestCase):

    class NumberParser(Parser):
        numbers = D(r'\d+', int)

    def test_if_parser_is_callable(self):
        result = self.NumberParser.line('1 2 3')
        assert result['numbers'] == [1, 2, 3]
