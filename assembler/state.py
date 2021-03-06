from typing import Dict
from bitstring import Bits

from assembler.memory import MemorySegment

SymbolTable = Dict[str, Bits]

class AssemblerPassState(object):

    def __init__(self):
        self.filename: str = None
        self.lineno: int = 0
        self.pc_addr: int = 0
        self.segment: MemorySegment = MemorySegment.TEXT # Assume text (code) segment if none defined in source file
        self.__sym_table = {}
        self.__def_table = {}

    def add_symbol(self, name: str, value: Bits):
        self.__sym_table[name] = value
        #print('{}:{}: INFO: Resolved symbol \'{}\' at address {} with value 0x{}'.format(self.filename, self.lineno, name, self.pc_addr, value.hex))

    def get_symbol(self, name:str) -> Bits:
        return self.__sym_table[name]

    def add_define(self, name: str, value: str):
        self.__def_table[name] = value

    def get_define(self, name: str) -> str:
        return self.__def_table[name]

    def get_defines(self):
        return self.__def_table.items()
    
    def get_define_table(self):
        return self.__def_table

