# MathEnvironment
The MathEnvironment is a collection of Python Modules supporting the parsing, manipulation, and evaluation of mathemetatical expressions.

The most important file is Expressions.py containing the 'Expression' class and the 'parse' method. Use the parse method to convert mathematical text into an Evaluatable object.

There are many different types of Evaluatable objects (and more can be added), including Decimal, Variable, Constant. However, the most usefull Evaluatable is Expression. Expressions combine other Evaluatables (including other Expressions) via an Operator defined in Operators.py or some other implementation of Operator, found in OperatorABCs.py. Expression thus merges the two sides of the MathEnvironment: Evaluatables and Operators.

The MathEnvironment also includes the Environment class, included in Environment.py.

    1) The Environment acts as a library for Expression parsing.
    It holds (i.) a dictionary of functions, which is initialized with
    builtin functions like 'sin', 'mod', '+', '^', and (ii.) a dictionary
    of constants which starts with constants like 'pi' and 'e'.
    The dictionaries can be appended to by using 'user_grow' or 'grow'
    or by simpling added directly to the dict objects.

    2) The Environment acts as a User Interface.
    When the 'run', 'user_prompt', and 'user_grow' methods are called,
    the environment prompts the user for some text input that will interact
    with the environment.
    One especially cool User Interface feature is the automatic rapid
    evaluation mode.

Altogether, the modules can be used to maintain a REPL with the user through a console. A possible implementation of this can be found in Main.py; however, the modules are designed to be flexible and usable in many different application contexts.
