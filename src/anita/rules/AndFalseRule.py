from anita.constants.constants import constants
from anita.rules.BasicRule import BasicRule
from anita.formula.binary_formula.BinaryFormula import BinaryFormula


class AndFalseRule(BasicRule):
    def evaluation(self,parser,deduction_result):
        before = parser.check_line_reference_before_rule_error(deduction_result,self)
        if before:
            parser.check_line_branch_reference_error(deduction_result,self, reference1=True)      

        formula1 = parser.symbol_table.lookup_formula_by_line(self.line, self.reference1)
        true_value = parser.symbol_table.lookup_true_value_by_line(self.line, self.reference1)
        if(formula1 is None):
            return
        
        if(not isinstance(formula1, BinaryFormula) or (isinstance(formula1, BinaryFormula) and not formula1.is_conjunction()) 
            or true_value!='F'):
            parser.has_error = True
            deduction_result.add_error(parser.get_error(constants.IS_NOT_CONJUNCTION_FALSE, self.token_reference1, self))
        else:
            if(not (formula1.left == self.formula or formula1.right == self.formula)):
                parser.has_error = True
                deduction_result.add_error(parser.get_error(constants.INVALID_LEFT_OR_RIGHT_CONJUNCTION, self.token_formula, self))