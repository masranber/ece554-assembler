from typing import List
from assembler.memory import MemorySegment
from .directive_processor import DirectiveProcessor
from assembler.state import AssemblerPassState
from assembler.exceptions import AssemblerError

from bitstring import Bits, CreationError


# Segment directives

class SegmentDirectiveProcessor(DirectiveProcessor):

    def process(self, value: str, aps: AssemblerPassState):
        if not value: raise AssemblerError('Expected memory segment after directive token \'.segment\'.', aps.filename, aps.lineno, None, None)
        value_upper = value.upper()
        try:
            aps.segment = MemorySegment[value_upper]
            #print('SWITCHED MEMORY SEGMENT: '+aps.segment.name)
        except KeyError:
            raise AssemblerError('Invalid memory segment \'{}\' specified.'.format(value), aps.filename, aps.lineno, None, value)

class DefineDirectiveProcessor(DirectiveProcessor):

    def __init__(self, name: str, illegal_tokens: List[str] = {}):
        super().__init__(name)
        self.__illegal_tokens = illegal_tokens

    def process(self, value: str, aps: AssemblerPassState):
        if not value: raise AssemblerError('Expected name, value after directive token \'.define\'.', aps.filename, aps.lineno, None, None)
        try:
            def_name, def_val = value.split(' ', maxsplit=1)
            def_val = def_val.strip()
            
            if any(token in def_name for token in self.__illegal_tokens):
                raise AssemblerError('Encountered illegal token \'{}\' in define name.', aps.filename, aps.lineno, at_token=def_name)

            aps.add_define(def_name.strip(), def_val)
            
        except ValueError:
            raise AssemblerError('Invalid format for define directive. Expected \'.define <NAME> <VALUE>\'', aps.filename, aps.lineno, at_token=value)