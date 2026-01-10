from abc import ABC, abstractmethod

from Factory.IRule import IRule

class IRuleFactory(ABC):
    """Interface para factories de regras"""
    
    @abstractmethod
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Verifica se esta factory pode criar uma regra para os parâmetros dados"""
        pass
    
    @abstractmethod
    def create_rule(self, token_line, token_true_value, token_formula, 
                   token_symbol_rule, token_reference1, **kwargs) -> IRule:
        """Cria uma instância da regra específica"""
        pass
    
    @abstractmethod
    def get_rule_type(self) -> str:
        """Retorna o tipo de regra (alpha, beta, etc)"""
        pass
