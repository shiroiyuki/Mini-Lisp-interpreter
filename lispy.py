import io
import collections
from errorCheck import *

_if, _define, _fun, _begin, _definemacro, = list(map(Sym,
"if   define   fun   begin   define-macro".split()))
class Procedure(object):
    def __init__(self, parms, exp, env):
        self.parms, self.exp, self.env = parms, exp, env
    def __call__(self, *args):
        return eval(self.exp, Env(self.parms, args, self.env))

class InPort(object):
    tokenizer = (r"""\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)""")
    def __init__(self, file):
        self.file, self.line = file, ''
    def next_token(self):
        while True:
            if self.line == '':
                self.line = self.file.readline()
            if self.line == '':
                return eof_object
            token, self.line = re.match(InPort.tokenizer, self.line).groups()
            if token != '' and not token.startswith(';'):
                return token

def parse(inport):
    if isinstance(inport, str):
        inport = InPort(io.StringIO(inport))
    return expand(read(inport), toplevel=True)

def read(inport):
    def read_ahead(token):
        if '(' == token:
            L = []
            while True:
                token = inport.next_token()
                if token == ')':
                    return L
                else:
                    L.append(read_ahead(token))
        elif ')' == token:
            raise SyntaxError('syntax error.')
        elif token is eof_object:
            raise SyntaxError('syntax error.')
        else:
            return atom(token)
    token1 = inport.next_token()
    return eof_object if token1 is eof_object else read_ahead(token1)

def atom(token):
    if token == '#t':
        return True
    elif token == '#f':
        return False
    try:
        if len(token) > 1:
            if token[0] == '0':
                return error_object
            elif len(token)>2:
                if token[0] == '-' and token[1] == '0':
                    return error_object
        return int(token)
    except ValueError:
        try: return float(token)
        except ValueError: return Sym(token)

def load(filename):
    repl(InPort(open(filename)))

def repl(inport=InPort(sys.stdin)):
    while True:
        try:
            x = parse(inport)
            if x is eof_object:
                return
            elif rangeCheck(x) == 0:
                raise Exception("Out of range.")
            elif rangeCheck(x) == 1:
                raise Exception("ID Error.")
            elif rangeCheck(x) == 2:
                raise Input_Error("Expect ID.")
            elif rangeCheck(x) == 3:
                raise Input_Error("Input Error: cannot input float type")
            elif rangeCheck(x) == 4:
                raise Exception("syntax error.")
            val = eval(x)
        except Exception as e:
            #print('%s: %s' % (type(e).__name__, e))
            print(e)
        except Input_Error as e:
            print(e)

global_env = standard_globals(Env())

def eval(x, env = global_env):
    while True:
        if x is None:
            return None
        elif isinstance(x, Symbol):
            return env.find(x)[x]
        elif not isinstance(x, list):   
            return x
        elif x[0] is _begin:
            for exp in x[1:-1]:
                eval(exp, env)
            x = x[-1]
        elif x[0] is _if:        
            (_, test, conseq, alt) = x
            x = (conseq if eval(test, env) else alt)
        elif x[0] is _define: 
            try:
                if x[1] in checkWords:
                    return Error("you cannot use {} as ID".format(x[1]))
                env.find(x[1])
                return Error("ReDefine!")
            except:
                (_, var, exp) = x
                if isinstance(exp,list):
                    if(exp[0] is _fun):
                        (_, vars, exps) = exp
                        if isinstance(vars,list):
                            for i in vars:
                                if  i in checkWords:
                                    return Error("you cannot use {} as ID".format(i))
                env[var] = eval(exp, env)               
                return None
        elif x[0] is _fun:    
            (_, vars, exp) = x
            #try:
                #for i in exp:
                    #if  i in checkWords:
                        #return Error("you cannot use {} as ID".format(i))
            return Procedure(vars, exp, env)
            #except:
                #return Procedure(vars, exp, env)
        else:
            exps = [eval(exp, env) for exp in x]
            proc = exps.pop(0)
            try:
                if isinstance(proc, Procedure):
                    x = proc.exp
                    env = Env(proc.parms, exps, proc.env)
                else:
                    tmp = len(exps)
                    if tmp > 2:
                        if x[0] == '*':
                            if boolCheck(exps):
                                ans = 1;
                            else:
                                return Error("Type Error: Expect ‘number’ but got ‘boolean’.");
                        elif x[0] == '+':
                            if boolCheck(exps):
                                ans = 0;
                            else:
                                return Error("Type Error: Expect ‘number’ but got ‘boolean’.");
                        elif x[0] == 'and':
                            if not numCheck(exps):
                                return Error("Type Error: Expect ‘boolean’ but got ‘number’.")
                            ans = True;
                        elif x[0] == 'or':
                            if not numCheck(exps):
                                return Error("Type Error: Expect ‘boolean’ but got ‘number’.")
                            ans = False;
                        elif x[0] == '=':
                            if not boolCheck(exps):
                                return Error("Type Error: Expect ‘number’ but got ‘boolean’.")
                            ans = exps[0]
                        for i in exps:
                            ans = proc(ans,i)
                    elif tmp == 2:
                        if x[0] in numOp:
                            if not boolCheck(exps):
                                return Error("Type Error: Expect ‘number’ but got ‘boolean’.")
                        elif x[0] in logicOp:
                            if not numCheck(exps):
                                return Error("Type Error: Expect ‘boolean’ but got ‘number’.")
                        ans = proc(*exps)
                    else:
                        if x[0] == 'not':
                            if not isinstance(exps[0],bool):
                                return Error("Type Error: Expect ‘boolean’ but got ‘number’.")
                        try:
                            ans = proc(*exps)
                            #if x[0] == 'print-num' or x[0] == 'print-bool' and not isinstance(ans,str):
                                #print(to_string(ans))
                        except:
                            return Error("syntax error.")
                    return ans
            except Exception as e:
                return Error("syntax error")

def require(x, predicate, msg = "wrong length"):
    if not predicate:
        raise SyntaxError(to_string(x) + ': ' + msg)

def expand(x, toplevel=False):
    #require(x, x != [])
    if not isinstance(x, list):
        return x
    elif x[0] is _if:
        if len(x) == 3:
            x = x + [None]
        require(x, len(x) == 4)
        return list(list(map(expand, x)))
    elif x[0] is _define:
        require(x, len(x) >= 3)
        _def, v, body = x[0], x[1], x[2:]
        if isinstance(v, list) and v: 
            f, args = v[0], v[1:]
            return expand([_def, f, [_fun, args] + body])
        else:
            require(x, len(x) == 3)
            require(x, isinstance(v, Symbol), "can define only a symbol")
            exp = expand(x[2])
            return [_define, v, exp]
    elif x[0] is _begin:
        if len(x) == 1:
            return None 
        else:
            return [expand(xi, toplevel) for xi in x]
    elif x[0] is _fun:
        require(x, len(x) >= 3)
        vars, body = x[1], x[2:]
        require(x, (isinstance(vars, list) and all(isinstance(v, Symbol) for v in vars))
                or isinstance(vars, Symbol), "illegal lambda argument list")
        exp = body[0] if len(body) == 1 else [_begin] + body
        return [_fun, vars, expand(exp)]
    elif isinstance(x[0], Symbol) and x[0] in macro_table:
        return expand(macro_table[x[0]](*x[1:]), toplevel)
    else: 
        return list(list(map(expand, x)))
macro_table = {}

if __name__ == '__main__':
    if len(sys.argv) == 1:
        repl()
    else:
        load(sys.argv[1])
