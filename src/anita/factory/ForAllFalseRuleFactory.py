from anita.factory.BaseRuleFactory import BaseRuleFactory
from anita.formula.quantifier_formula.UniversalFormula import UniversalFormula


class ForAllFalseRuleFactory(BaseRuleFactory):
    """Factory para regra AF (Universal Falso)"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'ALL_FALSE')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Pode criar se a fórmula é universal E valor verdade é F"""
        return (isinstance(formula, UniversalFormula) and 
                true_value == 'F')
    
    def get_rule_type(self) -> str:
        return "alpha"