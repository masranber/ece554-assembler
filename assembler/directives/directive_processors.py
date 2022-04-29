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

    def process(self, value: str, aps: AssemblerPassState):
        if not value: raise AssemblerError('Expected name, value after directive token \'.segment\'.', aps.filename, aps.lineno, None, None)
        value_upper = value.upper()
        try:
            try:
                def_name, def_val, *_ = value.split(' ', maxsplit=2)
                def_val = def_val.strip()
                is_signed = def_val.startswith('s') or def_val.startswith('S')
                imm_val = def_val[1:] if is_signed else def_val
                imm_bits = None
                try:
                    imm_bits = Bits(auto=imm_val)
                    imm_bits.int
                except ValueError:
                    try:
                        imm_bits = Bits(int=int(imm_val), length=64) if is_signed else Bits(uint=int(imm_val), length=64)
                    except CreationError:
                        raise AssemblerError('Literal \'{}\' is not a valid immediate of type \'{}-bit {} integer\'.'.format(imm_val, self.length, 'signed' if self.is_signed else 'unsigned'), at_token=def_val)

                aps.add_symbol(def_name.strip(), imm_bits)
                if _:
                    raise AssemblerError('Unexpected define parameter \'{}\'.'.format(_[0]), aps.filename, aps.lineno, at_token=value)
            except ValueError:
                raise AssemblerError('Invalid format for define directive. Expected \'.define <NAME> <VALUE>\'', aps.filename, aps.lineno, at_token=value)
        except KeyError:
            raise AssemblerError('Invalid memory segment \'{}\' specified.'.format(value), aps.filename, aps.lineno, None, value)