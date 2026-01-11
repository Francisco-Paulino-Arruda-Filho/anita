

from enum import Enum

from anita.rules.IRule import IRule
from anita.rules.AndFalseRule import AndFalseRule
from anita.rules.AndTrueRule import AndTrueRule
from anita.rules.ClosedRule import ClosedRule
from anita.rules.ExistsFalseRule import ExistsFalseRule
from anita.rules.ExistsTrueRule import ExistsTrueRule
from anita.rules.ForAllFalseRule import ForAllFalseRule
from anita.rules.ForAllTrueRule import ForAllTrueRule
from anita.rules.ImpFalseRule import ImpFalseRule
from anita.rules.ImpTrueRule import ImpTrueRule
from anita.rules.NegationRule import NegationRule
from anita.rules.OrFalseRule import OrFalseRule
from anita.rules.OrTrueRule import OrTrueRule


class RuleType(Enum):
  CLOSED_RULE = 1
  EXISTS_TRUE_RULE = 2
  EXISTS_FALSE_RULE = 3
  OR_TRUE_RULE = 4
  OR_FALSE_RULE = 5
  AND_TRUE_RULE = 6
  AND_FALSE_RULE = 7
  IMPLICATION_TRUE_RULE = 8
  IMPLICATION_FALSE_RULE = 9
  FOR_ALL_TRUE_RULE = 10
  FOR_ALL_FALSE_RULE = 11
  NEGATION_RULE = 12

class RuleFactory:
  def __init__(self):
    self.rules_creators_mapper = {
      RuleType.CLOSED_RULE: ClosedRule,
      RuleType.EXISTS_TRUE_RULE: ExistsTrueRule,
      RuleType.EXISTS_FALSE_RULE: ExistsFalseRule,
      RuleType.OR_TRUE_RULE: OrTrueRule,
      RuleType.OR_FALSE_RULE: OrFalseRule,
      RuleType.AND_TRUE_RULE: AndTrueRule,
      RuleType.AND_FALSE_RULE: AndFalseRule,
      RuleType.IMPLICATION_TRUE_RULE: ImpTrueRule,
      RuleType.IMPLICATION_FALSE_RULE: ImpFalseRule,
      RuleType.FOR_ALL_TRUE_RULE: ForAllTrueRule,
      RuleType.FOR_ALL_FALSE_RULE: ForAllFalseRule,
      RuleType.NEGATION_RULE: NegationRule,
    }

  def create_rule(self, rule_type, *args, **kwargs) -> IRule:
    rule_class = self.rules_creators_mapper.get(rule_type)
    
    if rule_class:
      return rule_class(*args, **kwargs)
    return None