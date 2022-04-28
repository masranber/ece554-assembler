from enum import Enum, auto
from bitstring import Bits

from assembler.isa import *
from assembler.directives import DirectiveTable, SegmentDirectiveProcessor
from assembler.preprocessor import *
from assembler.synthesis import Synthesizer
from assembler.assembler import Assembler

# File Syntax Constants
PREFIX_LINE_COMMENT  = ';'
PREFIX_BLK_COMMENT_S = '/*'
PREFIX_BLK_COMMENT_E = '*/'
PREFIX_IMMEDIATE     = '#'
PREFIX_REGISTER      = '$'
PREFIX_DIRECTIVE     = '.'

SUFFIX_LABEL         = ':'

# Instruction Syntax Constants
INSTR_LEN              = 16
INSTR_OPC_LEN          = 5

INSTR_OPD_DELIM        = ','

INSTR_OPD_LEN_GP_REG   = 3
INSTR_OPD_LEN_VDOT_REG = 3
INSTR_OPD_LEN_IMM_BOOL = 1
INSTR_OPD_LEN_IMM3     = 3
INSTR_OPD_LEN_IMM5     = 5
INSTR_OPD_LEN_IMM8     = 8
INSTR_OPD_LEN_IMM11    = 11
INSTR_OPD_LEN_ALU_OP   = 2

# File Extensions
FILE_EXT_ASSEMBLY    = 'asm'

CPU_GP_REGISTERS: RegisterTable = {
    '0' : Register('0', Bits(uint=0, length=INSTR_OPD_LEN_GP_REG)),
    '1' : Register('1', Bits(uint=1, length=INSTR_OPD_LEN_GP_REG)),
    '2' : Register('2', Bits(uint=2, length=INSTR_OPD_LEN_GP_REG)),
    '3' : Register('3', Bits(uint=3, length=INSTR_OPD_LEN_GP_REG)),
    '4' : Register('4', Bits(uint=4, length=INSTR_OPD_LEN_GP_REG)),
    '5' : Register('5', Bits(uint=5, length=INSTR_OPD_LEN_GP_REG)),
    '6' : Register('6', Bits(uint=6, length=INSTR_OPD_LEN_GP_REG)),
    '7' : Register('7', Bits(uint=7, length=INSTR_OPD_LEN_GP_REG)),
}

''' VDOT registers don't need special names anymore
VDOT_REGISTERS: RegisterTable = {
    'V0' : Register('V0', Bits(uint=0, length=INSTR_OPD_LEN_VDOT_REG)),
    'V1' : Register('V1', Bits(uint=1, length=INSTR_OPD_LEN_VDOT_REG)),
    'V2' : Register('V2', Bits(uint=2, length=INSTR_OPD_LEN_VDOT_REG)),
    'V3' : Register('V3', Bits(uint=3, length=INSTR_OPD_LEN_VDOT_REG)),
    'V4' : Register('V4', Bits(uint=4, length=INSTR_OPD_LEN_VDOT_REG)),
    'V5' : Register('V5', Bits(uint=5, length=INSTR_OPD_LEN_VDOT_REG)),
    'V6' : Register('V6', Bits(uint=6, length=INSTR_OPD_LEN_VDOT_REG)),
    'V7' : Register('V7', Bits(uint=7, length=INSTR_OPD_LEN_VDOT_REG)),
}
'''


class Opcodes(Enum):
    HALT = Opcode('HALT', Bits(uint=0 , length=INSTR_OPC_LEN))
    NOP  = Opcode('NOP' , Bits(uint=1 , length=INSTR_OPC_LEN))
    ADDI = Opcode('ADDI', Bits(uint=8 , length=INSTR_OPC_LEN))
    SUBI = Opcode('SUBI', Bits(uint=9 , length=INSTR_OPC_LEN))
    ST   = Opcode('ST'  , Bits(uint=16, length=INSTR_OPC_LEN))
    LD   = Opcode('LD'  , Bits(uint=17, length=INSTR_OPC_LEN))
    VLD  = Opcode('VLD' , Bits(uint=2 , length=INSTR_OPC_LEN))
    VDOT = Opcode('VDOT', Bits(uint=3 , length=INSTR_OPC_LEN))
    STU  = Opcode('STU' , Bits(uint=19, length=INSTR_OPC_LEN))
    ADD  = Opcode('ADD' , Bits(uint=25, length=INSTR_OPC_LEN))
    SUB  = Opcode('SUB' , Bits(uint=25, length=INSTR_OPC_LEN))
    SEQ  = Opcode('SEQ' , Bits(uint=28, length=INSTR_OPC_LEN))
    BEQZ = Opcode('BEQZ', Bits(uint=12, length=INSTR_OPC_LEN))
    BLTZ = Opcode('BLTZ', Bits(uint=14, length=INSTR_OPC_LEN))
    LBI  = Opcode('LBI' , Bits(uint=24, length=INSTR_OPC_LEN))
    SLBI = Opcode('SLBI', Bits(uint=18, length=INSTR_OPC_LEN))
    J    = Opcode('J'   , Bits(uint=4 , length=INSTR_OPC_LEN))
    JR   = Opcode('JR'  , Bits(uint=5 , length=INSTR_OPC_LEN))
    JALR = Opcode('JALR', Bits(uint=6 , length=INSTR_OPC_LEN))


class OperandProcessorDefs:
    REG_GP         = RegisterOperandProcessor(INSTR_OPD_LEN_GP_REG   , registers=CPU_GP_REGISTERS) # General-purpose (GP) CPU register
    #REG_VDOT       = RegisterOperandProcessor(INSTR_OPD_LEN_VDOT_REG , registers=VDOT_REGISTERS)   # Vector dot product (VDOT) CPU register
    IMM_BOOL       = ImmediateOperandProcessor(INSTR_OPD_LEN_IMM_BOOL, is_signed=False)            # 1-bit unsigned (boolean) immediate
    IMM3_UNSIGNED  = ImmediateOperandProcessor(INSTR_OPD_LEN_IMM3    , is_signed=False)            # 3-bit unsigned immediate
    IMM3_SIGNED    = ImmediateOperandProcessor(INSTR_OPD_LEN_IMM3    , is_signed=True )            # 3-bit signed immediate
    IMM5_UNSIGNED  = ImmediateOperandProcessor(INSTR_OPD_LEN_IMM5    , is_signed=False)            # 5-bit unsigned immediate
    IMM5_SIGNED    = ImmediateOperandProcessor(INSTR_OPD_LEN_IMM5    , is_signed=True )            # 5-bit signed immediate
    IMM8_UNSIGNED  = ImmediateOperandProcessor(INSTR_OPD_LEN_IMM8    , is_signed=False)            # 8-bit unsigned immediate
    IMM8_SIGNED    = ImmediateOperandProcessor(INSTR_OPD_LEN_IMM8    , is_signed=True )            # 8-bit signed immediate
    IMM11_UNSIGNED = ImmediateOperandProcessor(INSTR_OPD_LEN_IMM11   , is_signed=False)            # 11-bit unsigned immediate
    IMM11_SIGNED   = ImmediateOperandProcessor(INSTR_OPD_LEN_IMM11   , is_signed=True )            # 11-bit signed immediate
    ZERO_PADDING   = ImplicitOperandProcessor.ZEROS(INSTR_LEN - INSTR_OPC_LEN)                     # Padding operand (all 0's)
    ALU_OPC_ADD    = ImplicitOperandProcessor(Bits(uint=0, length=INSTR_OPD_LEN_ALU_OP))           # ALU opcode for addition instruction
    ALU_OPC_SUB    = ImplicitOperandProcessor(Bits(uint=1, length=INSTR_OPD_LEN_ALU_OP))           # ALU opcode for subtraction instruction
    ALU_OPC_XX     = ImplicitOperandProcessor.DONT_CARES(INSTR_OPD_LEN_ALU_OP)                     # ALU opcode don't care
    

INSTRUCTION_SET: InstructionSet = {
    Opcodes.HALT.name : InstructionProcessor(Opcodes.HALT.value, pad = OperandProcessorDefs.ZERO_PADDING),
    Opcodes.NOP.name  : InstructionProcessor(Opcodes.NOP.value , pad = OperandProcessorDefs.ZERO_PADDING),
    Opcodes.ADDI.name : InstructionProcessor(Opcodes.ADDI.value, Rd = OperandProcessorDefs.REG_GP, Rs = OperandProcessorDefs.REG_GP, immediate = OperandProcessorDefs.IMM5_SIGNED),
    Opcodes.SUBI.name : InstructionProcessor(Opcodes.SUBI.value, Rd = OperandProcessorDefs.REG_GP, Rs = OperandProcessorDefs.REG_GP, immediate = OperandProcessorDefs.IMM5_SIGNED),
    Opcodes.ST.name   : InstructionProcessor(Opcodes.ST.value  , Rd = OperandProcessorDefs.REG_GP, Rs = OperandProcessorDefs.REG_GP, immediate = OperandProcessorDefs.IMM5_SIGNED),
    Opcodes.LD.name   : InstructionProcessor(Opcodes.LD.value  , Rd = OperandProcessorDefs.REG_GP, Rs = OperandProcessorDefs.REG_GP, immediate = OperandProcessorDefs.IMM5_SIGNED),
    Opcodes.VLD.name  : InstructionProcessor(Opcodes.VLD.value , Rd = OperandProcessorDefs.REG_VDOT, Rs = OperandProcessorDefs.REG_VDOT, immediate = OperandProcessorDefs.IMM5_SIGNED),
    Opcodes.VDOT.name : InstructionProcessor(Opcodes.VDOT.value, Rd = OperandProcessorDefs.REG_GP, Rs = OperandProcessorDefs.REG_GP, ac = OperandProcessorDefs.IMM_BOOL, pad = ImplicitOperandProcessor.ZEROS(4)),
    Opcodes.STU.name  : InstructionProcessor(Opcodes.STU.value , Rd = OperandProcessorDefs.REG_GP, Rs = OperandProcessorDefs.REG_GP, immediate = OperandProcessorDefs.IMM5_SIGNED),
    Opcodes.ADD.name  : InstructionProcessor(Opcodes.ADD.value , Rd = OperandProcessorDefs.REG_GP, Rs = OperandProcessorDefs.REG_GP, Rt = OperandProcessorDefs.REG_GP, alu_op=OperandProcessorDefs.ALU_OPC_ADD),
    Opcodes.SUB.name  : InstructionProcessor(Opcodes.SUB.value , Rd = OperandProcessorDefs.REG_GP, Rs = OperandProcessorDefs.REG_GP, Rt = OperandProcessorDefs.REG_GP, alu_op=OperandProcessorDefs.ALU_OPC_SUB),
    Opcodes.SEQ.name  : InstructionProcessor(Opcodes.SEQ.value , Rd = OperandProcessorDefs.REG_GP, Rs = OperandProcessorDefs.REG_GP, Rt = OperandProcessorDefs.REG_GP, alu_op=OperandProcessorDefs.ALU_OPC_XX),
    Opcodes.BEQZ.name : InstructionProcessor(Opcodes.BEQZ.value, Rs = OperandProcessorDefs.REG_GP, immediate = OperandProcessorDefs.IMM8_SIGNED),
    Opcodes.BLTZ.name : InstructionProcessor(Opcodes.BLTZ.value, Rs = OperandProcessorDefs.REG_GP, immediate = OperandProcessorDefs.IMM8_SIGNED),
    Opcodes.LBI.name  : InstructionProcessor(Opcodes.LBI.value , Rs = OperandProcessorDefs.REG_GP, immediate = OperandProcessorDefs.IMM8_SIGNED),
    Opcodes.SLBI.name : InstructionProcessor(Opcodes.SLBI.value, Rs = OperandProcessorDefs.REG_GP, immediate = OperandProcessorDefs.IMM8_UNSIGNED),
    Opcodes.J.name    : InstructionProcessor(Opcodes.J.value   , immediate = OperandProcessorDefs.IMM11_SIGNED),
    Opcodes.JR.name   : InstructionProcessor(Opcodes.JR.value  , Rs = OperandProcessorDefs.REG_GP, immediate = OperandProcessorDefs.IMM8_SIGNED),
    Opcodes.JALR.name : InstructionProcessor(Opcodes.JALR.value, Rs = OperandProcessorDefs.REG_GP, immediate = OperandProcessorDefs.IMM8_SIGNED),
}

class Directives(Enum):
    SEGMENT = auto()
    VALUE = auto()
    STRING = auto()
    ENTRY = auto()

DIRECTIVE_TABLE: DirectiveTable = {
    Directives.SEGMENT.name: SegmentDirectiveProcessor(Directives.SEGMENT.name),
    Directives.VALUE.name: None,
    Directives.STRING.name: None,
    Directives.ENTRY.name: None,
}

class CustomPreprocessor(Preprocessor):

    def __init__(self):
        # Preprocessor tasks can have state so new instances must be constructed for each preprocessor
        PREPROCESSOR_TASKS: List[PreprocessorTask] = [
            StripCommentsTask(PREFIX_LINE_COMMENT, BlockCommentPrefix(PREFIX_BLK_COMMENT_S, PREFIX_BLK_COMMENT_E)),
            StripWhitespaceTask(),
            DirectiveTask(PREFIX_DIRECTIVE, DIRECTIVE_TABLE),
            AddressingTask(SUFFIX_LABEL),
        ]
        super().__init__(PREPROCESSOR_TASKS)

class CustomSynthesizer(Synthesizer):

    def __init__(self):
        # Instruction processors are stateless so instances can be shared across synthesizer instances
        super().__init__(INSTRUCTION_SET)


class CustomAssembler(Assembler):

    def __init__(self):
        super().__init__(CustomPreprocessor(), CustomSynthesizer())
