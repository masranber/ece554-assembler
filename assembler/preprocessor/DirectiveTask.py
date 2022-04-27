from assembler.directives.directive import *
from assembler.exceptions import AssemblerError
from .PreprocessorTask import *

class DirectiveTask(PreprocessorTask):

    def __init__(self, directivePrefix: str, directiveTable: DirectiveTable):
        self.__prefix = directivePrefix
        self.__directiveTable = directiveTable

    def process_line(self, line: str, aps: AssemblerPassState) -> str:
        if self.__prefix:
            if line.startswith(self.__prefix):
                dir_name = None
                try:
                    dir_name, dir_val = line[1:].split(' ', maxsplit=1)
                    dir_processor: AssemblerDirective = self.__directiveTable[dir_name.upper()]
                    if dir_processor: dir_processor.process(dir_val, aps)
                    return None
                except ValueError:
                    raise AssemblerError('Invalid assembler directive format \'{}\''.format(line), aps.filename, aps.lineno, line, line)
                except KeyError:
                    print(self.__directiveTable.keys())
                    raise AssemblerError('Invalid assembler directive name \'{}\''.format(dir_name), aps.filename, aps.lineno, line, dir_name)
                except AssemblerError as e:
                    if not e.line: e.line = line
                    if not e.at_token: e.at_token = line
                    raise e
        return line