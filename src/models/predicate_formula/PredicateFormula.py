class PredicateFormula():
    def __init__(self, name = '', variables = []):
        self.variables = variables
        self.name = name

    def __eq__(self, other): 
        if not isinstance(other, PredicateFormula):
            return NotImplemented
        return self.variables == other.variables and self.name == other.name
    
    def __ne__(self, other): 
        if not isinstance(other, PredicateFormula):
            return NotImplemented

        return self.variables != other.variables or self.name != other.name

    def toLatex(self, parentheses= False):
        if self.variables: 
            return self.name+'('+','.join(self.variables)+')'
        else:
            return self.name

    def toString(self, parentheses= False):
        if self.variables: 
            return self.name+'('+','.join(self.variables)+')'
        else:
            return self.name

    def get_values_x_substitution(self, var_x, formula):
      values = set()
      if isinstance(formula, PredicateFormula) and formula.name==self.name and len(formula.variables)==len(self.variables):
        for i in range(len(self.variables)):
          if self.variables[i]==var_x:
            values.add(formula.variables[i])
      return values

    def all_variables(self):
      return set(self.variables)

    def bound_variables(self):
      return set()

    def free_variables(self):
      return set(self.variables)

    def is_substitutable(self, x, y):
      return True

    def substitution(self, var_x, a):
      aux_variables = []
      for v in self.variables:
        if(v==var_x): 
          aux_variables.append(a)
        else: 
          aux_variables.append(v)
      return PredicateFormula(self.name, aux_variables)

    def is_first_order_formula(self):
      return True