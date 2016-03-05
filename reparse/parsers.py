""" Contains all the parser types and the parser generator.
"""
from reparse.expression import SimpleExpression

def basic_parser(patterns, with_name=None):
    """ Basic ordered parser.
    """
    def parse(line):
        output = None
        highest_order = 0
        highest_pattern_name = None
        for pattern in patterns:
            results = pattern.findall(line)
            if results and any(results):
                if pattern.order > highest_order:
                    output = results
                    highest_order = pattern.order
                    if with_name:
                        highest_pattern_name = pattern.name
        if with_name:
            return output, highest_pattern_name
        return output

    return parse


def alt_parser(patterns):
    """ This parser is able to handle multiple different patterns
        finding stuff in text-- while removing matches that overlap.
    """
    from reparse.util import remove_lower_overlapping
    get_first = lambda items: [i[0] for i in items]
    get_second = lambda items: [i[1] for i in items]

    def parse(line):
        output = []
        for pattern in patterns:
            results = pattern.scan(line)
            if results and any(results):
                output.append((pattern.order, results))
        return get_first(reduce(remove_lower_overlapping, get_second(sorted(output)), []))

    return parse


def pattern_list(patterns):
    """ You can use this in the parser_type to
        simply get your list of patterns.
    """
    return patterns


def build_tree_parser(patterns):
    """ This parser_type simply outputs an array of [(tree, regex)]
        for use in another language.
    """
    def output():
        for pattern in patterns:
            yield (pattern.build_full_tree(), pattern.regex)
    return list(output())


def parser(parser_type=basic_parser, functions=None, patterns=None, expressions=None, patterns_yaml_path=None,
           expressions_yaml_path=None):
    """ A RE|PARSE parser description.
        Simply provide the functions, patterns, & expressions to build.
        If you are using YAML for expressions + patterns, you can use
        ``expressions_yaml_path`` & ``patterns_yaml_path`` for convenience.

        The default parser_type is the basic ordered parser.
    """
    from reparse.builders import build_all
    from reparse.validators import validate

    def _load_yaml(file_path):
        import yaml
        with open(file_path) as f:
            return yaml.safe_load(f)

    assert expressions or expressions_yaml_path, "RE|PARSE can't build a parser without expressions"
    assert patterns or patterns_yaml_path, "RE|PARSE can't build a parser without patterns"
    assert functions, "RE|PARSE can't build without a functions"

    if patterns_yaml_path:
        patterns = _load_yaml(patterns_yaml_path)
    if expressions_yaml_path:
        expressions = _load_yaml(expressions_yaml_path)
    validate(patterns, expressions)

    return parser_type(build_all(patterns, expressions, functions))


class Parser(object):
    """Parser allows to apply multiple regular expresions on same data.

    Each result is added to output dictionary.

    Args:
        expresions: multiple instances of Expression.

    Example:

        >>> from datetime import datetime
        >>> parser_obj = Parser(
        ...     SimpleExpression('price', r'\$(\d+)', lambda x: int(x)),
        ...     SimpleExpression('service', r'(aws-[\w-]+)', lambda x: x),
        ...     SimpleExpression(
        ...         'date', r'(\d{4}-\d{2}-\d{2})',
        ...         lambda x: datetime.strptime(x, '%Y-%m-%d').date()
        ...     ),
        ... )
        >>> result = parser_obj.line('aws-s3-bucket 6GB $10 2015-01-14')
        >>> result['service']
        'aws-s3-bucket'
        >>> result['price']
        10
        >>> result['date']
        datetime.date(2015, 1, 14)
    """

    def __init__(self, *expressions):
        self.expressions = expressions

    def line(self, line):
        """Returns a dictionary of results processed by all expressions.

        Args:
            line (str): string

        Returns:
            dict: {expression.name: result}
        """
        output = {}
        for expression in self.expressions:
            # one expresion can yield multiple matches, or None
            for res in expression.findall(line):
                output = self.merge_output(
                    output,
                    {
                        expression.name: res
                    }
                )
        return output

    def parse_file(self, f):
        """Calls self.line for each line in file. Composes dict of data
        returned by expressions for each line in a file.

        """
        final_output = {}
        for line in f:
            output = self.line(line)
            self.merge_output(final_output, output)
        return final_output

    def merge_output(self, result, part):
        """Merges two dictionaries in a way that no data is lost.

        >>> parser = Parser()
        >>> parser.merge_output({'a': 3}, {'a': 4})
        {'a': [3, 4]}
        >>> parser.merge_output({}, None)
        {}
        >>> parser.merge_output({}, [])
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

    def __call__(self, source):
        if isinstance(source, str):
            return self.line(source)
        else:
            return self.parse_file(source)
