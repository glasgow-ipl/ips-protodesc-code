from .extended_diagrams import ExtendedDiagrams
from .names import Names
from .dictionarable import Dictionarable

__all__ = ['ExtendedDiagrams', 'Names', 'Dictionarable']


def parse_file(filename):
    return ExtendedDiagrams.parse_file(filename)
