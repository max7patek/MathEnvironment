from Environment import Environment

def main():
    env = Environment()

    instructions(env)

    while True:
        print()
        out = env.run(keys = ('stop',))
        if out == 'stop':
            print('Goodbye')
            break
        print(out)

def instructions(env):

    print("\
Input an expression to evaluate it.\n\
    If the expression has no variables, the value is printed.\n\
    If the expression has variables, the environment goes into rapid evaluation mode.\n\
        When in rapid evaluation mode, input values for each variable in the original expression.\n\
            Multiple layers of rapid evaluation can be achieved by inputing variable expressions as plugs.\n\
            To exit a layer of rapid evaluation, simply input ‘stop’ at any time.\n\
Assign constants by stating:  name, '=', value.\n\
    for example, 'a = pi*4'\n\
Assign functions by stating:  name, '(', comma separated arguments, ')=', function.\n\
    for example, ‘func(x,y,z) = z^y+sin(z)’")



'''
from Expressions import *
from Operators import UserFunction, Multiply, Pow

f = UserFunction(Expression(Pow(), Variable('x') , Decimal(2)), ('x',), 'f')
exp = Expression(f, Variable('y'))

print(exp, exp.op.fun)
print(exp.substitute({'y':Variable('x')}) , exp.substitute({'y':Variable('x')}).op.fun)
print(exp.derivative('y'))

print(exp.eval({'y':3}))
print(exp.substitute({'y':Variable('x')}).eval({'x':3}))
print(exp.derivative('y').eval({'y':3}))
print(exp.derivative('y').substitute({'y':Variable('x')}).eval({'x':3}))

print()

exp.op = exp.op.partial('x')

print(exp, exp.eval({'y': 3}))

'''

if __name__ == '__main__':
    main()