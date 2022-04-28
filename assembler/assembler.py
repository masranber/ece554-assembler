from abc import abstractmethod
from bitstring import Bits
from typing import Dict, Any, List

from assembler.preprocessor import PreprocessorTask

from assembler.isa import *
from assembler.state import *
from assembler.exceptions import AssemblerWarning, AssemblerError

from assembler.preprocessor import preprocessor
from assembler.synthesis import Synthesizer


class Assembler(object):
    
    def __init__(self, preprocessor: preprocessor, synthesizer: Synthesizer):
        self.__preprocessor = preprocessor
        self.__synthesizer = synthesizer

    def assemble(self, source_str: str, filename: str = None) -> Bits:
        return self.assemble_lines(source_str.splitlines(), filename)

    def assemble_lines(self, source_lines: List[str], filename: str = None) -> Bits:
        if not self.__preprocessor or not self.__synthesizer:
            raise ValueError('Assembler must have a preprocessor and synthesizer! One or both were not set in the constructor.')

        self.__preprocessor.reset()
        self.__synthesizer.reset()

        aps = AssemblerPassState()
        aps.filename = filename
        aps.lineno = 0
        aps.pc_addr = 0

        # Assembler Pass 1: Preprocess the source code lines, build the symbol table
        processed_lines = []
        for line in source_lines:
            processed_lines.append(self.__preprocessor.process_line(line, aps))
            aps.lineno += 1

        aps.lineno = 0
        aps.pc_addr = 0

        # Assembler Pass 2: Synthesize the processed source code lines into machine code
        text_segment = BitString()
        for i, instr in enumerate(processed_lines):
            b, _ = self.__synthesizer.process_instruction(instr, source_lines[i], aps)
            aps.lineno += 1
            if b is not None:
                text_segment.append(b)
                aps.pc_addr += 2
                print_info(aps, '\'{:20s}\' -> {} (0x{})'.format(instr, b.bin, b.hex))

        #text_segment.byteswap(2) # change endianness of the machine code
        return text_segment
        


    def assemble_file(self, filepath: str) -> Bits:
        with open(filepath, 'r') as src_file:
            return self.assemble_lines(src_file.readlines(), src_file.name)

        

