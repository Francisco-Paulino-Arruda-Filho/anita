from anita.constants.constants import constants
from anita.rules.IRule import IRule


class ClosedRule(IRule):
    def __init__(self, token_line, token_formula, token_reference1, token_reference2, show_token_symbol=True):
        self.token_line = token_line
        self.token_formula = token_formula
        self.token_reference1 = token_reference1
        self.token_reference2 = token_reference2
        self.line = token_line.value
        self.formula = token_formula[1]
        self.reference1 = token_reference1.value
        self.reference2 = token_reference2.value
        self.show_token_symbol = show_token_symbol

    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line occurs in the branch of the rule line 
      if before:
        parser.check_line_branch_reference_error(deduction_result,self, reference1=True, reference2=True)      

      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1)
      true_value1 = parser.symbol_table.lookup_true_value_by_line(self.line, self.reference1)
      formula2 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference2)
      true_value2 = parser.symbol_table.lookup_true_value_by_line(self.line, self.reference2)

      if(formula1 is None or formula2 is None or self.formula is None):
        return

      # If the formula (reference 1) is not a contradiction
      if(self.formula.toString()!='@'):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_RESULT, self.token_formula, self))
      else:
          # if both formulas are the same and one contradicts the other.
          if(formula2 != formula1 or true_value1==true_value2):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_NEGATION, self.token_reference1, self))

    def toLatex(self, symbol_table):
      return '\\times'
    
    def toString(self):
      if self.show_token_symbol:
        return '{}. {} fechado {},{}'.format(self.line, self.formula.toString(), self.reference1, self.reference2)
      else:
        return '{}. {} {},{}'.format(self.line, self.formula.toString(), self.reference1, self.reference2)