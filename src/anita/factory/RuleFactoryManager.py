from anita.factory.IRuleFactory import IRuleFactory


class RuleFactoryManager:
    """Gerenciador central de factories de regras"""
    
    def __init__(self):
        self._factories = []
    
    def register_factory(self, factory: IRuleFactory):
        """Registra uma nova factory"""
        self._factories.append(factory)
    
    def create_rule(self, formula, true_value: str, token_line, token_true_value, 
                   token_formula, token_reference1, context: dict = None, **kwargs):
        """
        Encontra a factory apropriada e cria a regra
        
        Args:
            formula: A fórmula a ser analisada
            true_value: Valor verdade ('T' ou 'F')
            context: Contexto adicional (ex: informações da symbol_table)
        """
        if context is None:
            context = {}
        
        # Procura a factory que pode criar a regra
        for factory in self._factories:
            if anita.factory.can_create(formula, true_value, context):
                # Cria o token_symbol_rule apropriado
                from rply import Token
                token_symbol_rule = Token(anita.factory.symbol_name, anita.factory.symbol_name)
                
                return anita.factory.create_rule(
                    token_line,
                    token_true_value,
                    token_formula,
                    token_symbol_rule,
                    token_reference1,
                    **kwargs
                )
        
        # Se nenhuma factory for encontrada, retorna None ou lança exceção
        return None
    
    def get_factories_by_type(self, rule_type: str):
        """Retorna todas as factories de um determinado tipo"""
        return [f for f in self._factories if f.get_rule_type() == rule_type]
    
    def list_factories(self):
        """Lista todas as factories registradas"""
        return [(f.__class__.__name__, f.get_rule_type()) for f in self._factories]