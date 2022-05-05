from typing import List
from assembler.memory import MemorySegment
from .directive_processor import DirectiveProcessor
from assembler.state import AssemblerPassState
from assembler.exceptions import AssemblerError


'''
Processes "segment" directives. Segment directives are used to control the active memory region of the assembler.
'''
class SegmentDirectiveProcessor(DirectiveProcessor):

    '''
    Sets the assembler state to the new memory segment, or raises an exception if the value
    is invalid
    '''
    def process(self, value: str, aps: AssemblerPassState):
        if not value: raise AssemblerError('Expected memory segment after directive token \'.segment\'.', aps.filename, aps.lineno, None, None)
        value_upper = value.upper() # make the name matching case insensitive
        try:
            aps.segment = MemorySegment[value_upper]
        except KeyError:
            raise AssemblerError('Invalid memory segment \'{}\' specified.'.format(value), aps.filename, aps.lineno, None, value)


'''
Processes "define" directives. Define directives are used to substitute named literal values
within instructions during the assembly process. Since directive processing happens in the same
assembler pass as define substitutions happen, define directives must be defined before reference (forward references
are not allowed unlike symbols in the symbol table)
'''
class DefineDirectiveProcessor(DirectiveProcessor):

    '''
    illegal_tokens: list of strings that definition names may NOT contain
    '''
    def __init__(self, name: str, illegal_tokens: List[str] = {}):
        super().__init__(name)
        self.__illegal_tokens = illegal_tokens


    '''
    Adds a definition's name and value pair to the assembler state's definition table for lookup/substitution later.
    Raises an exception if the name includes illegal tokens
    '''
    def process(self, value: str, aps: AssemblerPassState):
        if not value: raise AssemblerError('Expected name, value after directive token \'.define\'.', aps.filename, aps.lineno, None, None)
        try:
            def_name, def_val = value.split(' ', maxsplit=1)
            def_val = def_val.strip()
            
            if any(token in def_name for token in self.__illegal_tokens):
                raise AssemblerError('Encountered illegal token \'{}\' in define name.', aps.filename, aps.lineno, at_token=def_name)

            aps.add_define(def_name.strip(), def_val) # add to the definition table
            
        except ValueError:
            raise AssemblerError('Invalid format for define directive. Expected \'.define <NAME> <VALUE>\'', aps.filename, aps.lineno, at_token=value)