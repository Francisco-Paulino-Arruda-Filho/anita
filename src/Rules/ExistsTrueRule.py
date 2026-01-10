from Rules.BasicRule import BasicRule
from models.constants import constants
from models.quantifier_formula.ExistentialFormula import ExistentialFormula
from models.quantifier_formula.QuantifierFormula import QuantifierFormula


class ExistsTrueRule(BasicRule):
    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      # If the reference1 line occurs in the branch of the rule line 
      if before:
        parser.check_line_branch_reference_error(deduction_result,self, reference1=True)      

      formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1)
      true_value = parser.symbol_table.lookup_true_value_by_line(self.line, self.reference1)

      if(formula1 is None):
        return

      # If the formula is not an universal formula
      if(not isinstance(formula1, QuantifierFormula) or (isinstance(formula1, QuantifierFormula) and not formula1.is_existential()) or (true_value!=self.true_value)):
        parser.has_error = True
        deduction_result.add_error(parser.get_error(constants.INVALID_EXISTENCIAL_FORMULA, self.token_reference1, self))

      # If the conclusion is a valid substitution of the existencial formula (referecence 1)
      elif(isinstance(formula1, QuantifierFormula) and not formula1.valid_substitution(self.formula)):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_SUBSTITUTION_UNIVERSAL, self.token_formula, self))
      # If the variable is not a fresh variable 
      elif(isinstance(formula1, QuantifierFormula)):
        variables = formula1.get_values_x_substitution(formula1.variable, ExistentialFormula(formula1.variable, self.formula))
        if not parser.symbol_table.is_fresh_variable(self.line, list(variables)[0]):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.VARIABLE_IS_NOT_FRESH_VARIABLE, self.token_formula,self))