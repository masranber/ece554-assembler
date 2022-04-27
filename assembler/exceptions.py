

class AssemblerException(Exception):
    
    def __init__(self, msg: str, tag: str = 'AssemblerException', filename: str = None, lineno: int = 0, line:str = None, at_token: str = None):
        super().__init__(msg)
        self.tag = tag
        self.filename = filename
        self.lineno = lineno
        self.line = line
        self.at_token = at_token

    def tostring(self):
        return '{}:{}: {}:\nWHAT: {}\nWHERE: at token \'{}\' in line \'{}\''.format(self.filename, self.lineno+1, self.tag, self.args[0], self.at_token, self.line)

class AssemblerWarning(AssemblerException):
    
    TAG: str = 'WARN'

    def __init__(self, msg: str, filename: str = None, lineno: int = 0, line:str = None, at_token: str = None):
        super().__init__(msg, AssemblerWarning.TAG, filename, lineno, line, at_token)


class AssemblerError(AssemblerException):
    
    TAG: str = 'ERROR'

    def __init__(self, msg: str, filename: str = None, lineno: int = 0, line:str = None, at_token: str = None):
        super().__init__(msg, AssemblerError.TAG, filename, lineno, line, at_token)