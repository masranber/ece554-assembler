from abc import abstractmethod
from typing import Dict
from assembler.state import AssemblerPassState

class AssemblerDirective(object):

    def __init__(self, name: str):
        self.name = name

    def reset(self):
        pass

    @abstractmethod
    def process(self, value: str, aps: AssemblerPassState):
        pass

DirectiveTable = Dict[str, AssemblerDirective] # Maps directive names to their directive processors