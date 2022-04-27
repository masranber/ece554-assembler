from assembler.memory import MemorySegment
from .directive import AssemblerDirective
from assembler.state import AssemblerPassState
from assembler.exceptions import AssemblerError

class MemorySegmentDirective(AssemblerDirective):

    def process(self, value: str, aps: AssemblerPassState):
        if not value: raise AssemblerError('Expected memory segment after directive token \'.segment\'.', aps.filename, aps.lineno, None, None)
        value_upper = value.upper()
        try:
            aps.segment = MemorySegment[value_upper]
            #print('SWITCHED MEMORY SEGMENT: '+aps.segment.name)
        except KeyError:
            raise AssemblerError('Invalid memory segment \'{}\' specified.'.format(value), aps.filename, aps.lineno, None, value)