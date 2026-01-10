from anita.constants.constants import constants
from anita.rules.BasicRule import BasicRule
from anita.formula.athom_formula.NegationFormula import NegationFormula


class NegationRule(BasicRule):
    def evaluation(self,parser,deduction_result):
      # If the references lines occur before the rule line 
      before = parser.check_line_reference_before_rule_error(deduction_result,self)
      if before:
        parser.check_line_branch_reference_error(deduction_result,self, reference1=True)      

      formula1= parser.symbol_table.lookup_formula_by_line(self.line, self.reference1)
      true_value = parser.symbol_table.lookup_true_value_by_line(self.line, self.reference1)
      if(formula1 is None):
        return

      # If the formula is not a negation formula or the true value is not different
      if(formula1 != NegationFormula(self.formula)):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.INVALID_RESULT, self.token_reference1, self))
      elif (true_value=='F' and self.token_symbol_rule.gettokentype() == 'NEG_TRUE'):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.IS_NOT_NEGATION_TRUE, self.token_reference1, self))
      elif (true_value=='T' and self.token_symbol_rule.gettokentype() == 'NEG_FALSE'):
          parser.has_error = True
          deduction_result.add_error(parser.get_error(constants.IS_NOT_NEGATION_FALSE, self.token_reference1, self))