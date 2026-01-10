from abc import abstractmethod
from typing import Type
from Factory.IRule import IRule
from Factory.IRuleFactory import IRuleFactory


class BaseRuleFactory(IRuleFactory):
    """Classe base abstrata para factories de regras"""
    
    def __init__(self, rule_class: Type[IRule], symbol_name: str):
        self.rule_class = rule_class
        self.symbol_name = symbol_name
    
    def create_rule(self, token_line, token_true_value, token_formula, 
                   token_symbol_rule, token_reference1, **kwargs) -> IRule:
        """Implementação padrão de criação de regra"""
        return self.rule_class(
            token_line, 
            token_true_value, 
            token_formula, 
            token_symbol_rule, 
            token_reference1,
            **kwargs
        )
    
    @abstractmethod
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        pass
    
    @abstractmethod
    def get_rule_type(self) -> str:
        pass