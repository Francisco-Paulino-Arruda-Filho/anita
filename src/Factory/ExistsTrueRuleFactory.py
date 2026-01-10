from Factory.BaseRuleFactory import BaseRuleFactory
from models.quantifier_formula.ExistentialFormula import ExistentialFormula


class ExistsTrueRuleFactory(BaseRuleFactory):
    """Factory para regra ET (Existencial Verdadeiro)"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'EXT_TRUE')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Pode criar se a fórmula é existencial E valor verdade é T"""
        return (isinstance(formula, ExistentialFormula) and 
                true_value == 'T')
    
    def get_rule_type(self) -> str:
        return "alpha"