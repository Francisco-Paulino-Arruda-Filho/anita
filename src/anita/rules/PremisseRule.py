class PremisseRule():
    def __init__(self, token_line, token_true_value, token_formula):
        self.token_line = token_line
        self.token_formula = token_formula[0]
        self.token_true_value = token_true_value
        self.line = token_line.value
        self.formula = token_formula[1]
        self.true_value = token_true_value.value

    def evaluation(self,parser,deduction_result):
        return

    def toLatex(self, symbol_table):
        return '{}~{}'.format(self.true_value, self.formula.toLatex())

    def toString(self):
        return '{}. {} {} pre'.format(self.line, self.true_value, self.formula.toString())