class Parser(object):
    """Turns textual data into python dict

    Each line in a file gets parsed by expression, result is added to output
    dictionary. Expression name is used as a key in result dictionary

    Args:
        expresions: multiple instances of Expression.

    Example:

        >>> from datetime import datetime
        >>> from reparse.expression import Expression
        >>> parser = Parser(
        ...     Expression('price', r'\$(\d+)', lambda x: int(x)),
        ...     Expression('service', r'(aws-[\w-]+)', lambda x: x),
        ...     Expression(
        ...         'date', r'(\d{4}-\d{2}-\d{2})',
        ...         lambda x: datetime.strptime(x, '%Y-%m-%d').date()
        ...     ),
        ... )
        >>> result = parser('aws-s3-bucket 6GB $10 2015-01-14')
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
