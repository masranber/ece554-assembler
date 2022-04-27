from .PreprocessorTask import *

from bitstring import Bits

class AddressingTask(PreprocessorTask):

    def __init__(self, labelSuffix: str):
        self.__labelSuffix = labelSuffix

    def process_line(self, line: str, aps: AssemblerPassState) -> str:
        if not line: return None
        if self.__labelSuffix and line.endswith(self.__labelSuffix):
            label_name = line[:-1].strip()
            label_addr = Bits(uint=aps.pc_addr, length=64)
            #print('FOUND LABEL \'{}\' at address {}'.format(label_name, aps.pc_addr))
            aps.add_symbol(label_name, label_addr)
            return None
        return line