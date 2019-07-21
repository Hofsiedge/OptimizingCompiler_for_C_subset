from operation_utils import Definition, Usage

class Register:

    def __init__(self, real=False, name=''):
        self.name   = name
        self.real   = real

    @property
    def value(self):
        return self

    def __repr__(self):
        return self.name if self.real else f'dword [{self.name}]'


class EAX(Register):

    def __init__(self):
        super().__init__(True, 'eax')

    def load(self, symbolic_register):
        return MOV(self, symbolic_register)
    

class Expression:

    def __init__(self):
        self.value      = None
        self.register   = Register()
        self.evaluated  = False
        self.in_stack   = False
    
    @property
    def code(self):
        return ''

    def __repr__(self):
        return repr(self.value)


class Integer(Expression):

    def __init__(self, value):
        super().__init__()
        self._value = value
        self.value = self

    def __add__(self, other):
        return self._value + other._value

    def __sub__(self, other):
        return self._value - other._value

    def __mul__(self, other):
        return self._value * other._value

    def __div__(self, other):
        return self._value // other._value
    
    def __repr__(self):
        return f'{self._value}'


class Variable(Expression):

    def __init__(self, name):
        super().__init__()
        self.name   = name
        self.value  = self.register
    
    @property
    def real(self):
        return self.register.real


class BinaryOperation(Expression):

    def __init__(self, left, right, eax=None):
        super().__init__()
        self.eax    = eax
        self.value  = None
        self.left   = left
        self.right  = right
        self.du     = []


# is used in EAX and DIV
class MOV(BinaryOperation):

    def __init__(self, left, right):
        super().__init__(left, right)
        self.value  = left.value

    @property
    def code(self):
        return f'\tMOV {self.left},\t{self.right}\n' if self.left != self.right else ''


class Assign(BinaryOperation):

    def __init__(self, left, right, eax):
        super().__init__(left, right, eax)
        self.value  = left

        if type(left) != Variable:
            raise Exception(f"Assigning to {type(left)}!")
        
        if type(right) == Variable:
            self.du.append(Usage(right, self))
        elif type(right) == Assign:
            self.du.append(Usage(right.value, self))
        
        self.du.append(Definition(left, self))

    @property
    def code(self):

        code = ''
        
        if self.left.real \
             or type(self.right) == Integer \
             or self.right.value.real:                          # r, *  |  m, r/int
            code = f'\tMOV {self.left},\t{self.right}\n\n'

        else:                                                   # both are symbolic (m, m)
            mov    =  self.eax.load(self.right.value)
            code   += mov.code
            code   += f'\tMOV {self.left},\t{self.eax}\n\n'

        return code


# r, r/m/int
# m, r/int
class AdditiveOperation(BinaryOperation):

    def __init__(self, operation, left, right, eax):
        super().__init__(left, right, eax)
        self.operation = operation

        if type(left) == Integer and type(right) == Integer:
            self.value = left + right if operation == 'ADD' else left - right
        else:
            self.value = None if self.in_stack else eax
        
        if type(left)   == Variable:
            self.du.append(Usage(left, self))
        if type(right)  == Variable:
            self.du.append(Usage(right, self))

    @property
    def code(self):

        if type(self.left) == Integer and type(self.right) == Integer:
            return ''

        right = self.right.value
        code = ''
        if right == self.eax:
            code = f'\tMOV dword [__temp], {right}\n'
            right = 'dword [__temp]'
        
        if self.left.in_stack:
            code += '\tPOP eax\n'
        elif self.left != self.eax:
            code += self.eax.load(self.left.value).code

        code += f'\t{self.operation} eax,\t{right}\n'
        code += '\tPUSH eax\n' if self.in_stack else '\n'

        return code


class ADD(AdditiveOperation):

    def __init__(self, left, right, eax):
        super().__init__('ADD', left, right, eax)


class SUB(AdditiveOperation):

    def __init__(self, left, right, eax):
        super().__init__('SUB', left, right, eax)

# r/m
class MultiplicativeOperation(BinaryOperation):

    def __init__(self, operation, left, right, eax):
        super().__init__(left, right, eax)
        self.operation = operation

        if type(left) == Integer and type(right) == Integer:
            self.value = left * right if operation == 'IMUL' else left // right
        else:
            self.value = None if self.in_stack else eax
        
        if type(left)   == Variable:
            self.du.append(Usage(left, self))
        if type(right)  == Variable:
            self.du.append(Usage(right, self))

    @property
    def code(self):

        if type(self.left) == Integer and type(self.right) == Integer:
            return ''
        
        code = ''

        right = self.right.value
        if right == self.eax or type(right) == Integer:
            code = f'\tMOV dword [__temp], {right}\n'
            right = '\tdword [__temp]\n'
        
        if self.left.in_stack:
            code += '\tPOP eax\n'
        elif self.left.value != self.eax:
            code += self.eax.load(self.left.value).code

        if self.operation == 'IDIV':
            code += '\tPUSH edx\n'
            code += '\tXOR edx, edx\n'

        code += f'\t{self.operation} {right}\n'
        
        if self.operation == 'DIV':
            code += '\tPOP edx\n'
        code += '\tPUSH eax\n' if self.in_stack else '\n'

        return code


class MUL(MultiplicativeOperation):
    def __init__(self, left, right, eax):
        super().__init__('IMUL', left, right, eax)


class DIV(MultiplicativeOperation):
    def __init__(self, left, right, eax):
        super().__init__('IDIV', left, right, eax)


class RET(Expression):

    def __init__(self, expr, eax):
        self.expr   = expr
        self.eax    = eax
        self.value  = eax
        self.du     = []
        self.evaluated = False
        if type(expr) == Variable:
            self.du.append(Usage(expr, self))

    @property
    def code(self):
        code = '\tPOP eax\n' if self.expr.in_stack else '' 
        if self.expr.value != self.eax:            
            mov   = self.eax.load(self.expr.value)
            code   += mov.code
        code       += f'\tRET\n'

        return code


class Condition(BinaryOperation):

    def __init__(self, left, right, eax):
        super().__init__(left, right, eax)
        self.value = None
        
        if type(left)   == Variable:
            self.du.append(Usage(left, self))
        if type(right)  == Variable:
            self.du.append(Usage(right, self))

    @property
    def code(self):

        code    = ''
        right   = self.right.value
        left    = self.left.value
        
        if self.left.in_stack:
            if right == self.eax:
                code += f'\tMOV dword [__temp], {right}\n'
                right = 'dword [__temp]'
            code += '\tPOP eax\n'
            left = self.eax
            code += f'\tCMP eax,\t{right}\n\n'
            return code
        
        if left != self.eax:
            if right == self.eax:
                code += f'\tMOV dword [__temp], {right}\n'
                right = 'dword [__temp]'
            mov         = self.eax.load(left)
            code   += mov.code
        
        code += f'\tCMP eax,\t{right}\n\n'
        return code


class START_WHILE(Expression):

    def __init__(self, loop_id):
        self.loop_id    = loop_id
        self.du         = []
        self.value      = None
    
    @property
    def code(self):
        return f'\twhile_{self.loop_id}:\n\n'


class MID_WHILE(Expression):

    def __init__(self, loop_id, jmp):
        self.jmp        = jmp
        self.loop_id    = loop_id
        self.du         = []
        self.value      = None
        
    @property
    def code(self):
        return f'\t{self.jmp} end_while_{self.loop_id}\n\n'

class END_WHILE(Expression):

    def __init__(self, loop_id):
        self.loop_id    = loop_id
        self.du         = []
        self.value      = None
    
    @property
    def code(self):
        return f'\tjmp while_{self.loop_id}\n\tend_while_{self.loop_id}:\n\n'
