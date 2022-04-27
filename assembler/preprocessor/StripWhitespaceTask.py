from .PreprocessorTask import *

class StripWhitespaceTask(PreprocessorTask):

    def process_line(self, line: str, aps: AssemblerPassState) -> str:
        if not line: return None
        return line.strip()