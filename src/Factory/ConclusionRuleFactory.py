from Factory.BaseRuleFactory import BaseRuleFactory


class ConclusionRuleFactory(BaseRuleFactory):
    """Factory para regra de Conclusão"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'CONCLUSION')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Conclusão é identificada por contexto específico"""
        return context.get('is_conclusion', False)
    
    def create_rule(self, token_line, token_true_value, token_formula, 
                   token_symbol_rule, token_reference1, **kwargs):
        """Conclusão não usa token_symbol_rule nem reference"""
        return self.rule_class(token_line, token_true_value, token_formula)
    
    def get_rule_type(self) -> str:
        return "special"