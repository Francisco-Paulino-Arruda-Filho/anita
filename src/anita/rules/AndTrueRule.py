from anita.rules.BasicRule import BasicRule
from anita.constants.constants import constants
from anita.formula.binary_formula.BinaryFormula import BinaryFormula


class AndTrueRule(BasicRule):
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
      # If the formula (reference 1) is not a conjunction formula
      if(not isinstance(formula1, BinaryFormula) or (isinstance(formula1, BinaryFormula) and not formula1.is_conjunction()) 
              or true_value!='T'):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.IS_NOT_CONJUNCTION_TRUE, self.token_reference1, self))
      else:
          # If the left formula of conclusion (the conjunction) is one of the references 
          if(not (formula1.left == self.formula or formula1.right == self.formula)):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_LEFT_OR_RIGHT_CONJUNCTION, self.token_reference1, self))