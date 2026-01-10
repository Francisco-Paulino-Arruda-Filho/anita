from anita.factory.BaseRuleFactory import BaseRuleFactory
from anita.formula.binary_formula.BinaryFormula import BinaryFormula


class OrFalseRuleFactory(BaseRuleFactory):
    """Factory para regra |F (Disjunção Falsa)"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'OR_FALSE')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Pode criar se a fórmula é disjunção E valor verdade é F"""
        return (isinstance(formula, BinaryFormula) and 
                formula.is_disjunction() and 
                true_value == 'F')
    
    def get_rule_type(self) -> str:
        return "alpha"