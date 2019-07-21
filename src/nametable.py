from tokens import Variable

class ParsingError(Exception):
    """Parsing error base class"""
    pass

class UnknownIDException(ParsingError):
    def __init__(self, ID, message=None):
        self.ID         = ID
        self.message    = message if message else f"Unknown Identifier: {ID}"


class DuplicateNamesException(ParsingError):
    def __init__(self, ID='', message=None):
        self.ID         = ID
        self.message    = message if message else f"Duplicate name: {ID}"


class NamedEntity:
    def __init__(self, identifier, mutable=True, value=None):
        self.mutable    = mutable
        self.value      = value
        self.name       = identifier
        self.var        = Variable(identifier) # edited here


class Int(NamedEntity):
    def __init__(self, identifier):
        super().__init__(identifier, True)


class Const(NamedEntity):
    def __init__(self, identifier, value):
        super().__init__(identifier, mutable=False, value=value)


class Scope:

    def __init__(self, outer_scope=None):
        self.entities       = {}
        self.inner_scope    = None
        self.outer_scope    = outer_scope

    def __getitem__(self, name):
        if name in self.entities:
            return self.entities[name]
        return self.outer_scope[name] if self.outer_scope else None

    def __setitem__(self, name, entity):
        if self[name]:
            raise DuplicateNamesException(name)
        self.entities[name] = entity

    def __repr__(self):
        
        consts_repr = 'Consts:'
        vars_repr   = 'Variables:'
        indent      = '\n'

        current_scope = self
        
        while current_scope:
            indent  += '\t'
            for entity_name in current_scope.entities:
                if current_scope[entity_name].mutable:
                    vars_repr += f'{indent} {entity_name}'
                else:
                    consts_repr += f'{indent} {entity_name} = {current_scope[entity_name].value}'
            current_scope = current_scope.inner_scope

        return consts_repr + '\n\n' + vars_repr

class SymbolTable:

    def __init__(self):
        self.outermost_scope    = Scope()
        self.innermost_scope    = self.outermost_scope
        self.name_set           = set()

    def push_scope(self):
        if self.innermost_scope.inner_scope:
            raise Exception('Pushing a scope over existing one')
        self.innermost_scope.inner_scope = Scope(self.innermost_scope)
        self.innermost_scope = self.innermost_scope.inner_scope

    def pop_scope(self):
        self.innermost_scope = self.innermost_scope.outer_scope
        self.innermost_scope.inner_scope = None
    
    def rewrite_var(self, name):
        scope   = self.innermost_scope

        while scope:
            if name in scope.entities:
                break
            scope = scope.outer_scope
            
        if scope == None:
            raise Exception(f'Trying to override unknown variable {name}')

        scope.entities.__delitem__(name)
        scope[name] = Int(name)

    def __getitem__(self, name):
        return self.innermost_scope[name]

    def __setitem__(self, name, entity):
        self.innermost_scope[name] = entity
        if entity.mutable:
            self.name_set.add(name)

    def __repr__(self):
        return self.outermost_scope.__repr__()
