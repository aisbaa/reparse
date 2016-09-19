import six

from deparse.expression import Expression


class D(Expression):
    """Short for declaration

    Holds data required for parser.

    Args:
        regex(str): regular expression passed to expression object
        func(callable): optional parameter used by parser to do post matching
            processing.
    """

    def __init__(self, regex, func=None):
        super(D, self).__init__(regex)
        self.func = func


class ParserMeta(type):
    """Collects D into cls._definitions dict"""

    def __new__(cls, clsname, bases, dct):
        attr = dct.copy()
        definitions = {
            name: d for name, d in dct.items() if isinstance(d, D)
        }

        for name, d in definitions.items():
            if d.func is None:
                d.func = 'f_' + name

        attr['_definitions'] = definitions
        return super(ParserMeta, cls).__new__(
            cls,
            clsname,
            bases,
            attr
        )


@six.add_metaclass(ParserMeta)
class Parser(object):
    """Turns textual data into python dict/object

    Each line in a file gets parsed by expression, result is added to output
    dictionary. Expression name is used as a key in result dictionary

    Args:
        inp(file/string): input file or string to be parsed.

    Example:

        >>> from datetime import datetime
        >>> class AWSParser(Parser):
        ...     price = D(r'\$(\d+)', func=int)
        ...     service = D(r'(aws-[\w-]+)', func='f_echo')
        ...     date = D(
        ...         r'(\d{4}-\d{2}-\d{2})',
        ...         func=lambda x: datetime.strptime(x, '%Y-%m-%d').date())
        ...
        ...     @staticmethod
        ...     def f_echo(arg):
        ...         return arg
        ...
        >>> res = AWSParser.line('aws-s3-bucket 6GB $10 2015-01-14')
        >>> res['service']
        'aws-s3-bucket'
        >>> res['date']
        datetime.date(2015, 1, 14)
        >>> res['price']
        10
    """

    class SkipResult(Exception):
        """Post processing function can raise this exception to exclude current
        result
        """
        pass

    def __init__(self, inp=None):
        for attr, val in self.parse_file(inp).items():
            if hasattr(self, attr):
                setattr(self, attr, val)

    @classmethod
    def line(cls, line):
        """Returns a dictionary of results processed by all expressions.

        Args:
            line (str): to be parsed with all definitions

        Returns:
            dict: {expression.name: result}
        """
        output = {}
        for name, d in cls._definitions.items():
            # one expression can yield multiple matches, or None
            for match in d.findall(line):
                try:
                    output = cls.merge_output(
                        output,
                        {
                            name: cls.apply_function(d, match)
                        }
                    )
                except cls.SkipResult:
                    pass
        return output

    @classmethod
    def apply_function(cls, d, match):
        """Calls function specified in D.func"""
        func = d.func if callable(d.func) else getattr(cls, d.func)
        if isinstance(match, str):
            return func(match)
        else:
            return func(*match)


    @classmethod
    def parse_file(cls, f):
        """Calls self.line for each line in file. Composes dict of data
        returned by expressions for each line in a file.

        """
        final_output = {}
        for line in f:
            output = cls.line(line)
            cls.merge_output(final_output, output)
        return final_output

    @staticmethod
    def merge_output(result, part):
        """Merges two dictionaries in a way that no data is lost.

        >>> Parser.merge_output({'a': 3}, {'a': 4})
        {'a': [3, 4]}
        >>> Parser.merge_output({}, None)
        {}
        >>> Parser.merge_output({}, [])
        {}
        """
        if not part:
            return result

        for k, v in part.items():
            if k not in result:
                # no key in result dict
                result[k] = v
                continue
            # key is in result dictionary
            result_value = result[k]
            if isinstance(result_value, list):
                result_value.append(v)
            else:
                result[k] = [result_value, v]
        return result
