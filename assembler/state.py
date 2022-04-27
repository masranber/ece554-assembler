from typing import Dict
from bitstring import Bits

from assembler.MemorySegment import MemorySegment

SymbolTable = Dict[str, Bits]

class AssemblerPassState(object):

    def __init__(self):
        self.filename: str = None
        self.lineno: int = 0
        self.pc_addr: int = 0
        self.segment: MemorySegment = MemorySegment.NONE
        self.__sym_table = {}

    def add_symbol(self, name: str, value: Bits):
        self.__sym_table[name] = value

    def get_symbol(self, name:str) -> Bits:
        return self.__sym_table[name]
