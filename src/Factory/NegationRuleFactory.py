from Factory.BaseRuleFactory import BaseRuleFactory
from models.athom_formula.NegationFormula import NegationFormula
from rply import Token


class NegationRuleFactory(BaseRuleFactory):
    """Factory para regras de negação (~T e ~F)"""
    
    def __init__(self, rule_class):
        # O symbol_name será determinado dinamicamente
        super().__init__(rule_class, 'NEG')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Pode criar se a fórmula é negação"""
        return isinstance(formula, NegationFormula)
    
    def create_rule(self, token_line, token_true_value, token_formula, 
                   token_symbol_rule, token_reference1, **kwargs):
        """Cria regra de negação com símbolo apropriado"""
        true_value = token_true_value.gettokentype()
        
        if true_value == 'TRUE':
            symbol = Token('NEG_FALSE', '~F')
        else:  # FALSE
            symbol = Token('NEG_TRUE', '~T')
        
        return self.rule_class(
            token_line,
            token_true_value,
            token_formula,
            symbol,
            token_reference1,
            **kwargs
        )
    
    def get_rule_type(self) -> str:
        return "alpha"