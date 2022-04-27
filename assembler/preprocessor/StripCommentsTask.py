from typing import NamedTuple

from assembler.exceptions import AssemblerError

from .PreprocessorTask import *

class BlockCommentPrefix(NamedTuple):
    begin: str
    terminate: str

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