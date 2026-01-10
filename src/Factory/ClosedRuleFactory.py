from Factory.BaseRuleFactory import BaseRuleFactory


class ClosedRuleFactory(BaseRuleFactory):
    """Factory para regra de Fechamento (Closed)"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'CLOSED')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Closed é identificada por contexto específico"""
        return context.get('is_closed', False)
    
    def create_rule(self, token_line, token_true_value, token_formula, 
                   token_symbol_rule, token_reference1, **kwargs):
        """Closed usa duas referências"""
        token_reference2 = kwargs.get('token_reference2')
        return self.rule_class(
            token_line, 
            token_formula, 
            token_reference1, 
            token_reference2
        )
    
    def get_rule_type(self) -> str:
        return "special"