from abc import ABCMeta, abstractmethod


class Operator(object, metaclass=ABCMeta):
    """
    An Abstract Base Class for Operators

    All Operators must be able to operate on operands, returning
    some sort of value. They also cary some metadata which is mostly
    used for parsing. """

    @abstractmethod
    def operate(self, operands: list, plugs: dict) -> object:
        """
        Executes the main purpose of the Operator, the operation.

        Arguments:
            operands: is a list of what the operator is to operate on
            plugs: is a dictionary listing decimals to fill any variables with

        Returns:
            the result of the operation. Often a number, but possibly some other data structure

        Note:
            The operate method should call '.eval(plugs)' on each operands at some point

        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        Built-in method for converting to str must be re-implemented
        because it is needed to parse and reconstruct expresssions.
        """
        pass

    @abstractmethod
    def precedence(self) -> float:
        """
        All Operators must be able to give there precedence (in the order
        of operations).

                """
        pass

    @abstractmethod
    def fix(self) -> int:
        """
        Method for providing the _fix of the operator:
            -1 = prefix
            0  = infix
            1  = postfix (not used)

                """
        pass

    @abstractmethod
    def args_req(self) -> int: #TODO make return a Predicate <int>
        """
        All operators must be able to state how many arguments they
        are defined for. Failure to comply with an Operator's stated
        args_req may result in IndexOutOfBoundsException or unexpected
        behaviour.

        Operations may return None for args_req to indicate that they are defined
        for any number of arguments.
                """
        pass

    @abstractmethod
    def associativity(self) -> int:
        """
        All Operators must be able to state their associativity:
            -1 = left-associative
            0  = totally associative (used for simplification of some expressions)
            1  = right-associative (like the Pow operator)
                """
        pass


class Invertable(metaclass=ABCMeta):
    @abstractmethod
    def inverse(self):
        raise NotImplementedError("Please Implement this method")


class Differentiable(metaclass = ABCMeta):
    @abstractmethod
    def derivative(self, operands, var):
        pass

class Trimmable(metaclass=ABCMeta):
    @abstractmethod
    def trim(self, operands):
        pass

