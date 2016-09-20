import six

from deparse.expression import Expression


class D(Expression):
    """Short for declaration

    Holds data required for parser.

    Args:
        regex(str): regular expression passed to expression object
        func(callable): optional parameter used by parser to do post matching
            processing.
        container(optional): factory function to create empty container for
            values
    """

    @staticmethod
    def single():
        return None

    def __init__(self, regex, func=None, container=None):
        super(D, self).__init__(regex)
        self.func = func
        self.container = container or D.single

    def merge(self, container, value):
        merge_func = {
            D.single: self.merge_single,
            list: self.merge_list,
            dict: self.merge_dict,
        }[self.container]
        return merge_func(container, value)

    def merge_results(self, output, part):
        # TODO(Aistis): add test for merging single
        assert type(output) == type(part) or self.container == self.single
        merge_func = {
            D.single: self.merge_single,
            list: self.merge_list_result,
            dict: self.merge_dict,
        }[self.container]

        return merge_func(output, part)

    # merge line result methods

    def merge_single(self, container, value):
        return container if value is None else value

    def merge_list(self, container, value):
        container.append(value)
        return container

    def merge_dict(self, container, value):
        container.update(value)
        return container

    # merge file results methods

    def merge_list_result(self, container, part):
        container += part
        return container


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
        ...     price = D(r'\$(\d+)', func=int, container=D.single)
        ...     service = D(r'(aws-[\w-]+)', func='f_echo', container=D.single)
        ...     date = D(
        ...         r'(\d{4}-\d{2}-\d{2})', container=D.single,
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
            output[name] = d.container()

            # one expression can yield multiple matches, or None
            for match in d.findall(line):
                try:
                    value = cls.apply_function(d, match)
                    output[name] = d.merge(output[name], value)
                except cls.SkipResult:
                    pass
        return output

    @classmethod
    def apply_function(cls, d, match):
        """Calls function specified in D.func"""
        func = d.func if callable(d.func) else getattr(cls, d.func)

        if isinstance(match, six.string_types):
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

    @classmethod
    def merge_output(cls, result, part):
        """Merges two dictionaries in a way that no data is lost.

        Example:

            >>> class AParser(Parser):
            ...     a = D(r'a', container=list, func=str)
            ...
            >>> AParser.merge_output({'a': [3]}, {'a': [4]})
            {'a': [3, 4]}
            >>> AParser.merge_output({}, None)
            {}
            >>> AParser.merge_output({}, [])
            {}
        """
        if not part:
            return result

        for name, value in part.items():
            if name not in result:
                # no key in result dict
                result[name] = value
                continue

            d = cls._definitions[name]
            result[name] = d.merge_results(result[name], value)

        return result
