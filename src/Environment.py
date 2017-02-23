import math
from Evaluatables import Constant, Vector, Variable
from Exceptions import MyException
from Operators import *
from Expressions import parse


def _unique_vars(exps):
    u = []

    for i in exps: #TODO i can be any Evaluatable
        if isinstance(i, (Expression, Vector)):
            for v in i.list_vars():
                if v not in u:
                    u.append(v)
        elif isinstance(i, Variable):
            if str(i) not in u:
                u.append(str(i))

    return u

def my_parse(string, library, variables = None):
    s = string
    while True:
        try:
            if variables is None:
                out = parse(s, library)
            else:
                out = parse(s, library, variables)
            break
        except MyException as e:
            print(e.args)
            s = input('please try again   > ')
        except Exception as a:
            print("Aghhh! A Bug! Fix Me")
            print(e.with_traceback())
            s = input('please try again   > ')
    return out



class Environment(object):
    """
    The Environement ties the whole thing together.

    1) The Environment acts as a library for Expression parsing.
    It keeps a dictionary of functions, which is initialized to
    builtin functions like sin(), mod(), '+', '^', and a dictionary
    of constants which starts with constants like pi and e. The
    dictionaries use the Strings that represent functions or constants
    (ie '+', 'sin', 'pi') as keys, and instances of Operator or Constant
    respectively are are the values.
    The dictionaries can be appended to by using 'user_grow' or 'grow'
    or by simpling added directly to the dict objects.

    2) The Environment acts as a User Interface.
    When the 'run', 'user_prompt', and 'user_grow' methods are called,
    the environment prompts the user for some text input that will interact
    with the environment.
    One especially cool User Interface feature is the automatic rapid
    evaluation mode detailed below.

    """

    def __init__(self, operators = {}, constants = {}):
        #print("LIBRARY BEING CREATED")
        self.operators = operators
        ops = [Add(), Subtract(), Multiply(), Divide(), Pow(), Log(), Ln(), Sqrt(), Abs(), Sign(), Mod(),
               Sin(), Asin(), Cos(), Acos(), Tan(), Atan(), Sec(), Asec(), Csc(), Acsc(), Cot(), Acot()]
        for op in ops:
            self.operators[str(op)] = op

        self.infix_ops = []
        for v in self.operators.values():
            if v.fix() == 0:
                self.infix_ops.append(str(v))

        self.constants = constants
        cons = {'pi':math.pi, 'e':math.e}
        for c in list(cons.keys()):
            self.constants[c] = Constant(c, cons[c])

    def run(self, prompt = "  > ", keys = ()):
        inp = input(prompt)
        for k in keys:
            if inp == k:
                return k
        if '=' in inp:
            return self.grow(inp)
        else:
            exp = my_parse(inp, self)
            print(exp)

            if exp.plugs_needed() == 0:
                return exp.eval({})
            else:
                self.rapid_eval(exp)
                return ''


    def rapid_eval(self, exp):
        """
        This method allows the user to repeatedly evaluate an Expression
        with different variable plugs. This is really usefull for when you
        need to find the output of a function for several inputs. Instead
        of typing out the function for every input value, the user can simply
        input the values one after the other and input "stop" when finished.
        """
        g = self.generator(exp.list_vars())
        for i in g:
            print(exp.eval(i))
    def generator(self, vs):
        """
        The use of this generator function by rapid_eval allows for several
        layers of rapid evaluation simultaneaously. The generator yeilds a
        new value everytime the user has input a set of plugs that completely
        plugs all variables. If the user inputs plugs that include new variables
        the generator function is called recursively to start another layer.
        """
        while True:
            o = {}
            for v in vs:
                inp = input(v +'  = ')
                if inp == 'stop':
                    return
                o[v] = my_parse(inp, self)
            u = _unique_vars(o.values())
            out = {}
            if len(u) == 0:
                for v in vs:
                    out[v] = o[v].eval({})
                yield out
            else:
                g = self.generator(u) # THIS IS RECURSION
                for i in g:
                    for v in vs:
                        out[v] = o[v].eval(i)
                    yield out

    def user_prompt(self, prompt, keys = ()):
        inp = input(prompt)
        for k in keys:
            if inp == k:
                return k
        if '=' in inp:
            self.grow(inp)
            return self.user_prompt(prompt, keys) # THIS IS RECURSION
        return self.prompt(inp)

    def prompt(self, inp):
        exp = my_parse(inp, self)
        plugs = {}
        for i in exp.list_vars():
            plugs[i] = self.user_prompt(i + " = ") # THIS IS RECURSION
        return exp.eval(plugs)

    def user_grow(self, prompt, keys = ()):
        inp = input(prompt)
        for k in keys:
            if inp == k:
                return k
        return self.grow(inp)

    def grow(self, inp):
        inp = inp.replace(' ', '')
        all = inp.split('=')
        print(all)
        if '(' in all[0]:
            left = all[0].split('(')
            left[1] = left[1].replace(')', '')
            variables = left[1].split(',')
            fun = my_parse(all[1], self, variables)
            print(fun)

            self.operators[left[0]] = UserFunction(fun, variables, left[0])

        else:
            exp = my_parse(all[1], self)
            print(exp)
            plugs = {}
            if exp.plugs_needed() > 0:
                for i in exp.list_vars():
                    plugs[i] = self.user_prompt(i + " = ", ('stop',))
            num = exp.eval(plugs)
            self.constants[all[0]] = Constant(all[0], num)
        return "confirmed"