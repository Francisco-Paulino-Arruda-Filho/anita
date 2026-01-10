from Factory.BaseRuleFactory import BaseRuleFactory
from models.binary_formula.BinaryFormula import BinaryFormula


class AndTrueRuleFactory(BaseRuleFactory):
    """Factory para regra &T (Conjunção Verdadeira)"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'AND_TRUE')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Pode criar se a fórmula é conjunção E valor verdade é T"""
        return (isinstance(formula, BinaryFormula) and 
                formula.is_conjunction() and 
                true_value == 'T')
    
    def get_rule_type(self) -> str:
        return "alpha"