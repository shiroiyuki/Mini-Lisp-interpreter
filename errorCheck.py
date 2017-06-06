import re
from Env import *

#reservedWords = ['Plus','Minus','Multiply','Divide','Modulus','Greater','Smaller','Equal','And','Or','Not']
numOp = ['+','-','*','/','mod','>','<','=']
logicOp = ['and','or','not']
otherOp = ['if','define','fun']
Op = numOp + logicOp
reservedWords = Op + otherOp 
checkWords = logicOp + otherOp + ['mod']
#reservedWords = reservedWords + numOp + logicOp
eof_object = Symbol('#<eof-object>')
error_object = Symbol('#<error-object>')
class Input_Error(BaseException):
    def __init__(self, m = "TypeError"):
        self.message = str(m)
    def __str__(self):
        return self.message

def Error(msg):
    print(msg)
    return None 

def rangeCheck(exps):
    check = 3
    if isinstance(exps,list):
        for exp in exps:
            if isinstance(exp,list):
                check = rangeCheck(exp)
            elif not isinstance(exp,bool):
                if isinstance(exp, int):
                    if exp > 2147483647 or exp < -2147483647:
                        return 0
                elif isinstance(exp ,Symbol):
                    a = re.match('^[a-z]([a-z]|[0-9]|-)*$',exp)
                    if exp is error_object:
                        return 2
                    if a is None and not exp in reservedWords:
                        return 1
    else:
        if not isinstance(exps,bool):
            if isinstance(exps, int):
                if exps > 2147483647 or exps < -2147483647:
                    return 0
            elif isinstance(exps ,Symbol):
                a = re.match('^[a-z]([a-z]|[0-9]|-)*$',exps)
                if exps is error_object:
                    return 2
                if a is None and not exps in Op:
                    return 1
    return check

def boolCheck(exps):
    try:
        for exp in exps:
            if isinstance(exp,bool):
                raise BoolException
        return True
    except BoolException:
        return False

def numCheck(exps):
    try:
        for exp in exps:
            if not isinstance(exp,bool):
                if isinstance(exp, int):
                    raise NumException
        return True
    except NumException:
        return False