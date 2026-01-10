from  anita.rules.BasicRule import BasicRule
from anita.constants.constants import constants
from anita.formula.quantifier_formula.QuantifierFormula import QuantifierFormula


class ForAllTrueRule(BasicRule):
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

      # If the formula is not a existential formula
      if(not isinstance(formula1, QuantifierFormula) or (isinstance(formula1, QuantifierFormula) and not formula1.is_universal()) or (true_value!=self.true_value)):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_UNIVERSAL_FORMULA, self.token_reference1, self))

      # If the conclusion is a valid substitution of the universal formula (referecence 1)
      if(isinstance(formula1, QuantifierFormula) and not formula1.valid_substitution(self.formula)):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_SUBSTITUTION_UNIVERSAL, self.token_formula, self))