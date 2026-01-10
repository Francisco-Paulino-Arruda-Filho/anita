
class BasicRule():
    def __init__(self, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=True):
        self.token_line = token_line
        self.token_formula = token_formula[0]
        self.token_true_value = token_true_value
        self.token_reference1 = token_reference1
        self.token_symbol_rule = token_symbol_rule
        self.line = token_line.value
        self.formula = token_formula[1]
        self.true_value = token_true_value.value
        self.reference1 = token_reference1.value
        self.show_token_symbol = show_token_symbol
        
    def toLatex(self, symbol_table):
        return '{}~{}'.format(self.true_value, self.formula.toLatex())
   
    def toString(self):
        if self.show_token_symbol:
            return '{}. {} {} {} {}'.format(self.line, self.true_value, self.formula.toString(), self.token_symbol_rule.value, self.reference1)
        else:
            return '{}. {} {} {}'.format(self.line, self.true_value, self.formula.toString(), self.reference1)