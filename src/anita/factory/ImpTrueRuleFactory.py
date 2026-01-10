from anita.factory.BaseRuleFactory import BaseRuleFactory
from anita.formula.binary_formula.BinaryFormula import BinaryFormula


class ImpTrueRuleFactory(BaseRuleFactory):
    """Factory para regra ->T (Implicação Verdadeira) - Beta"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'IMP_TRUE')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Pode criar se a fórmula é implicação E valor verdade é T"""
        return (isinstance(formula, BinaryFormula) and 
                formula.is_implication() and 
                true_value == 'T')
    
    def get_rule_type(self) -> str:
        return "beta"