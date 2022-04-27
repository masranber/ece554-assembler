from abc import abstractmethod

from assembler.state import AssemblerPassState


class PreprocessorTask(object):

    def reset(self):
        pass

    @abstractmethod
    def process_line(self, line: str, aps: AssemblerPassState) -> str:
        pass