from typing import List
from .preprocessor_task import PreprocessorTask
from assembler.state import AssemblerPassState

class Preprocessor(object):

    def __init__(self, tasks: List[PreprocessorTask]):
        self.__tasks = tasks

    def reset(self):
        for task in self.__tasks:
            task.reset()
    
    def process_line(self, line: str, aps: AssemblerPassState) -> str:
        current_line = line
        ateLine = False
        for task in self.__tasks:
            if not current_line: # If the previous preprocessor task consumed the line, break the preprocessor chain
                ateLine = True
                current_line = None
                break
            current_line = task.process_line(current_line, aps)
        if current_line and not ateLine:
            aps.pc_addr += 1 # Uneaten lines are instructions, increment the PC for each instruction
        return current_line