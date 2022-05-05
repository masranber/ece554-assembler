from typing import List
from .preprocessor_task import PreprocessorTask
from assembler.state import AssemblerPassState


'''
The preprocessor is reponsible for stripping source code down to just the instructions
for the synthesizer (which translates instructions to machine code). The preprocessor represents
the first pass of a two pass assembler (the synthesizer is the 2nd pass). To abstract this functionality
the preprocessor has a list of customizable tasks it performs sequentially on lines of source code to prepare
it for the synthesizer.
'''
class Preprocessor(object):

    def __init__(self, tasks: List[PreprocessorTask]):
        self.__tasks = tasks

    def reset(self):
        for task in self.__tasks:
            task.reset()
    
    def process_line(self, line: str, aps: AssemblerPassState) -> str:
        current_line = line
        consumed_line = False # Flag set when a preprocessor task consumes an entire line of source code (returns '' or None)
        for task in self.__tasks:
            if not current_line: # If the previous preprocessor task consumed the line, break the preprocessor chain
                consumed_line = True
                current_line = None
                break
            current_line = task.process_line(current_line, aps)
        if current_line and not consumed_line:
            aps.pc_addr += 1 # Uneaten lines are instructions, increment the PC for each instruction
        return current_line