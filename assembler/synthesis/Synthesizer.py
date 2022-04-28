from assembler.isa import InstructionSet, InstructionProcessor, AssembledBitString
from assembler.state import AssemblerPassState

from assembler.exceptions import AssemblerWarning, AssemblerError

class Synthesizer(object):
    
    def __init__(self, instr_set: InstructionSet):
        self.__instr_set = instr_set

    def reset(self):
        pass

    def process_instruction(self, instr_str: str, line: str, aps: AssemblerPassState) -> AssembledBitString:
        if not instr_str: return AssembledBitString(None, None)
        try:
            opc_str, *opds_str = instr_str.split(' ', maxsplit=1)
            instr_proc: InstructionProcessor = self.__instr_set[opc_str.upper()]
            return instr_proc.process_str(opds_str[0] if opds_str else '', aps)
        except KeyError:
            raise AssemblerError('Failed to resolve instruction \'{}\'. Bad opcode or bad instruction format'.format(opc_str), aps.filename, aps.lineno, line, at_token=opc_str)
        except ValueError:
            raise AssemblerError('Unknown instruction format \'{}\'. Expected opcode, operands.'.format(instr_str), aps.filename, aps.lineno, line, at_token=instr_str)
        except AssemblerError as e:
            if not e.filename: e.filename = aps.filename
            if not e.line: e.line = instr_str
            if not e.at_token: e.at_token = instr_str
            if not e.lineno: e.lineno = aps.lineno
            raise e