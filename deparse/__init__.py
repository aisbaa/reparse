"""DE|PARSE"""

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


from .expression import Expression
from .parsers import Parser, D


__all__ = [
    'Expression',
    'Parser',
    'D',
]
