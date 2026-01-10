from  anita.rules.BasicRule import BasicRule
from anita.formula.binary_formula.BinaryFormula import BinaryFormula
from anita.constants.constants import constants

class ImpTrueRule(BasicRule):
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
      if(not isinstance(formula1, BinaryFormula) or (isinstance(formula1, BinaryFormula) and not formula1.is_implication())):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.IS_NOT_IMPLICATION, self.token_reference1, self))
      else:
          # If the left formula of conclusion (the conjunction) is one of the references 
          if(formula1.left == self.formula):
            if(true_value==self.true_value):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_LEFT_IMPLICATION, self.token_line, self))
          elif(formula1.right == self.formula):
            if(true_value!=self.true_value):
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_RIGHT_IMPLICATION, self.token_true_value, self))
          else:
              parser.has_error = True
              deduction_result.add_error(parser.get_error(constants.INVALID_LEFT_RIGHT_IMPLICATION, self.token_true_value, self))