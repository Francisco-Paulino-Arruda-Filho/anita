from Factory.BaseRuleFactory import BaseRuleFactory
from models.binary_formula.BinaryFormula import BinaryFormula


class ImpFalseRuleFactory(BaseRuleFactory):
    """Factory para regra ->F (Implicação Falsa)"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'IMP_FALSE')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Pode criar se a fórmula é implicação E valor verdade é F"""
        return (isinstance(formula, BinaryFormula) and 
                formula.is_implication() and 
                true_value == 'F')
    
    def get_rule_type(self) -> str:
        return "alpha"