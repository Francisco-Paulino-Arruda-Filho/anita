from Factory.BaseRuleFactory import BaseRuleFactory
from models.quantifier_formula.ExistentialFormula import ExistentialFormula


class ExistsFalseRuleFactory(BaseRuleFactory):
    """Factory para regra EF (Existencial Falso)"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'EXT_FALSE')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Pode criar se a fórmula é existencial E valor verdade é F"""
        return (isinstance(formula, ExistentialFormula) and 
                true_value == 'F')
    
    def get_rule_type(self) -> str:
        return "alpha"