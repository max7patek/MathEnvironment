"""

Some "home-made" Exeptions for internal MathEnvironment exceptions.

All MyExceptions should be caught in the Environment

"""

class MyException(Exception):
    pass


class ExpressionParseException(MyException):
    pass


class NotDifferentiable(MyException):
    pass


class Undefined(MyException):
    pass