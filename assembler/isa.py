from abc import abstractmethod
from typing import NamedTuple, Dict, List

from bitstring import BitArray, Bits, BitStream, BitString, CreationError

from assembler.exceptions import AssemblerWarning, AssemblerError
from assembler.state import AssemblerPassState
from assembler.utils import resize_bits

class Opcode(NamedTuple):
    name: str
    bitstring: Bits

class Register(NamedTuple):
    name: str
    bitstring: Bits

# Type Aliases (equiv to typedef in C++)
OpcodeTable = Dict[str, Opcode]     # Maps opcode names to opcodes
RegisterTable = Dict[str, Register] # Maps register names to registers

class AssembledBitString(NamedTuple):
    bitstring: Bits
    warnings: List[AssemblerWarning]

class Operand(object):

    def __init__(self, length: int):
        self.length = length

    @abstractmethod
    def process_str(self, opd_str: str) -> AssembledBitString:
        pass

    @abstractmethod
    def process_symbol(self, opd_bits: Bits) -> AssembledBitString:
        pass

class ImplicitOperand(Operand):

    def __init__(self, value: Bits):
        super().__init__(len(value))
        self.__value = value

    @classmethod
    def ZEROS(cls, length: int):
        return cls(Bits(length))

    @classmethod
    def DONT_CARES(cls, length: int):
        return cls.ZEROS(length)

    def process_str(self, opd_str: str) -> AssembledBitString:
        if opd_str:
            raise AssemblerError('Unexpected operand.')
        return (self.__value, None)

    def process_symbol(self, opd_bits: Bits) -> AssembledBitString:
        if opd_bits:
            raise AssemblerError('Unexpected operand.')
        return (self.__value, None)

class RegisterOperand(Operand):

    def __init__(self, length: int, registers: RegisterTable):
        super().__init__(length)
        self.registers = registers

    def process_str(self, opd_str: str) -> AssembledBitString:
        opd_str = opd_str.strip()
        if opd_str[0] != '$': raise AssemblerError('Unknown format specifier \'{}\' for operand of type \'register\'. Expected \'{}\'.'.format(opd_str[0], '$'), at_token=opd_str)

        reg_name, *t = opd_str[1:].split(' ', maxsplit=1)
        if t:
            raise AssemblerError('Unexpected additional token \'{}\' found for operand of type \'register\'.'.format(t[0]), at_token=opd_str)

        try:
            return AssembledBitString(self.registers[reg_name].bitstring, warnings=None)
        except KeyError:
            raise AssemblerError('Unknown CPU register \'{}\'.'.format(reg_name), at_token=opd_str)

    def process_symbol(self, opd_bits: Bits) -> AssembledBitString:
        try:
            opd_bits = resize_bits(opd_bits, self.length, is_signed=False)
            if not opd_bits in self.registers.values():
                raise AssemblerError('Unknown CPU register symbol \'{}\'.'.format(opd_bits.bin))
            else:
                return AssembledBitString(opd_bits, warnings=None)
        except ValueError:
            raise AssemblerError('Invalid symbol \'{}\' for type CPU register of length {} bits.'.format(opd_bits.uint, self.length))
    

class ImmediateOperand(Operand):
    
    def __init__(self, length: int, is_signed: bool = True):
        super().__init__(length)
        self.is_signed = is_signed

    def process_str(self, opd_str: str) -> AssembledBitString:
        opd_str = opd_str.strip()
        if opd_str[0] != '#': raise AssemblerError('Unknown format specifier \'{}\' for operand of type \'immediate\'. Expected \'{}\'.'.format(opd_str[0], '#'), at_token=opd_str)

        imm_str, *t = opd_str[1:].split(' ', maxsplit=1)

        if t:
            raise AssemblerError('Unexpected additional token \'{}\' found for operand of type \'immediate\'.'.format(t[0]), at_token=opd_str)

        try:
            imm_bits = Bits(auto=imm_str)
            imm_bits.int
            try:
               return self.process_symbol(imm_bits)
            except AssemblerError as e:
                e.at_token = opd_str
                raise e
        except ValueError:
            try:
                imm_bits = Bits(int=int(imm_str), length=64) if self.is_signed else Bits(uint=int(imm_str), length=64)
                try:
                    return self.process_symbol(imm_bits)
                except AssemblerError as e:
                    e.at_token = opd_str
                    raise e
            except CreationError:
                raise AssemblerError('Literal \'{}\' is not a valid immediate of type \'{}-bit {} integer\'.'.format(imm_str, self.length, 'signed' if self.is_signed else 'unsigned'), at_token=opd_str)

    def process_symbol(self, opd_bits: Bits) -> AssembledBitString:
        try:
            return AssembledBitString(resize_bits(opd_bits, self.length, self.is_signed), warnings=None)
        except ValueError as e:
            raise AssemblerError(e)


class Instruction(object):

    OPERAND_DELIM = ','
    
    def __init__(self, opcode: Opcode, **kwargs: Operand):
        self.__opcode = opcode
        self.__operands = kwargs

    def process_str(self, opds_str: str, aps: AssemblerPassState) -> AssembledBitString:
        bitstring = BitString(self.__opcode.bitstring)
        warnings: List[AssemblerWarning] = list()

        if opds_str is None: raise ValueError('opds_str cannot be None.')

        if not opds_str and len(self.__operands) == 0:
            return (bitstring, warnings)

        opd_strs = opds_str.split(Instruction.OPERAND_DELIM)

        if len(opd_strs) > len(self.__operands):
            bad_index = len(self.__operands)
            raise AssemblerError('Unexpected operand \'{}\' at position {} for instruction of type \'{}\'. Expected {} operands, but {} were provided.'.format(opd_strs[bad_index], bad_index, self.__opcode.name, len(self.__operands), len(opd_strs)), at_token=opds_str)

        i: int = 0
        opd_name: str
        opd: Operand
        for i, (opd_name, opd) in enumerate(self.__operands.items()):
            if type(opd) == ImplicitOperand:
                opd_strs.insert(i, '')
            try:
                opd_str = opd_strs[i].strip()
                opd_bitstring = None
                opd_warnings = None
                try:
                    opd_bitstring, opd_warnings = opd.process_symbol(aps.get_symbol(opd_str))
                except KeyError:
                    opd_bitstring, opd_warnings = opd.process_str(opd_str)
                except AssemblerError as e:
                    if not e.at_token: e.at_token = opd_str
                    raise e
                
                bitstring.append(opd_bitstring)
                warnings.append(opd_warnings)
                
            except IndexError:
                raise AssemblerError('Expected operand \'{}\' at position {} for instruction of type \'{}\'. Expected {} operands, only {} were provided.'.format(opd_name, i, self.__opcode.name, len(self.__operands), len(opd_strs)), at_token=opds_str)

        return (bitstring, warnings)


# Type Aliases (equiv to typedef in C++)
InstructionSet = Dict[str, Instruction] # Maps opcodes to instruction definitions