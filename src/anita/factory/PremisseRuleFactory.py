from anita.factory.BaseRuleFactory import BaseRuleFactory


class PremisseRuleFactory(BaseRuleFactory):
    """Factory para regra de Premissa"""
    
    def __init__(self, rule_class):
        super().__init__(rule_class, 'PREMISSE')
    
    def can_create(self, formula, true_value: str, context: dict) -> bool:
        """Premissa é identificada por contexto específico"""
        return context.get('is_premisse', False)
    
    def create_rule(self, token_line, token_true_value, token_formula, 
                   token_symbol_rule, token_reference1, **kwargs):
        """Premissa não usa token_symbol_rule nem reference"""
        return self.rule_class(token_line, token_true_value, token_formula)
    
    def get_rule_type(self) -> str:
        return "special"