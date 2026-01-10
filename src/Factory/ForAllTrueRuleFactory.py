from Factory.BaseRuleFactory import BaseRuleFactory
from models.quantifier_formula.UniversalFormula import UniversalFormula


class ForAllTrueRuleFactory(BaseRuleFactory):
    """Factory para regra AT (Universal Verdadeiro)"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'ALL_TRUE')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Pode criar se a fórmula é universal E valor verdade é T"""
        return (isinstance(formula, UniversalFormula) and 
                true_value == 'T')
    
    def get_rule_type(self) -> str:
        return "alpha"