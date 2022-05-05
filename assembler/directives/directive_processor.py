from abc import abstractmethod
from typing import Dict
from assembler.state import AssemblerPassState

'''
Abstract class for directive processors. Every directive processor has a name.
A directive processor processes a given value for that directive into either
the assembler state or internal state for later use.

Ex) The directive processor for "entry" directives (.entry 0x0000) would
process the value 0x0000
'''
class DirectiveProcessor(object):

    def __init__(self, name: str):
        self.name = name

    '''
    Called every time a new assembler pass is started.
    Used to reset the processor's internal state.
    '''
    def reset(self):
        pass

    '''
    Method that directive processors must implement to process the given
    directive value.
    '''
    @abstractmethod
    def process(self, value: str, aps: AssemblerPassState):
        pass

DirectiveTable = Dict[str, DirectiveProcessor] # Maps directive names to their directive processors