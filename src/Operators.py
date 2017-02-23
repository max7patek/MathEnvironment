from math import log, sin, asin, cos, acos, tan, atan, sqrt, fabs

from Evaluatables import Decimal
from Exceptions import Undefined
from Expressions import Expression
from OperatorABCs import *

"""
All of these classes are completely or partially concrete
implementations of the Abstract Base Classes defined in the
OperatorABSs.py file. They are in seperate files for
(1) organization and (2) so other files that use Operators
can import the Abstract Base Classes file without importing
all the tedious details in this file.

"""


class ExpressionOperator(Operator, Differentiable):
    def __init__(self, exp, variables, name):
        self.fun = exp
        if isinstance(exp, Expression):
            self.fun.assert_vars(variables)
        self.vars = variables
        print(self.vars)
        self.name  = name

    def operate(self, operands, plugs) :
        my_operands = {}
        variables = self.vars
        for i in range(variables.__len__()):
            my_operands[variables[i]] = operands[i].eval(plugs)
        return self.fun.eval(my_operands)

    def derivative(self, operands, var):
        subs = {}
        for i in range(self.vars.__len__()):
            subs[self.vars[i]] = operands[i]
        for i in range(len(subs)):
            print(list(subs.keys())[i], list(subs.values())[i])
        ls = []
        for i in self.vars:
            ls.append(self.fun.derivative(i).substitute(subs))
        rs = []
        for i in operands:
            rs.append(i.derivative(var))
        terms = []
        for i in range(self.vars.__len__()):
            terms.append(Expression(Multiply(), ls[i], rs[i]))
        return Expression(Add(), *terms)

    def partial(self, var):
        exp = self.fun.derivative(var)
        print(exp)
        return UserFunction(exp, self.vars, self.name + '_' + var)

    def __str__(self):
        return self.name

    def args_req(self):
        return len(self.vars)



class BasicOp(Operator, Invertable, Differentiable, Trimmable):

    def fix(self):
        return 0
    def associativity(self):
        return -1



class Add(BasicOp):

    def operate(self, operands, plugs):
        sum = 0
        for i in operands:
            sum += i.eval(plugs)
        return sum

    def derivative(self, operands, var):
        #print("running " + self.__class__.__name__ + " derivative")
        new_operands = []
        for i in operands:
            new_operands.append(i.derivative(var))
        return  Expression(Add(), *new_operands)

    def trim(self, operands):
        #print("Add is trimming")
        o = []
        for i in operands:
            if i.plugs_needed() != 0 or i.eval({}) != 0:
                o.append(i)
        if len(o) > 1:
            return Expression(Add(), *o)
        if len(o) == 1:
            return o[0]
        return Decimal(0)


    def __str__(self):
        return '+'

    def inverse(self):
        return Subtract()

    def precedence(self):
        return 1

    def associativity(self):
        return 0

    def args_req(self):
        return None

class Subtract(BasicOp):

    def operate(self, operands, plugs):
        return operands[0].eval(plugs) - operands[1].eval(plugs)

    def derivative(self, operands, var):
        #print("running " + self.__class__.__name__ + " derivative")
        new_operands = []
        for i in operands:
            new_operands.append(i.derivative(var))
        return Expression(Subtract(), *new_operands)

    def trim(self, operands):
        print("subtraction trimmming")

        e1 = operands[0]
        e2 = operands[1]
        b1 = e1.plugs_needed() == 0 and e1.eval({}) == 0 # trimmability
        b2 = e2.plugs_needed() == 0 and e2.eval({}) == 0
        if not b1 and not b2:
            return Expression(Subtract(), e1, e2)
        if b1 and not b2:
            return Expression(Multiply(), Decimal(-1), e2)
        if not b1 and b2:
            return e1
        return Decimal(0)




    def __str__(self):
        return '-'

    def inverse(self):
        return Add()

    def precedence(self):
        return 1

    def args_req(self):
        return 2

class Multiply(BasicOp):

    def operate(self, operands, plugs):
        pro = 1
        for i in operands:
            pro *= i.eval(plugs)
        return pro

    def derivative(self, operands, var):
        #print("running "+self.__class__.__name__+ " derivative")
        terms = []
        for i in range(len(operands)):
            factors = [operands[i].derivative(var)]
            for j in range(1,len(operands)):
                factors.append(operands[(i+j)%len(operands)])
            terms.append(Expression(Multiply(), *factors))

        return Expression(Add(), *terms)

    def trim(self, operands):
        #print("Multiply is trimming")

        o = []
        for i in operands:
            pn = i.plugs_needed()
            if pn == 0 and i.eval({}) == 0:
                return Decimal(0)
            if pn != 0 or i.eval({}) != 1:
                o.append(i)
        if len(o) > 1:
            return Expression(Multiply(), *o)
        if len(o) == 1:
            return o[0]
        return Decimal(1)

    def __str__(self):
        return "*"

    def inverse(self):
        return Divide()

    def precedence(self):
        return 2

    def associativity(self):
        return 0

    def args_req(self):
        return None

class Divide(BasicOp):

    def operate(self, operands, plugs):
        return operands[0].eval(plugs) / operands[1].eval(plugs)

    def derivative(self, operands, var):
        #print("running " + self.__class__.__name__ + " derivative")
        tl = Expression(Multiply(), operands[0].derivative(var), operands[1])
        tr = Expression(Multiply(), operands[1].derivative(var), operands[0])
        top = Expression(Subtract(), tl, tr)
        bottom = Expression(Pow(), operands[1], Decimal(2))
        return Expression(Divide(), top, bottom)

    def trim(self, operands):
        e1 = operands[0]
        e2 = operands[1]
        b1 = e1.plugs_needed() == 0 and e1.eval({}) == 1 # trimmability
        b2 = e2.plugs_needed() == 0 and e2.eval({}) == 1
        if not b1 and not b2:
            return Expression(Divide(), e1, e2)
        if b1 and not b2:
            return Expression(Pow(), e2, Decimal(-1))
        if not b1 and b2:
            return e1
        return Decimal(1)

    def __str__(self):
        return "/"

    def inverse(self):
        return Add()

    def precedence(self):
        return 2
    def args_req(self):
        return 2

class Pow(Operator, Differentiable):

    def operate(self, operands, plugs):
        return operands[0].eval(plugs) ** operands[1].eval(plugs)

    def derivative(self, operands, var):
        e1 = operands[0].plugs_needed() > 0
        e2 = operands[1].plugs_needed() > 0
        if e1 and not e2:
            foo = Expression(Pow(), operands[0], Expression(Subtract(), operands[1], Decimal(1)))
            return Expression(Multiply(), operands[1], foo, operands[0].derivative(var))
        if not e1 and e2:
            return Expression(Multiply(),
                              Expression(Pow(), *operands),
                              Expression(Ln(), operands[0]),
                              operands[1].derivative(var))
        if not e1 and not e2:
            return Expression(None, Decimal(0))
        else:
            thm1 = Expression(Pow(), operands[0], Expression(Subtract(), operands[1], Decimal(1)))
            left =  Expression(Multiply(), operands[1], thm1, operands[0].derivative(var))
            right = Expression(Multiply(),
                              Expression(Pow(), *operands),
                              Expression(Ln(), operands[0]),
                              operands[1].derivative(var))
            return Expression(Add(), left, right)

    def __str__(self):
        return '^'

    def precedence(self):
        return 3

    def fix(self):
        return 0

    def args_req(self):
        return 2

    def associativity(self):
        return 1

class Sqrt(Operator, Differentiable):
    def operate(self, operands: list, plugs: dict):
        return sqrt(operands[0].eval(plugs))

    def derivative(self, operands, var):
        return Expression(Pow(), operands[0], Decimal(.5)).derivative(var)

    def __str__(self):
        return 'sqrt'

    def precedence(self):
        return 10

    def fix(self):
        return -1

    def args_req(self):
        return 1

    def associativity(self):
        return 1

class Mod(Operator):
    def operate(self, operands, plugs):
        return int(round(operands[0].eval(plugs))) % int(round(operands[1].eval(plugs)))

    def __str__(self):
        return '%'

    def precedence(self):
        return 1.5

    def fix(self):
        return 0

    def args_req(self):
        return 2

    def associativity(self):
        return -1

class Abs(Operator, Differentiable):
    def operate(self, operands, plugs):
        return fabs(operands[0].eval(plugs))

    def derivative(self, operands, var):
        return Expression(Sign(), operands[0].derivative(var))

    def __str__(self):
        return 'abs'

    def precedence(self):
        return 10

    def fix(self):
        return -1

    def args_req(self):
        return 1

    def associativity(self):
        return 1

class Sign(Operator, Differentiable):
    def operate(self, operands, plugs):
        val = operands[0].eval(plugs)
        if val > 0:
            return 1
        if val < 0:
            return -1
        raise Undefined()

    def derivative(self, operands, var):
        return Expression(ZeroNotZero(), operands[0].derivative(var))

    def __str__(self):
        return 'sign'

    def precedence(self):
        return 10

    def fix(self):
        return -1

    def args_req(self):
        return 1

    def associativity(self):
        return 1

class ZeroNotZero(Operator, Differentiable):
    def operate(self, operands: list, plugs: dict):
        if operands[0].eval(plugs) == 0:
            raise Undefined()
        return 0

    def derivative(self, operands, var):
        return Expression(ZeroNotZero(), operands[0].derivative(var))

    def __str__(self):
        return self.__class__.__name__

    def precedence(self):
        return 10

    def fix(self):
        return -1

    def args_req(self):
        return 1

    def associativity(self):
        return 1


class Log(Operator, Differentiable):
    def operate(self, operands, plugs):
        return log(operands[0].eval(plugs), operands[1].eval(plugs))

    def derivative(self, operands, var):
        top = Expression(Ln(), operands[0])
        bot = Expression(Ln(), operands[1])
        exp = Expression(Divide(), top, bot)
        return exp.derivative(var)

    def __str__(self):
        return "log"

    def precedence(self):
        return 10

    def fix(self):
        return -1

    def args_req(self):
        return 2

    def associativity(self):
        return 1

class Ln(Log):
    def operate(self, operands, plugs):
        return log(operands[0].eval(plugs))

    def derivative(self, operands, var):
        return Expression(Divide(), operands[0].derivative(var), operands[0])

    def __str__(self):
        return "ln"

    def args_req(self):
        return 1


class TrigFunc(Operator, Invertable, Differentiable):

    def __str__(self):
        return self.__class__.__name__.lower()

    def precedence(self):
        return 10

    def fix(self):
        return -1

    def args_req(self):
        return 1

    def associativity(self):
        return -1

    #@abstractmethod TODO: implement this such that tan return sin/cos etc.
    def simplify(self, operands):
        pass

class Sin(TrigFunc):

    def operate(self, operands, plugs):
        return sin(operands[0].eval(plugs))

    def derivative(self, operands, var):
        return Expression(Multiply(), Expression(Cos(), operands[0]), operands[0].derivative(var))

    def inverse(self):
        return Asin()

class Asin(TrigFunc):

    def operate(self, operands, plugs):
        return asin(operands[0].eval(plugs))

    def derivative(self, operands, var):
        rad = Expression(Subtract(), Decimal(1), Expression(Pow(), operands[0], Decimal(2)))
        return Expression(Divide(), operands[0].derivative(var), Expression(Sqrt(), rad))

    def inverse(self):
        return Sin()

class Cos(TrigFunc):

    def operate(self, operands, plugs):
        return cos(operands[0].eval(plugs))

    def derivative(self, operands, var):
        return Expression(Multiply(), Decimal(-1), Expression(Sin(), operands[0]), operands[0].derivative(var))

    def inverse(self):
        return Acos()

class Acos(TrigFunc):
    def operate(self, operands, plugs):
        return acos(operands[0].eval(plugs))

    def derivative(self, operands, var):
        rad = Expression(Subtract(), Decimal(1), Expression(Pow(), operands[0], Decimal(2)))
        top = Expression(Multiply(), Decimal(-1), operands[0].derivative(var))
        return Expression(Divide(), top, Expression(Sqrt(), rad))

    def inverse(self):
        return Sin()

class Tan(TrigFunc):

    def operate(self, operands, plugs):
        return tan(operands[0].eval(plugs))

    def derivative(self, operands, var):
        p = Expression(Pow(), Expression(Sec(), operands[0]), Decimal(2))
        return Expression(Multiply(), p, operands[0].derivative(var))

    def inverse(self):
        return Atan()

class Atan(TrigFunc):

    def operate(self, operands, plugs):
        return atan(operands[0].eval(plugs))

    def derivative(self, operands, var):
        rad = Expression(Add(), Decimal(1), Expression(Pow(), operands[0], Decimal(2)))
        return Expression(Divide(), operands[0].derivative(var), rad)

    def inverse(self):
        return Tan()




class Sec(TrigFunc):
    def operate(self, operands, plugs):
        return 1/cos(operands[0].eval(plugs))

    def derivative(self, operands, var):
        return Expression(Multiply(), Expression(Cos(), operands[0]), operands[0].derivative(var))

    def inverse(self):
        return Asec()
class Asec(TrigFunc):
    def operate(self, operands, plugs):
        return acos(1/operands[0].eval(plugs))

    def derivative(self, operands, var):
        rad = Expression(Subtract(), Expression(Pow(), operands[0], Decimal(2)), Decimal(1))
        bot = Expression(Multiply(), Expression(Abs(), operands[0]), Expression(Sqrt(), rad))
        return Expression(Divide(), operands[0].derivative(var), bot)

    def inverse(self):
        return Sec()
class Csc(TrigFunc):
    def operate(self, operands, plugs):
        return 1/sin(operands[0].eval(plugs))

    def derivative(self, operands, var):
        return Expression(Multiply(), Expression(Cos(), operands[0]), operands[0].derivative(var))

    def inverse(self):
        return Acsc()
class Acsc(TrigFunc):
    def operate(self, operands, plugs):
        return asin(1/operands[0].eval(plugs))

    def derivative(self, operands, var):
        rad = Expression(Subtract(), Expression(Pow(), operands[0], Decimal(2)), Decimal(1))
        bot = Expression(Multiply(), Expression(Abs(), operands[0]), Expression(Sqrt(), rad))
        return Expression(Divide(), Expression(Multiply(), Decimal(-1), operands[0].derivative(var)), bot)

    def inverse(self):
        return Csc()
class Cot(TrigFunc):
    def operate(self, operands, plugs):
        return 1/tan(operands[0].eval(plugs))

    def derivative(self, operands, var):
        return Expression(Multiply(), Expression(Cos(), operands[0]), operands[0].derivative(var))

    def inverse(self):
        return Acot()
class Acot(TrigFunc):
    def operate(self, operands, plugs):
        return atan(1/operands[0].eval(plugs))

    def derivative(self, operands, var):
        rad = Expression(Add(), Decimal(1), Expression(Pow(), operands[0], Decimal(2)))
        return Expression(Divide(), Expression(Multiply(), Decimal(-1), operands[0].derivative(var)), rad)

    def inverse(self):
        return Cot()


class UserFunction(ExpressionOperator):

    def precedence(self):
        return 10

    def fix(self):
        return -1

    def associativity(self):
        return 1
