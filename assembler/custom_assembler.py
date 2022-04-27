from enum import Enum, auto
from bitstring import Bits

from assembler.isa import *
from assembler.directives import DirectiveTable, MemorySegmentDirective
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
    'R0' : Register('R0', Bits(uint=0, length=INSTR_OPD_LEN_GP_REG)),
    'R1' : Register('R1', Bits(uint=1, length=INSTR_OPD_LEN_GP_REG)),
    'R2' : Register('R2', Bits(uint=2, length=INSTR_OPD_LEN_GP_REG)),
    'R3' : Register('R3', Bits(uint=3, length=INSTR_OPD_LEN_GP_REG)),
    'R4' : Register('R4', Bits(uint=4, length=INSTR_OPD_LEN_GP_REG)),
    'R5' : Register('R5', Bits(uint=5, length=INSTR_OPD_LEN_GP_REG)),
    'R6' : Register('R6', Bits(uint=6, length=INSTR_OPD_LEN_GP_REG)),
    'R7' : Register('R7', Bits(uint=7, length=INSTR_OPD_LEN_GP_REG)),
}

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


class Opcodes(Enum):
    HALT = Opcode('HALT', Bits(uint=0 , length=INSTR_OPC_LEN))
    NOP  = Opcode('NOP' , Bits(uint=1 , length=INSTR_OPC_LEN))
    ADDI = Opcode('ADDI', Bits(uint=8 , length=INSTR_OPC_LEN))
    SUBI = Opcode('SUBI', Bits(uint=9 , length=INSTR_OPC_LEN))
    STT  = Opcode('STT' , Bits(uint=16, length=INSTR_OPC_LEN))
    STS  = Opcode('STS' , Bits(uint=29, length=INSTR_OPC_LEN))
    LDO  = Opcode('LDO' , Bits(uint=17, length=INSTR_OPC_LEN))
    LDS  = Opcode('LDS' , Bits(uint=18, length=INSTR_OPC_LEN))
    VLD  = Opcode('VLD' , Bits(uint=30, length=INSTR_OPC_LEN))
    STU  = Opcode('STU' , Bits(uint=19, length=INSTR_OPC_LEN))
    VDOT = Opcode('VDOT', Bits(uint=31, length=INSTR_OPC_LEN))
    ADD  = Opcode('ADD' , Bits(uint=25, length=INSTR_OPC_LEN))
    SUB  = Opcode('SUB' , Bits(uint=25, length=INSTR_OPC_LEN))
    SEQ  = Opcode('SEQ' , Bits(uint=28, length=INSTR_OPC_LEN))
    #SLT  = Opcode('SLT' , Bits(uint=28, length=INSTR_OPC_LEN))
    #SLE  = Opcode('SLE' , Bits(uint=28, length=INSTR_OPC_LEN))
    BEQZ = Opcode('BEQZ', Bits(uint=12, length=INSTR_OPC_LEN))
    #BNEZ = Opcode('BNEZ', Bits(uint=14, length=INSTR_OPC_LEN))
    BLTZ = Opcode('BLTZ', Bits(uint=14, length=INSTR_OPC_LEN))
    #BGEZ = Opcode('BGEZ', Bits(uint=16, length=INSTR_OPC_LEN))
    LBI  = Opcode('LBI' , Bits(uint=24, length=INSTR_OPC_LEN))
    SLBI = Opcode('SLBI', Bits(uint=18, length=INSTR_OPC_LEN))
    J    = Opcode('J'   , Bits(uint=4 , length=INSTR_OPC_LEN))
    JR   = Opcode('JR'  , Bits(uint=5 , length=INSTR_OPC_LEN))
    JALR = Opcode('JALR', Bits(uint=6 , length=INSTR_OPC_LEN))


class OperandDefs:
    REG_GP         = RegisterOperand(INSTR_OPD_LEN_GP_REG   , registers=CPU_GP_REGISTERS) # General-purpose (GP) CPU register
    REG_VDOT       = RegisterOperand(INSTR_OPD_LEN_VDOT_REG , registers=VDOT_REGISTERS)   # Vector dot product (VDOT) CPU register
    IMM_BOOL       = ImmediateOperand(INSTR_OPD_LEN_IMM_BOOL, is_signed=False)            # 1-bit unsigned (boolean) immediate
    IMM3_UNSIGNED  = ImmediateOperand(INSTR_OPD_LEN_IMM3    , is_signed=False)            # 3-bit unsigned immediate
    IMM3_SIGNED    = ImmediateOperand(INSTR_OPD_LEN_IMM3    , is_signed=True )            # 3-bit signed immediate
    IMM5_UNSIGNED  = ImmediateOperand(INSTR_OPD_LEN_IMM5    , is_signed=False)            # 5-bit unsigned immediate
    IMM5_SIGNED    = ImmediateOperand(INSTR_OPD_LEN_IMM5    , is_signed=True )            # 5-bit signed immediate
    IMM8_UNSIGNED  = ImmediateOperand(INSTR_OPD_LEN_IMM8    , is_signed=False)            # 8-bit unsigned immediate
    IMM8_SIGNED    = ImmediateOperand(INSTR_OPD_LEN_IMM8    , is_signed=True )            # 8-bit signed immediate
    IMM11_UNSIGNED = ImmediateOperand(INSTR_OPD_LEN_IMM11   , is_signed=False)            # 11-bit unsigned immediate
    IMM11_SIGNED   = ImmediateOperand(INSTR_OPD_LEN_IMM11   , is_signed=True )            # 11-bit signed immediate
    ZERO_PADDING   = ImplicitOperand.ZEROS(INSTR_LEN - INSTR_OPC_LEN)                     # Padding operand (all 0's)
    ALU_OPC_ADD    = ImplicitOperand(Bits(uint=0, length=INSTR_OPD_LEN_ALU_OP))           # ALU opcode for addition instruction
    ALU_OPC_SUB    = ImplicitOperand(Bits(uint=1, length=INSTR_OPD_LEN_ALU_OP))           # ALU opcode for subtraction instruction
    ALU_OPC_XX     = ImplicitOperand.DONT_CARES(INSTR_OPD_LEN_ALU_OP)                     # ALU opcode don't care
    

INSTRUCTION_SET: InstructionSet = {
    Opcodes.HALT.name : Instruction(Opcodes.HALT.value, pad = OperandDefs.ZERO_PADDING),
    Opcodes.NOP.name  : Instruction(Opcodes.NOP.value , pad = OperandDefs.ZERO_PADDING),
    Opcodes.ADDI.name : Instruction(Opcodes.ADDI.value, Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM5_SIGNED),
    Opcodes.SUBI.name : Instruction(Opcodes.SUBI.value, Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM5_SIGNED),
    Opcodes.STT.name  : Instruction(Opcodes.STT.value , Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM5_SIGNED),
    Opcodes.STS.name  : Instruction(Opcodes.STS.value , Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM5_SIGNED),
    Opcodes.STU.name  : Instruction(Opcodes.STU.value , Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM5_SIGNED),
    Opcodes.LDO.name  : Instruction(Opcodes.LDO.value , Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM5_SIGNED),
    Opcodes.LDS.name  : Instruction(Opcodes.LDS.value , Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM5_SIGNED),
    Opcodes.VLD.name  : Instruction(Opcodes.VLD.value , Rd = OperandDefs.REG_VDOT, Rs = OperandDefs.REG_VDOT, immediate = OperandDefs.IMM5_SIGNED),
    Opcodes.VDOT.name : Instruction(Opcodes.VDOT.value, Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, ac = OperandDefs.IMM_BOOL, pad = ImplicitOperand.ZEROS(4)),
    Opcodes.ADD.name  : Instruction(Opcodes.ADD.value , Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, Rt = OperandDefs.REG_GP, alu_op=OperandDefs.ALU_OPC_ADD),
    Opcodes.SUB.name  : Instruction(Opcodes.SUB.value , Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, Rt = OperandDefs.REG_GP, alu_op=OperandDefs.ALU_OPC_SUB),
    Opcodes.SEQ.name  : Instruction(Opcodes.SEQ.value , Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, Rt = OperandDefs.REG_GP, alu_op=OperandDefs.ALU_OPC_XX),
    #Opcodes.SLT.name  : Instruction(Opcodes.SLT.value , Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, Rt = OperandDefs.REG_GP, alu_op=OperandDefs.ALU_OPC_XX),
    #Opcodes.SLE.name  : Instruction(Opcodes.SLE.value , Rd = OperandDefs.REG_GP, Rs = OperandDefs.REG_GP, Rt = OperandDefs.REG_GP, alu_op=OperandDefs.ALU_OPC_XX),
    Opcodes.BEQZ.name : Instruction(Opcodes.BEQZ.value, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM8_SIGNED),
    #Opcodes.BNEZ.name : Instruction(Opcodes.BNEZ.value, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM8_SIGNED),
    Opcodes.BLTZ.name : Instruction(Opcodes.BLTZ.value, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM8_SIGNED),
    #Opcodes.BGEZ.name : Instruction(Opcodes.BGEZ.value, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM8_SIGNED),
    Opcodes.LBI.name  : Instruction(Opcodes.LBI.value , Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM8_SIGNED),
    Opcodes.SLBI.name : Instruction(Opcodes.SLBI.value, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM8_UNSIGNED),
    Opcodes.J.name    : Instruction(Opcodes.J.value   , immediate = OperandDefs.IMM11_SIGNED),
    Opcodes.JR.name   : Instruction(Opcodes.JR.value  , Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM8_SIGNED),
    Opcodes.JALR.name : Instruction(Opcodes.JALR.value, Rs = OperandDefs.REG_GP, immediate = OperandDefs.IMM8_SIGNED),
}

class Directives(Enum):
    SEGMENT = auto()
    VALUE = auto()
    STRING = auto()
    ENTRY = auto()

DIRECTIVE_TABLE: DirectiveTable = {
    Directives.SEGMENT.name: MemorySegmentDirective(Directives.SEGMENT.name),
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
