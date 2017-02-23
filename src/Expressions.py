from Evaluatables import Evaluatable, Decimal, Variable
from Exceptions import ExpressionParseException, NotDifferentiable
from OperatorABCs import *




""" -------- Functions for Parsing Strings into Evaluatables -------- """

def _strip(listlist):
    n = []
    for i in listlist:
        n.append(i[0])
    return n

def tokenize(infix_string, library, var_list):
    string = infix_string # TODO check if this is legit
    out = []
    seps = ['(',')','[',']','{','}',',','_','-', ' '] + library.infix_ops

    n = 0
    while n < len(string):
        for s in seps:
            if string[n:n+len(s)] == s:
                if n > 0:
                    out.append(string[:n])
                out.append(string[n:n+len(s)])
                string = string[n+len(s):]
                n = -1

        n += 1
    out.append(string)
    #for i in out
    #print(out)

    out = _identify(out, library, var_list)

    def absorb(index, o):
        o[index + 1][0] = o[index][0] + o[index + 1][0]
        del o[index]
        return o

    if out.__len__() > 1 and out[0][0] == '-' and isinstance(out[1][1], Decimal):
        out = absorb(0, out)

    i = 1
    while i < out.__len__() - 1:
        # print(strip(out))
        if out[i][0] == '-' and isinstance(out[i + 1][1], Decimal) and \
                (isinstance(out[i - 1][1], Operator) or out[i - 1][0] in '(,'):
            out = absorb(i, out)
        i += 1

    out = _identify(_strip(out), library, var_list)

    #print(_strip(out))
    return out


def _identify(tok_list, library, var_list=None):
    def tok_id(tok, library, var_list=None):
        if tok in '(){}[],_ ':
            return [tok, tok]
        if tok in library.constants.keys():
            return [tok, library.constants[tok]]
        if tok in library.operators.keys():
            return [tok, library.operators[tok]]
        if tok[tok.__len__() - 1] in '1234567890.':
            return [tok, Decimal(float(tok))]

        if var_list is not None:
            for var in var_list:
                if tok == var:
                    return [tok, Variable(var)]
        #else:
        return [tok, Variable(tok)]
        #raise SyntaxError("Unrecognized Token")

    out = []
    for token in tok_list:
        out.append(tok_id(token, library, var_list))
    return out

def partial_merge(toks):
    #out = []
    i = 0
    while i < len(toks):
        if toks[i][0] == '_':
            toks[i-1].append(toks[i+1][0])
            del toks[i]
            del toks[i]
        else:
            i += 1
    return toks


def shunting_yard(toks):
    """
    This was implemented almost directly from the Wikipedia page

    The Shunting Yard algorithm converts lists of tokens from
    infix notation to postfix notation, which is generally nice
    for computers. Here, this is desired because by converting to
    postfix, the most precedent operators shift all the way to the
    right, making recursive abstract syntax tree generation easier.

    The current implementation of the algorithm is too lenient and
    doesn't complain (throw exceptions) enough. For example, it allows
    the String "+" to be parsed and converted into 0+0. It allows
    "sin()" to be parsed as an Expression with no operands, which
    throws a tuple out of range exception in some cases.
    """
    def num(tok):
        return isinstance(tok[1], Evaluatable)
    def fun(tok):
        return isinstance(tok[1], Operator) and tok[1].fix() == -1
    def op(tok):
        return isinstance(tok[1], Operator) and tok[1].fix() == 0
    def comma(tok): return tok[1] == ','
    def r_paren(tok): return tok[1] == ')'
    def l_paren(tok): return tok[1] == '('

    def top(stack):
        return stack[stack.__len__()-1]


    out = []
    stack = []
    i = 0

    while i in range(toks.__len__()):
        t = toks[i]
        if num(t):
            out.append(t)
        elif fun(t):
            stack.append(t)
        elif comma(t):
            while len(stack) > 0 and not l_paren(top(stack)):
                out.append(stack.pop())
            if len(stack) == 0:
                raise ExpressionParseException("either the separator was misplaced or parentheses were mismatched")
        elif op(t):
            while stack.__len__() > 0 and op(top(stack)) and (
                    (t[1].associativity() <= 0 and t[1].precedence() <= top(stack)[1].precedence())
                    or  (t[1].associativity() > 0 and t[1].precedence() < top(stack)[1].precedence()) ):
                out.append(stack.pop())
            stack.append(t)
        elif l_paren(t):
            stack.append(t)
        elif r_paren(t):
            while not l_paren(top(stack)):
                out.append(stack.pop())
            stack.pop()
            if stack.__len__() > 0 and fun(top(stack)):
                out.append(stack.pop())
        i += 1
    while stack.__len__() > 0:
        out.append(stack.pop()) if op(stack[-1]) or fun(stack[-1]) else stack.pop()

    return out



def parse(string, library, var_list = None):
    tok = tokenize(string, library, var_list)
    tok = partial_merge(tok)
    rpn = shunting_yard(tok)
    exp = _recurse_on_prefix_tokens(rpn)
    return exp.simplify() if isinstance(exp, Expression) else exp #NOTE: this calls simplify, which is still 'so-so'

def _recurse_on_prefix_tokens(rpn):
    if not isinstance(rpn[-1][1], Operator):
        return rpn[0][1]
    op = rpn.pop()
    operands = []

    #print(op)
    def n_operands(tok):  # when grouping rpn into operands, need to know how many operands an op requires
        if tok[1].args_req() is None:
            return 2  #
        else:
            return tok[1].args_req()


    n = 0  # represents how many tokens need to be passed before getting back to primary operands
    operand = []  # holds the tokens that are being passed in order to append them to the operands list
    for i in range(rpn.__len__() - 1, -1, -1):
        # print(rpn[i])
        if isinstance(rpn[i][1], Operator):
            n += n_operands(rpn[i])
        if n >= 0:
            operand.insert(0, rpn[i])
        if n == 0:
            operands.insert(0, operand)
            operand = []
        if n > 0:
            n -= 1
    #print(list(map(_strip, operands)))

    for i in range(operands.__len__()):
        # print('%',self.operands[i])
        if operands[i].__len__() > 1:
            operands[i] = _recurse_on_prefix_tokens(operands[i])  # THIS IS RECURSION
        else:
            operands[i] = operands[i][0][1]

    exp = Expression(op[1], *operands)
    if len(op) > 2:
        for i in op[2:]:
            #print('applying _' + i)
            exp.op = exp.op.partial( i)
    #    subs = {}
    #    for i in range(exp.op.vars.__len__()):
    #        subs[exp.op.vars[i]] = exp.operands[i]
    #    if exp.op.fun.plugs_needed() > 0:
    #        exp.op.fun = exp.op.fun.substitute(subs)
    #print(exp)
    return exp









""" -------- Definition of the Expression -------- """
""" (where the world of operators and evaluatables meet) """

class Expression(Evaluatable):
    """
    The Expression object is one of the most import classes. It is
    an Evaluatable which combines other Evaluatables through Operators,
    thus merging the two sides of the MathEnvironment: Evaluatables and
    Operators.

    All Expressions have a list of operands, the Evaluatables to be
    combined, and single operator which describes a filter that the
    operands must pass through for the Expression to be evaluated.

    Expressions are meant to be immutable. While currently the operands
    list is a tuple and thus immutable, the operator is currently mutable.
    This is a change that should happen in the future.
    """

    def __init__(self, operator, *operands):
        self.op = operator
        self.operands = operands

    def eval(self, plugs):
        if self.op is not None:
            #print(self.op)
            return self.op.operate(self.operands, plugs) # THIS RECURSIVELY CALLS EVAL ON THE OPERANDS
        return self.operands[0].eval(plugs)

    def derivative(self, var):
        #if self.op is None:
        #    return self.operands[0].derivative(var)
        if isinstance(self.op, Differentiable):
            return self.op.derivative(self.operands, var).simplify()
        raise NotDifferentiable()

    def substitute(self, subs: dict):
        no = []
        for i in self.operands:
            if isinstance(i, Variable) and str(i) in subs.keys():
                no.append(subs[str(i)])
            elif isinstance(i, Expression):
                no.append(i.substitute(subs))
            else:
                no.append(i)
        return Expression(self.op, *no)

    def simplify(self): # TODO: improve and test
        return self.flatten().semi_eval().trim()

    def flatten(self):
        oo = []
        for i in self.operands:
            if isinstance(i, Expression):
                oo.append(i.flatten())
            else:
                oo.append(i)

        for o in oo:
            if isinstance(o, Expression) and isinstance(o.op, self.op.__class__) \
                    and self.op.fix() == 0 and self.op.args_req() is None:
                for r in o.operands:
                    oo.append(r)
                oo.remove(o)
        #print(oo)
        return Expression(self.op, *oo)

    def trim(self):
        oo = []
        for i in self.operands:
            if isinstance(i, Expression):
                oo.append(i.trim())
            else:
                oo.append(i)
        if isinstance(self.op, Trimmable):
            return self.op.trim(oo)
        return Expression(self.op, *oo)


    def semi_eval(self):
        '''should probably call flatten first'''

        #1 if totally associative: group elements into those needing plugs and those not
        annotated = []
        for i in self.operands:
            if i.plugs_needed() > 0:
                annotated.append((i, True))
            else:
                annotated.append((i, False))

        # 2 recurse on operands that need plugs
        for i in range(len(annotated)):
            if annotated[i][1] and isinstance(annotated[i][0], Expression):
                annotated[i] = (annotated[i][0].semi_eval(), True) # RECURSION
            if not annotated[i][1]:
                annotated[i] = (Decimal(annotated[i][0].eval({})), False)

        #3 return Expression(self.op, *(recursed_plug-needing_operands.append(Decimal((operands_w/o_plugs).eval({})))
        if self.op.args_req() is None:
            combine = []
            for i in annotated:
                if not i[1]:
                    combine.append(i[0])
            exp = Expression(self.op, *combine)
            oo = []
            from Operators import Multiply
            mult = isinstance(self.op, Multiply)
            if mult:
                oo.append(Decimal(exp.eval({})))
            for i in annotated:
                if i[1]:
                    oo.append(i[0])
            if not mult:
                oo.append(Decimal(exp.eval({})))
            return Expression(self.op, *oo)
        else:
            return Expression(self.op, *_strip(annotated))






    def __str__(self):
        def needs_parens(o, this):
            """
            Possibly one of the ugliest if statements ever written; however,
            the boolean algebra really is required to to deturmine whether a
            section of an expression requires parenthesis.
            """
            if isinstance(o, Expression) and this.op.fix() == 0 \
                        and (o.op.precedence() < this.op.precedence()
                             or (o.op.precedence() == this.op.precedence()
                                 and this.op.args_req() == 2 and o is this.operands[1] if this.op.associativity() <=0
                                                                            else this.operands[0])):
                return '(' + str(o) + ')'
            return str(o)

        if self.op is None:
            return str(self.operands[0])
        elif self.op.fix() == 0:
            s = needs_parens(self.operands[0], self)
            for i in self.operands[1:]:
                s += str(self.op) + needs_parens(i, self)
            return s
        elif self.op.fix() == -1:
            s = str(self.op) + '(' + needs_parens(self.operands[0], self)
            for i in self.operands[1:]:
                s += ', ' + needs_parens(i, self)
            s += ')'
            return s

    def assert_vars(self, vars):
        """
        This method allows Expression variable lists to be fixed.
        This is usefull (and necessary) for when an Expression
        represents a function where there are certain parameters
        which should be considered part of the Expression even if
        they don't exist in the Expression tree.

        Overriding the list_vars method by calling this function
        is dangerous because it is not undoable at all. Additionally,
        it defies the desire for Expressions to be immutable, so
        this method will likely disappear in the future.
        """
        self.var_list = vars

    def list_vars(self):
        if hasattr(self, 'var_list'):
            return self.var_list
        l = []
        for i in self.operands:
            if isinstance(i, Variable):
                l.append(i)
            if isinstance(i, Expression):
                l.extend(i.list_vars()) # RECURSION
        u = []
        for i in l:
            if str(i) not in list(map(str, u)):
            #if i not in u:
                u.append(str(i))
        return u

    def plugs_needed(self):
        return self.list_vars().__len__()