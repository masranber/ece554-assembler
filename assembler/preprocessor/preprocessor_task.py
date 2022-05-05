from abc import abstractmethod

from assembler.state import AssemblerPassState

'''
Abstract class for preprocessor tasks.
Preprocessor tasks perform a specific task on each line of source code.
Ex) A comment stripping preprocessor task may strip comments from each line of source code.
'''
class PreprocessorTask(object):

    '''
    Called each time a new assembler pass is started.
    Used to reset the processor's internal state.
    '''
    def reset(self):
        pass


    '''
    Method implemented by preprocessor tasks to perform their task on the line of source code.
    Returns the processed (modified) line or None to indicate the line should be removed from the source code tree.
    For example comment stripping tasks might return None on lines within a block comment to completely strip the line
    from future tasks in preprocessor chain.
    '''
    @abstractmethod
    def process_line(self, line: str, aps: AssemblerPassState) -> str:
        pass