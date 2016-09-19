import re


class InvalidPattern(Exception):
    """Helps to debug lazy regex

    Since Expression is evaluated on first use it might be hard to know which
    regex is faulty.
    """

    def __init__(self, pattern, regex_error):
        super(InvalidPattern, self).__init__()
        self.pattern = pattern
        self.regex_error = regex_error

    def __str__(self):
        return '%{0.regex_error} in "{0.pattern}" pattern'.format(self)


class Expression(object):
    """Slightly enhanced regex"""

    def __init__(self, regex, func=None):
        """
        Args:
            regex (str): regular expression used in findall method.
            func (function): optional function applied on matched string before
                yielding. Useful to convert string to desired type or perform
                additional processing.
        """
        super(Expression, self).__init__()

        if not func:
            func = lambda x: x

        self.regex = regex
        self.func = func
        self._compiled = None

    @property
    def pattern(self):
        """Compiled regex object"""
        if not self._compiled:
            try:
                self._compiled = re.compile(self.regex)
            except re.error as e:
                raise InvalidPattern(self.regex, e)
        return self._compiled

    def findall(self, string):
        """Parses given string and yields result

        Applies self.function before yielding result.
        """

        matches = self.pattern.findall(string)
        for match in matches:
            if isinstance(match, str):
                yield self.func(match)
            else:
                yield self.func(*match)
