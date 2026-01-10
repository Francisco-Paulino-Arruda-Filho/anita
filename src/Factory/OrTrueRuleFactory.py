from Factory.BaseRuleFactory import BaseRuleFactory
from models.binary_formula.BinaryFormula import BinaryFormula


class OrTrueRuleFactory(BaseRuleFactory):
    """Factory para regra |T (Disjunção Verdadeira) - Beta"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'OR_TRUE')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Pode criar se a fórmula é disjunção E valor verdade é T"""
        return (isinstance(formula, BinaryFormula) and 
                formula.is_disjunction() and 
                true_value == 'T')
    
    def get_rule_type(self) -> str:
        return "beta"