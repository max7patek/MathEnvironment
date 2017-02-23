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

Notes:
 - There are probably (definitely) bugs. Let me know if you find one!
 - The parser is configured to automatically identify any unknown token as a Variable. However, sometimes this is not desirable, so if you want to limit the Variables that can be identified, uncomment the two commented lines (currently 75 and 77, you will also have to indent line 76) in '_identify' in Expressions.py and pass a var_list to 'parse'
 - Partial derivatives are automatically built into the modules. Pure partial derivatives can be computed by assigning the expression to be differentiated to a function. Then, the user can compute and use the derivative by adding an ‘_’ and the variable to be differentiated with respect to after the function name.
 
    For example:
    
        ‘f(x,y,z) = e^x + y^2 + sin(z)’
        
        ‘f_y(456, 3, -634)’
        
            = 6
            
        ‘g(x) = f_y(0,x,0)’
