from abc import ABC, abstractmethod

class IRule(ABC):
    """Interface base para todas as regras"""
    
    @abstractmethod
    def evaluation(self, parser, deduction_result):
        """Avalia a regra e adiciona erros se necessário"""
        pass
    
    @abstractmethod
    def toString(self):
        """Converte a regra para string"""
        pass
    
    @abstractmethod
    def toLatex(self, symbol_table):
        """Converte a regra para LaTeX"""
        pass