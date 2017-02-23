from abc import ABCMeta, abstractmethod


class Evaluatable( metaclass=ABCMeta):
    """
    An Abstract Base Class for Evaluatable entities

    The most signifigant method of all Evaluatables is the 'eval'
    method. However, all Evaluatables must also state their
    derivative, the number of plugs needed, and their str representation.
    """

    @abstractmethod
    def eval(self, plugs):
        raise NotImplementedError("Please Implement this method")
    @abstractmethod
    def derivative(self, var):
        raise NotImplementedError("Please Implement this method")
    @abstractmethod
    def plugs_needed(self):
        raise NotImplementedError("Please Implement this method")
    @abstractmethod
    def __str__(self):
        raise NotImplementedError("Please Implement this method")


class Decimal(Evaluatable):

    def __init__(self, val):
        self.val = val
    def __str__(self):
        return str(self.val)

    def eval(self, plugs = None):
        return self.val

    def derivative(self, var):
        return Decimal(0)

    def plugs_needed(self):
        return 0


class Constant(Decimal):
    def __init__(self, name, val):
        super().__init__(val)
        self.name = name
    def __str__(self):
        return self.name


class Variable(Evaluatable):

    def __init__(self, name):
        self.name = name

    def eval(self, plugs):
        return plugs[self.name]

    def substitute(self, subs: dict):
        if self.name in subs.keys():
            return subs[self.name]

    def derivative(self, var):
        if str(var) == self.name:
            return Decimal(1)
        return Decimal(0)

    def plugs_needed(self):
        return 1

    def list_vars(self):
        return [self.name]

    def __str__(self):
        return self.name

class Vector(Evaluatable):
    """
    This is not actually used yet, but I've started writing it
    anyway. I hope to eventually incorperate Vectors and Matrices
    into the math environment when I have time.
    """

    def __init__(self, *components):
        self.components = components

    def eval(self, plugs):
        l = []
        for i in self.components:
            l.append(i.eval(plugs))
        return l

    #TODO implement substitute

    def derivative(self, var):
        l = []
        for i in self.components:
            l.append(i.derivative(var))
        return Vector(l)

    def list_vars(self):
        u = []
        from Expressions import Expression
        for i in self.components:

            if isinstance(i, Expression):
                for j in i.list_vars():
                    if j not in u:
                        u.append(j)
            elif isinstance(i, Variable):
                if str(i) not in u:
                    u.append(str(i))
        return u

    def plugs_needed(self):
        return len(self.list_vars())

    def __str__(self):
        s = '<'
        for i in self.components:
            s += str(i) + ', '
        s = s[:-2] + '>'
        return s

