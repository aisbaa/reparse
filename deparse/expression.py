import re


class InvalidPattern(Exception):
    """Helps to debug lazy regex

    Since Expression is evaluated on first use and parser contains multiple
    epxressions at the same time. It might be hard to know which regex is
    faulty.

    """

    def __init__(self, pattern, regex_error):
        super(InvalidPattern, self).__init__()
        self.pattern = pattern
        self.regex_error = regex_error

    def __str__(self):
        return '%{0.regex_error} in "{0.pattern}" pattern'.format(self)


class Expression(object):
    """Slightly enhanced regex expression

    Adds lazy evaluation. Raises InvalidPattern expcetion instead of re.error
    which includes patter in error message.

    """

    def __init__(self, regex):
        """
        Args:
            regex (str): regular expression used in findall method.
        """
        super(Expression, self).__init__()

        self.regex = regex
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
        """Yields result one by one"""
        for match in self.pattern.findall(string):
            yield match
