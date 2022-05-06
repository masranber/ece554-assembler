import re
from typing import Any, Dict, NamedTuple

from .preprocessor_task import *
from assembler.directives.directive_processor import DirectiveProcessor, DirectiveTable
from assembler.exceptions import AssemblerError

from bitstring import Bits


'''
Preprocessor task to process labels in the source code.
'''
class LabelTask(PreprocessorTask):

    '''
    labelSuffix: the suffix token used to identify labels
    '''
    def __init__(self, labelSuffix: str):
        self.__labelSuffix = labelSuffix

    '''
    Checks a line to see if it contains a label. If it contains a label
    the line is stripped to avoid future preprocessor tasks from processing it.
    The label and current instruction address are added to the assembler's symbol table.
    '''
    def process_line(self, line: str, aps: AssemblerPassState) -> str:
        if not line: return None
        if self.__labelSuffix and line.endswith(self.__labelSuffix):
            label_name = line[:-len(self.__labelSuffix)].strip() # exclude label suffix from the name
            label_addr = Bits(uint=aps.pc_addr, length=64)
            aps.add_symbol(label_name, label_addr)
            return None # strip entire line from source code
        return line


'''
Represents the beginning and terminating tokens of a block comment.
'''
class BlockCommentPrefix(NamedTuple):
    begin: str
    terminate: str


'''
Preprocessor task that strips comments from source code lines.
'''
class StripCommentsTask(PreprocessorTask):

    def __init__(self, lineCommentPrefix: str, blockCommentPrefix: BlockCommentPrefix):
        self.__hasUntermBlockComment = False
        self.__lineCommentPrefix = lineCommentPrefix
        self.__blockCommentPrefix = blockCommentPrefix

    def reset(self):
        self.__hasUntermBlockComment = False

    def strip_block_comments(self, line: str) -> str:
        output = ""
        cur_line = line
        while cur_line:
            if self.__hasUntermBlockComment:
                line_split = cur_line.split(self.__blockCommentPrefix.terminate, maxsplit=1)
                if len(line_split) == 2:
                    self.__hasUntermBlockComment = False
                    cur_line = line_split[1]
                else:
                    return output
            else:
                line_split = cur_line.split(self.__blockCommentPrefix.begin, maxsplit=1)
                output += line_split[0]
                if len(line_split) == 2:
                    self.__hasUntermBlockComment = True
                    cur_line = line_split[1]
                else:
                    return line_split[0]
        return output

    def strip_line_comments(self, line: str) -> str:
        if not line: return None
        if self.__lineCommentPrefix:
            return line.split(self.__lineCommentPrefix, maxsplit=1)[0]
        else:
            return line

    def process_line(self, line: str, aps: AssemblerPassState) -> str:
        no_block_comments = self.strip_block_comments(line)
        #print(no_block_comments)
        return self.strip_line_comments(no_block_comments)


'''
Preprocessor task that strips leading and trailing whitespace from source code lines.
'''
class StripWhitespaceTask(PreprocessorTask):

    def process_line(self, line: str, aps: AssemblerPassState) -> str:
        if not line: return None
        return line.strip()


'''
Preprocessor task that resolves assembler directives in the source code.
'''
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
                    dir_processor: DirectiveProcessor = self.__directiveTable[dir_name.upper()] # uppercase makes the names case insensitive
                    if dir_processor: dir_processor.process(dir_val.strip(), aps)
                    return None
                except ValueError:
                    raise AssemblerError('Invalid assembler directive format \'{}\''.format(line), aps.filename, aps.lineno, line, line)
                except KeyError:
                    raise AssemblerError('Invalid assembler directive name \'{}\''.format(dir_name), aps.filename, aps.lineno, line, dir_name)
                except AssemblerError as e:
                    if not e.line: e.line = line
                    if not e.at_token: e.at_token = line
                    raise e
        return line


'''
Preprocessor task that substitutes values in the assembler definition table.
These definition values come from define directives.
'''
class SubstituteTokensTask(PreprocessorTask):

    replacements = None

    def replace_token(match):
        return SubstituteTokensTask.replacements[match.group(0)]

    def process_line(self, line: str, aps: AssemblerPassState) -> str:
        SubstituteTokensTask.replacements = aps.get_define_table()
        line = re.sub('|'.join(r'\b%s\b' % re.escape(s) for s in SubstituteTokensTask.replacements), SubstituteTokensTask.replace_token, line) 
        return line