import sys
import operator as op

sys.tracebacklimit = None

class Symbol(str):
    pass

class BoolException(BaseException):
    pass

class NumException(BaseException):
    pass

class RangeException(BaseException):
    pass

class Env(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.outer = outer
        if isinstance(parms, Symbol):
            self.update({parms: list(args)})
        else:
            if len(args) != len(parms):
                raise TypeError('expected %s, given %s, '
                                % (to_string(parms), to_string(args)))
            self.update(list(zip(parms, args)))
    
    def find(self, var):
        if var in self:
            return self
        elif self.outer is None:
            raise LookupError(var)
        else:
            return self.outer.find(var)

def raise_(Error):
    try:
        if isinstance(Error,bool):
            raise BoolException
        else:
            raise NumException
    except BoolException:
        print("Type Error: Expect ‘number’ but got ‘boolean’.")
        return "error"
    except NumException:
        print("Type Error: Expect ‘boolean’ but got ‘number’.")
        return "error"

def Sym(s, symbol_table={}):
    if s not in symbol_table:
        symbol_table[s] = Symbol(s)
    return symbol_table[s]

def to_string(x):
    if x is True:
        return "#t"
    elif x is False:
        return "#f"
    elif isinstance(x, Symbol):
        return x
    elif isinstance(x, list):
        return '(' + ' '.join(map(to_string, x)) + ')'
    else:
        return str(x)

def standard_globals(self):
    self.update({
     '+': op.add, '-': op.sub, '*': op.mul, '/': op.floordiv, 'not': op.not_,
     '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,'mod':op.mod,
     'and':op.and_, 'or': op.or_,
     'print-num': lambda x: print(to_string(x)) if not isinstance(x,bool) else raise_(x),
     'print-bool': lambda x: print(to_string(x)) if isinstance(x, bool) else raise_(x)})
    return self