import traceback
from rply import ParserGenerator
from rply import Token
import sys

from anita.utils.i18n import t
from anita.rules.RuleFactory import RuleFactory, RuleType
from anita.rules.AndFalseRule import AndFalseRule
from anita.rules.AndTrueRule import AndTrueRule
from anita.rules.BasicRule import BasicRule
from anita.rules.ClosedRule import ClosedRule
from anita.rules.ConclusionRule import ConclusionRule
from anita.rules.ExistsFalseRule import ExistsFalseRule
from anita.rules.ExistsTrueRule import ExistsTrueRule
from anita.rules.ForAllFalseRule import ForAllFalseRule
from anita.rules.ForAllTrueRule import ForAllTrueRule
from anita.rules.ImpFalseRule import ImpFalseRule
from anita.rules.ImpTrueRule import ImpTrueRule
from anita.rules.NegationRule import NegationRule
from anita.rules.OrFalseRule import OrFalseRule
from anita.rules.OrTrueRule import OrTrueRule
from anita.rules.PremisseRule import PremisseRule
from anita.formula.binary_formula.AndFormula import AndFormula
from anita.formula.binary_formula.BinaryFormula import BinaryFormula
from anita.formula.binary_formula.OrFormula import OrFormula
from anita.formula.binary_formula.ImplicationFormula import ImplicationFormula
from anita.formula.binary_formula.BiImplicationFormula import BiImplicationFormula
from anita.formula.athom_formula.AtomFormula import AthomFormula
from anita.formula.athom_formula.NegationFormula import NegationFormula
from anita.formula.predicate_formula.PredicateFormula import PredicateFormula
from anita.formula.quantifier_formula.UniversalFormula import UniversalFormula
from anita.formula.quantifier_formula.ExistentialFormula import ExistentialFormula
from anita.lexer.lexer import Lexer
from anita.constants.constants import constants
from anita.utils.symbol_table import SymbolTable
from anita.utils.tableau_deduction_return import tableau_deduction_return
from anita.utils.value_error_handle import value_error_handle

## File analisys.py

deduction_result = tableau_deduction_return()

sys.excepthook = lambda exctype, value, tb: value_error_handle(exctype, value, tb, deduction_result)

class ParserAnita():
    def __init__(self, state):
        self.state = state
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['NUM', 'DOT', 'COMMA', 'OPEN_PAREN', 'CLOSE_PAREN', 'NOT', 'BOTTOM',
             'AND', 'OR', 'AND_TRUE', 'AND_FALSE', 'NEG_TRUE', 'NEG_FALSE','OR_FALSE', 'OR_TRUE', 'IMP_FALSE', 'IMP_TRUE', 
             'PREMISSE', 'ATHOM', 'OPEN_BRACKET', 'CLOSE_BRACKET', 'IMPLIE', 'CONCLUSION', 'CLOSED',
             'VAR', 'EXT', 'ALL', 'ALL_TRUE', 'EXT_FALSE', 'EXT_TRUE', 'ALL_FALSE', 'TRUE', 'FALSE' ],
            #The precedence $\lnot,\forall,\exists,\land,\lor,\rightarrow,\leftrightarrow$
            precedence=[
                ('right', ['IMPLIE']),
                ('right', ['OR']),
                ('right', ['AND']),
                ('right', ['EXT']),
                ('right', ['ALL']),
                ('right', ['NOT']),
            ]
        )
        self.symbol_table = SymbolTable()
        self.has_error = False
        self.rule_factory = RuleFactory()


    def verify_sequence_lines_error(self, deduction_result):
        productions = self.state.splitlines()
        i = 1
        for p in productions:
          x = p.split('.')[0]
          if x.isdigit():
            if int(x)!=i: 
              self.has_error = True
              if(i==1): 
                deduction_result.add_error('{}\n^, A numeração da linha {} deveria ser {}, pois a numeração da prova deve ser sequencial e iniciar em 1.\n'.format(p,x,i))
              else: 
                deduction_result.add_error('{}\n^, A numeração da linha {} deveria ser {}, pois a numeração da prova deve ser sequencial.\n'.format(p,x,i))
              break
            i+=1

    def check_is_closed_branches_by_rule(self,deduction_result):
      if(not self.symbol_table.is_closed_branchs()):
        self.has_error = True
        for key, branch in self.symbol_table.symbol_table.items():
          if (key=='branch_0'): 
            continue
          if(branch['end_line'] is None): 
            begin_rule = branch["rules"][0]
            begin_token = branch["rules"][0].token_formula
            deduction_result.add_error(self.get_error(constants.BOX_MUST_BE_DISPOSED, begin_token, begin_rule))

    def check_is_valid_initial_tableau(self,deduction_result):
      if (not self.symbol_table.is_valid_initial_tableau()):
        self.has_error = True
        begin_rule = self.symbol_table.symbol_table['branch_0']["rules"][0]
        begin_token = self.symbol_table.symbol_table['branch_0']["rules"][0].token_formula
        deduction_result.add_error(self.get_error(constants.INVALID_INITIAL_TABLEAU, begin_token, begin_rule))

    def check_line_reference_before_rule_error(self, deduction_result, rule):
      result = True
      if hasattr(rule, 'reference1'):
        if(int(rule.reference1) >= int(rule.line)):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.REFERENCED_LINE_NOT_DEFINED, rule.token_reference1, rule))
            result = False
      if hasattr(rule, 'reference2'):
        if(int(rule.reference2) >= int(rule.line)):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.REFERENCED_LINE_NOT_DEFINED, rule.token_reference2, rule))
            result = False
      return result

    def check_line_branch_reference_error(self, deduction_result, rule, reference1=False, reference2=False):
      result = True
      if reference1:
        if (self.symbol_table.lookup_formula_by_line(rule.line, rule.reference1) is None):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.USING_DESCARTED_RULE, rule.token_reference1, rule))
            result = False
      if reference2:
        if (self.symbol_table.lookup_formula_by_line(rule.line, rule.reference2) is None):
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.USING_DESCARTED_RULE, rule.token_reference2, rule))
            result = False
      return result


    def parse(self):
        deduction_result = tableau_deduction_return()
        @self.pg.production('program : steps')
        def program(p):
            self.verify_sequence_lines_error(deduction_result)
            self.check_is_closed_branches_by_rule(deduction_result)
            self.check_is_valid_initial_tableau(deduction_result)

            rule_info = p[0]
            for i in rule_info:
                rule_line, formula_reference = rule_info[i]

                rule = self.symbol_table.get_rule(rule_line.value)
                if(isinstance(rule, PremisseRule) ):
                    pass
                elif(isinstance(rule, ConclusionRule) ):
                    pass
                elif(isinstance(rule, NegationRule)):
                    rule.evaluation(self, deduction_result)
                    #Verifica se a regra já foi utilizada anteriormente
                    if self.symbol_table.count_used_rule_in_the_branch(rule)>1:
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.ALREADY_USED_RULE_IN_BRANCH, rule.token_reference1, rule))
                elif(isinstance(rule, ClosedRule)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, AndTrueRule)):
                    rule.evaluation(self, deduction_result)

                    #Verifica se ambas as fórmulas da conjunção estão definidas
                    formula1 = self.symbol_table.lookup_formula_by_line(rule.line,rule.reference1)
                    if formula1 is None or not isinstance(formula1, BinaryFormula):
                      continue
                    rule_AndTrue = self.symbol_table.get_rule(rule.reference1)
                    rule_previous = self.symbol_table.get_rule(str(int(rule.line)-1))
                    rule_next = self.symbol_table.get_rule(str(int(rule.line)+1))
                    if(formula1.left==rule.formula):    
                      if not ( rule_previous is not None and isinstance(rule_previous, AndTrueRule) and formula1.left==rule_previous.formula):                  
                        if( rule_next is None or (not isinstance(rule_next, AndTrueRule)) or formula1.right!=rule_next.formula):
                          self.has_error = True
                          deduction_result.add_error(self.get_error(constants.INVALID_TRUE_CONJUNCTION_NEXT, rule.token_line, rule_AndTrue))
                    elif(formula1.right==rule.formula):                      
                      if( rule_previous is None or (not isinstance(rule_previous, AndTrueRule)) or formula1.left!=rule_previous.formula):
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.INVALID_TRUE_CONJUNCTION_PREVIOUS, rule.token_line, rule_AndTrue))

                    #Verifica se a regra já foi utilizada anteriormente
                    if self.symbol_table.count_used_rule_in_the_branch(rule)>2:
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.ALREADY_USED_RULE_IN_BRANCH, rule.token_reference1, rule))
                elif(isinstance(rule, AndFalseRule)):
                    rule.evaluation(self, deduction_result)
                    branch = self.symbol_table.find_branch(rule.line)
                    branch_parent = self.symbol_table.symbol_table[branch]['parent']
                    branchs = self.symbol_table.symbol_table[branch_parent]['children']
                    last_rule_parent =self.symbol_table.symbol_table[branch_parent]['rules'][-1]
                    first_branch_rule =branchs[0]['rules'][0]
                    if(last_rule_parent.line!=str(int(first_branch_rule.line)-1) or len(branchs)!=2):
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.INVALID_BETA_RULE, rule.token_line, rule))
                    else:
                      formula1 = self.symbol_table.lookup_formula_by_line(rule.line,rule.reference1)
                      if formula1 is None or not isinstance(formula1, BinaryFormula):
                        continue
                      rule_AndFalse = self.symbol_table.get_rule(rule.reference1)
                      if(formula1.left==rule.formula):                      
                        rule_next = branchs[1]['rules'][0]
                        if( rule_next is None or (not isinstance(rule_next, AndFalseRule)) or formula1.right!=rule_next.formula):
                          self.has_error = True
                          deduction_result.add_error(self.get_error(constants.INVALID_FALSE_CONJUNCTION_NEXT, rule.token_line, rule_AndFalse))
                      elif(formula1.right==rule.formula):                      
                        rule_previous = branchs[0]['rules'][0]
                        if( rule_previous is None or (not isinstance(rule_previous, AndFalseRule)) or formula1.left!=rule_previous.formula):
                          self.has_error = True
                          deduction_result.add_error(self.get_error(constants.INVALID_FALSE_CONJUNCTION_PREVIOUS, rule.token_line, rule_AndFalse))
                    #Verifica se a regra já foi utilizada anteriormente
                    if self.symbol_table.count_used_rule_in_the_branch(rule)>1:
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.ALREADY_USED_RULE_IN_BRANCH, rule.token_reference1, rule))

                elif(isinstance(rule, OrFalseRule)):
                    rule.evaluation(self, deduction_result)
                    #Verifica se ambas as fórmulas da disjunção estão definidas
                    formula1 = self.symbol_table.lookup_formula_by_line(rule.line,rule.reference1)
                    if formula1 is None or not isinstance(formula1, BinaryFormula):
                      continue
                    rule_OrFalse = self.symbol_table.get_rule(rule.reference1)
                    rule_previous = self.symbol_table.get_rule(str(int(rule.line)-1))
                    rule_next = self.symbol_table.get_rule(str(int(rule.line)+1))
                    if(formula1.left==rule.formula):    
                      if not (rule_previous is not None and isinstance(rule_previous, OrFalseRule) and formula1.left==rule_previous.formula):
                        if( rule_next is None or (not isinstance(rule_next, OrFalseRule)) or formula1.right!=rule_next.formula):
                          self.has_error = True
                          deduction_result.add_error(self.get_error(constants.INVALID_FALSE_DISJUNCTION_NEXT, rule.token_line, rule_OrFalse))
                    elif(formula1.right==rule.formula):                      
                      if( rule_previous is None or (not isinstance(rule_previous, OrFalseRule)) or formula1.left!=rule_previous.formula):
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.INVALID_FALSE_DISJUNCTION_PREVIOUS, rule.token_line, rule_OrFalse))
                    #Verifica se a regra já foi utilizada anteriormente
                    if self.symbol_table.count_used_rule_in_the_branch(rule)>2:
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.ALREADY_USED_RULE_IN_BRANCH, rule.token_reference1, rule))
                
                elif(isinstance(rule, OrTrueRule)):
                    rule.evaluation(self, deduction_result)
                    branch = self.symbol_table.find_branch(rule.line)
                    branch_parent = self.symbol_table.symbol_table[branch]['parent']
                    branchs = self.symbol_table.symbol_table[branch_parent]['children']
                    last_rule_parent =self.symbol_table.symbol_table[branch_parent]['rules'][-1]
                    first_branch_rule =branchs[0]['rules'][0]
                    if(last_rule_parent.line!=str(int(first_branch_rule.line)-1) or len(branchs)!=2):
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.INVALID_BETA_RULE, rule.token_line, rule))
                    else:
                      formula1 = self.symbol_table.lookup_formula_by_line(rule.line,rule.reference1)
                      if formula1 is None or not isinstance(formula1, BinaryFormula):
                        continue
                      rule_OrTrue = self.symbol_table.get_rule(rule.reference1)
                      if(formula1.left==rule.formula):                      
                        rule_next = branchs[1]['rules'][0]
                        if( rule_next is None or (not isinstance(rule_next, OrTrueRule)) or formula1.right!=rule_next.formula):
                          self.has_error = True
                          deduction_result.add_error(self.get_error(constants.INVALID_TRUE_DISJUNCTION_NEXT, rule.token_line, rule_OrTrue))
                      elif(formula1.right==rule.formula):                      
                        rule_previous = branchs[0]['rules'][0]
                        if( rule_previous is None or (not isinstance(rule_previous, OrTrueRule)) or formula1.left!=rule_previous.formula):
                          self.has_error = True
                          deduction_result.add_error(self.get_error(constants.INVALID_TRUE_DISJUNCTION_PREVIOUS, rule.token_line, rule_OrTrue))
                    #Verifica se a regra já foi utilizada anteriormente
                    if self.symbol_table.count_used_rule_in_the_branch(rule)>1:
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.ALREADY_USED_RULE_IN_BRANCH, rule.token_reference1, rule))

                elif(isinstance(rule, ImpTrueRule)):
                    rule.evaluation(self, deduction_result)
                    branch = self.symbol_table.find_branch(rule.line)
                    branch_parent = self.symbol_table.symbol_table[branch]['parent']
                    branchs = self.symbol_table.symbol_table[branch_parent]['children']
                    last_rule_parent =self.symbol_table.symbol_table[branch_parent]['rules'][-1]
                    first_branch_rule =branchs[0]['rules'][0]
                    if(last_rule_parent.line!=str(int(first_branch_rule.line)-1) or len(branchs)!=2):
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.INVALID_BETA_RULE, rule.token_line, rule))
                    else:
                      formula1 = self.symbol_table.lookup_formula_by_line(rule.line,rule.reference1)
                      if formula1 is None or not isinstance(formula1, BinaryFormula):
                        continue
                      rule_ImpTrue = self.symbol_table.get_rule(rule.reference1)
                      if(formula1.left==rule.formula):                      
                        rule_next = branchs[1]['rules'][0]
                        if( rule_next is None or (not isinstance(rule_next, ImpTrueRule)) or formula1.right!=rule_next.formula):
                          self.has_error = True
                          deduction_result.add_error(self.get_error(constants.INVALID_TRUE_IMPLICATION_NEXT, rule.token_line, rule_ImpTrue))
                      elif(formula1.right==rule.formula):                      
                        rule_previous = branchs[0]['rules'][0]
                        if( rule_previous is None or (not isinstance(rule_previous, ImpTrueRule)) or formula1.left!=rule_previous.formula):
                          self.has_error = True
                          deduction_result.add_error(self.get_error(constants.INVALID_TRUE_IMPLICATION_PREVIOUS, rule.token_line, rule_ImpTrue))
                     #Verifica se a regra já foi utilizada anteriormente
                    if self.symbol_table.count_used_rule_in_the_branch(rule)>1:
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.ALREADY_USED_RULE_IN_BRANCH, rule.token_reference1, rule))

                elif(isinstance(rule, ImpFalseRule)):
                    rule.evaluation(self, deduction_result)
                    #Verifica se ambas as fórmulas da implicação estão definidas
                    formula1 = self.symbol_table.lookup_formula_by_line(rule.line,rule.reference1)
                    if formula1 is None or not isinstance(formula1, BinaryFormula):
                      continue
                    rule_ImpFalse = self.symbol_table.get_rule(rule.reference1)
                    if(formula1.left==rule.formula and rule.token_true_value.gettokentype()=='TRUE'):                      
                      rule_next = self.symbol_table.get_rule(str(int(rule.line)+1))
                      if( rule_next is None or (not isinstance(rule_next, ImpFalseRule)) or formula1.right!=rule_next.formula):
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.INVALID_FALSE_IMPLICATION_NEXT, rule.token_line, rule_ImpFalse))
                    elif(formula1.right==rule.formula and rule.token_true_value.gettokentype()=='FALSE'):                      
                      rule_previous = self.symbol_table.get_rule(str(int(rule.line)-1))
                      if( rule_previous is None or (not isinstance(rule_previous, ImpFalseRule)) or formula1.left!=rule_previous.formula):
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.INVALID_FALSE_IMPLICATION_PREVIOUS, rule.token_line, rule_ImpFalse))
                    #Verifica se a regra já foi utilizada anteriormente
                    if self.symbol_table.count_used_rule_in_the_branch(rule)>2:
                        self.has_error = True
                        deduction_result.add_error(self.get_error(constants.ALREADY_USED_RULE_IN_BRANCH, rule.token_reference1, rule))
                elif(isinstance(rule, ForAllTrueRule)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, ForAllFalseRule)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, ExistsTrueRule)):
                    rule.evaluation(self, deduction_result)
                elif(isinstance(rule, ExistsFalseRule)):
                    rule.evaluation(self, deduction_result)

            if(not self.has_error):
                deduction_result.latex = self.symbol_table.toLatex()
                deduction_result.premisses = self.symbol_table.getPremissesFormulas()
                deduction_result.conclusion = self.symbol_table.getConclusionFormula()
                deduction_result.theorem = ParserAnita.toString(deduction_result.premisses, deduction_result.conclusion)
                deduction_result.latex_theorem = ParserAnita.toLatex(deduction_result.premisses, deduction_result.conclusion)
                deduction_result.counter_examples = self.symbol_table.get_counter_examples_toString()
                deduction_result.is_closed = self.symbol_table.is_closed_tableau()
                deduction_result.saturared_branches, deduction_result.open_branches = self.symbol_table.get_open_saturated_branches()
                if(deduction_result.saturared_branches!=[]):
                  rules = []
                  for branch in deduction_result.saturared_branches:
                    rules = rules+ branch
                  deduction_result.colored_latex = self.symbol_table.toLatex(rules=rules,color="red")
                elif(deduction_result.open_branches!=[]):
                  rules = []
                  for branch in deduction_result.open_branches:
                    rules = rules+ branch
                  deduction_result.colored_latex = self.symbol_table.toLatex(rules=rules,color="red")
                else:
                  rules = self.symbol_table.get_reference_closed_rule()
                  deduction_result.colored_latex = self.symbol_table.toLatex(rules=rules,color="blue")
            return deduction_result

        @self.pg.production('steps : steps step')
        @self.pg.production('steps : step')
        def steps(p):
            if len(p) == 1:
                result = p[0]
                return {result[0].value: result}
            else:
                result = p[1]
                p[0][result[0].value] = result
                return p[0]

        # Alpha Rules without rule's name
        @self.pg.production('step : NUM DOT FALSE formula NUM')
        @self.pg.production('step : NUM DOT TRUE formula NUM')
        def Rule_alpha(p):
            token_line = p[0]
            token_true_value = p[2]
            token_formula = p[3]
            token_reference1 = p[4]
            formula = token_formula[1] 
            formula1 = self.symbol_table.lookup_formula_by_line(token_reference1.value, token_reference1.value)
            true_value_formula1 = self.symbol_table.lookup_true_value_by_line(token_reference1.value, token_reference1.value)
            if(isinstance(formula1, BinaryFormula) and formula1.is_conjunction() and true_value_formula1=='T'):
              token_symbol_rule = Token('AND_TRUE', '&T')
              f = self.rule_factory.create_rule(RuleType.AND_TRUE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
              if token_true_value.gettokentype() == 'FALSE':  
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, f))              
            elif(isinstance(formula1, BinaryFormula) and formula1.is_conjunction() and true_value_formula1=='F'):
              token_symbol_rule = Token('AND_FALSE', '&F')
              f = BasicRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_BETA, token_reference1, f))              
            elif(isinstance(formula1, BinaryFormula) and formula1.is_disjunction() and true_value_formula1=='F'):
              token_symbol_rule = Token('OR_FALSE', '|F')
              f = self.rule_factory.create_rule(RuleType.OR_FALSE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
              if token_true_value.gettokentype() == 'TRUE':  
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, f))              
            elif(isinstance(formula1, BinaryFormula) and formula1.is_disjunction() and true_value_formula1=='T'):
              token_symbol_rule = Token('OR_TRUE', '|T')
              f = BasicRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_BETA, token_reference1, f))              
            elif(isinstance(formula1, BinaryFormula) and formula1.is_implication() and true_value_formula1=='F'):
              token_symbol_rule = Token('IMP_FALSE', '->F')
              f = self.rule_factory.create_rule(RuleType.IMPLICATION_FALSE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
            elif(isinstance(formula1, BinaryFormula) and formula1.is_implication() and true_value_formula1=='T'):
              token_symbol_rule = Token('IMP_TRUE', '->T')
              f = BasicRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_BETA, token_reference1, f))              
            elif(isinstance(formula1, NegationFormula)):
              if true_value_formula1=='T':
                token_symbol_rule = Token('NEG_TRUE', '~T')
              elif true_value_formula1=='F':
                token_symbol_rule = Token('NEG_FALSE', '~F')
              negation = self.rule_factory.create_rule(RuleType.NEGATION_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(negation)
              if (token_true_value.gettokentype() == 'TRUE' and token_symbol_rule.gettokentype() == 'NEG_TRUE') or (token_true_value.gettokentype() == 'FALSE' and token_symbol_rule.gettokentype() == 'NEG_FALSE') :  
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, negation)) 

            elif(isinstance(formula1, UniversalFormula) and true_value_formula1=='T'):
              token_symbol_rule = Token('ALL_TRUE', 'AT')
              f = self.rule_factory.create_rule(RuleType.FOR_ALL_TRUE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
              if token_true_value.gettokentype() == 'FALSE':  
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, f))              
            elif(isinstance(formula1, UniversalFormula)  and true_value_formula1=='F'):
              token_symbol_rule = Token('ALL_FALSE', 'AF')
              f = self.rule_factory.create_rule(RuleType.FOR_ALL_FALSE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
              if token_true_value.gettokentype() == 'TRUE':  
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, f))              
            elif(isinstance(formula1, ExistentialFormula)  and true_value_formula1=='T'):
              token_symbol_rule = Token('EXT_TRUE', 'ET')
              f = self.rule_factory.create_rule(RuleType.EXISTS_TRUE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
              if token_true_value.gettokentype() == 'FALSE':  
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, f))              
            elif(isinstance(formula1, ExistentialFormula)  and true_value_formula1=='F'):
              token_symbol_rule = Token('EXT_FALSE', 'EF')
              f = self.rule_factory.create_rule(RuleType.EXISTS_FALSE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
              if token_true_value.gettokentype() == 'TRUE':  
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, f))              
            else:
              token_symbol_rule = None
              f = BasicRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_CANNOT_BE_APPLIED, token_reference1, f))              

            return token_line, formula

        # Beta Rules without rule's name
        @self.pg.production('step : NUM DOT OPEN_BRACKET TRUE formula NUM')
        @self.pg.production('step : NUM DOT OPEN_BRACKET FALSE formula NUM')
        def Rule_beta(p):
            token_line = p[0]
            token_true_value = p[3]
            token_formula = p[4]
            token_reference1 = p[5]
            formula = token_formula[1] 
            formula1 = self.symbol_table.lookup_formula_by_line(token_reference1.value, token_reference1.value)
            true_value_formula1 = self.symbol_table.lookup_true_value_by_line(token_reference1.value, token_reference1.value)
            if(isinstance(formula1, BinaryFormula) and formula1.is_conjunction() and true_value_formula1=='T'):
              token_symbol_rule = Token('AND_TRUE', '&T')
              f = BasicRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.add_branch(token_line.value)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_ALPHA, token_reference1, f))              
            elif(isinstance(formula1, BinaryFormula) and formula1.is_conjunction() and true_value_formula1=='F'):
              token_symbol_rule = Token('AND_FALSE', '&F')
              f = self.rule_factory.create_rule(RuleType.AND_FALSE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.add_branch(token_line.value)
              self.symbol_table.insert(f)
              if token_true_value.gettokentype() == 'TRUE':  
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, f))              
            elif(isinstance(formula1, BinaryFormula) and formula1.is_disjunction() and true_value_formula1=='F'):
              token_symbol_rule = Token('OR_FALSE', '|F')
              f = BasicRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.add_branch(token_line.value)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_ALPHA, token_reference1, f))              
            elif(isinstance(formula1, BinaryFormula) and formula1.is_disjunction() and true_value_formula1=='T'):
              token_symbol_rule = Token('OR_TRUE', '|T')
              f = self.rule_factory.create_rule(RuleType.OR_TRUE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.add_branch(token_line.value)
              self.symbol_table.insert(f)
              if token_true_value.gettokentype() == 'FALSE':  
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, f))              
            elif(isinstance(formula1, BinaryFormula) and formula1.is_implication() and true_value_formula1=='F'):
              token_symbol_rule = Token('IMP_FALSE', '->F')
              f = BasicRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.add_branch(token_line.value)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_ALPHA, token_reference1, f))              
            elif(isinstance(formula1, BinaryFormula) and formula1.is_implication() and true_value_formula1=='T'):
              token_symbol_rule = Token('IMP_TRUE', '->T')
              f = self.rule_factory.create_rule(RuleType.IMPLICATION_TRUE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.add_branch(token_line.value)
              self.symbol_table.insert(f)
            elif(isinstance(formula1, NegationFormula)):
              if true_value_formula1=='T':
                token_symbol_rule = Token('NEG_TRUE', '~T')
              elif true_value_formula1=='F':
                token_symbol_rule = Token('NEG_FALSE', '~F')
              f = BasicRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.add_branch(token_line.value)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_ALPHA, token_reference1, f))              
            elif(isinstance(formula1, UniversalFormula) and true_value_formula1=='T'):
              token_symbol_rule = Token('ALL_TRUE', 'AT')
              f = self.rule_factory.create_rule(RuleType.FOR_ALL_TRUE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.add_branch(token_line.value)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_ALPHA, token_reference1, f))              
            elif(isinstance(formula1, UniversalFormula)  and true_value_formula1=='F'):
              token_symbol_rule = Token('ALL_FALSE', 'AF')
              f = self.rule_factory.create_rule(RuleType.FOR_ALL_FALSE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.add_branch(token_line.value)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_ALPHA, token_reference1, f))              
            elif(isinstance(formula1, ExistentialFormula)  and true_value_formula1=='T'):
              token_symbol_rule = Token('EXT_TRUE', 'ET')
              f = self.rule_factory.create_rule(RuleType.EXISTS_TRUE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.add_branch(token_line.value)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_ALPHA, token_reference1, f))              
            elif(isinstance(formula1, ExistentialFormula)  and true_value_formula1=='F'):
              token_symbol_rule = Token('EXT_FALSE', 'EF')
              f = self.rule_factory.create_rule(RuleType.EXISTS_FALSE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.add_branch(token_line.value)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_ALPHA, token_reference1, f))              
            else:
              token_symbol_rule = None
              f = BasicRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1, show_token_symbol=False)
              self.symbol_table.insert(f)
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_CANNOT_BE_APPLIED, token_reference1, f))              
            return token_line, formula

        @self.pg.production('step : NUM DOT formula NUM COMMA NUM')
        def Rule_closed_rule(p):
            token_line = p[0]
            token_formula = p[2]
            token_reference1 = p[3]
            token_reference2 = p[5]
            formula = token_formula[1] 
            closed = ClosedRule(token_line, token_formula, token_reference1, token_reference2)
            self.symbol_table.insert(closed)
            return token_line, formula


### Rules with Rule's name
        @self.pg.production('step : NUM DOT FALSE formula PREMISSE')
        @self.pg.production('step : NUM DOT TRUE formula PREMISSE')
        def Premisse(p):
          token_line = p[0]
          token_true_value = p[2]
          token_formula = p[3]
          premisse = PremisseRule(token_line, token_true_value, token_formula)
          self.symbol_table.insert(premisse)
          if token_true_value.gettokentype() == 'FALSE':  
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.PREMISSE_SHOULD_BE_TRUE, token_true_value, premisse))              
          return token_line, formula


        @self.pg.production('step : NUM DOT TRUE formula CONCLUSION')
        @self.pg.production('step : NUM DOT FALSE formula CONCLUSION')
        def Conclusion(p):
            token_line = p[0]
            token_true_value = p[2]
            token_formula = p[3]
            formula = token_formula[1]
            conclusion = ConclusionRule(token_line, token_true_value, token_formula)
            self.symbol_table.insert(conclusion)
            if token_true_value.gettokentype() == 'TRUE':  
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.CONCLUSION_SHOULD_BE_FALSE, token_true_value, conclusion))              
            return token_line, formula


        @self.pg.production('step : NUM DOT FALSE formula AND_TRUE NUM')
        @self.pg.production('step : NUM DOT TRUE formula AND_TRUE NUM')
        def And_true(p):
            token_line = p[0]
            token_true_value = p[2]
            token_formula = p[3]
            token_symbol_rule = p[4]
            token_reference1 = p[5]
            formula = token_formula[1] 
            andTrue = self.rule_factory.create_rule(RuleType.AND_TRUE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
            self.symbol_table.insert(andTrue)
            if token_true_value.gettokentype() == 'FALSE':  
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, andTrue))              

            return token_line, formula

        @self.pg.production('step : NUM DOT OPEN_BRACKET TRUE formula AND_FALSE NUM')
        @self.pg.production('step : NUM DOT OPEN_BRACKET FALSE formula AND_FALSE NUM')
        def And_false(p):
            token_line = p[0]
            token_true_value = p[3]
            token_formula = p[4]
            token_symbol_rule = p[5]
            token_reference1 = p[6]
            formula = token_formula[1] 
            
            andFalse = self.rule_factory.create_rule(RuleType.AND_FALSE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
            self.symbol_table.add_branch(token_line.value)
            self.symbol_table.insert(andFalse)
            if token_true_value.gettokentype() == 'TRUE':  
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, andFalse))              
            return token_line, formula

        @self.pg.production('step : NUM DOT OPEN_BRACKET FALSE formula OR_TRUE NUM')
        @self.pg.production('step : NUM DOT OPEN_BRACKET TRUE formula OR_TRUE NUM')
        def Or_true(p):
            token_line = p[0]
            token_true_value = p[3]
            token_formula = p[4]
            token_symbol_rule = p[5]
            token_reference1 = p[6]
            formula = token_formula[1] 
            
            OrTrue = self.rule_factory.create_rule(RuleType.OR_TRUE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
            self.symbol_table.add_branch(token_line.value)
            self.symbol_table.insert(OrTrue)
            if token_true_value.gettokentype() == 'FALSE':  
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, OrTrue))              
            return token_line, formula

        @self.pg.production('step : NUM DOT TRUE formula OR_FALSE NUM')
        def Or_false_wrong(p):
            token_line = p[0]
            token_true_value = p[2]
            token_formula = p[3]
            token_symbol_rule = p[4]
            token_reference1 = p[5]
            formula = token_formula[1] 
            
            orFalse = BasicRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
            self.symbol_table.insert(orFalse)
            if token_true_value.gettokentype() == 'TRUE':  
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.RULE_MUST_BE_BETA, token_reference1, orFalse))              
            return token_line, formula

        @self.pg.production('step : NUM DOT FALSE formula OR_FALSE NUM')
        def Or_false(p):
            token_line = p[0]
            token_true_value = p[2]
            token_formula = p[3]
            token_symbol_rule = p[4]
            token_reference1 = p[5]
            formula = token_formula[1] 
            
            orFalse = self.rule_factory.create_rule(RuleType.OR_FALSE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
            self.symbol_table.insert(orFalse)
            return token_line, formula

        @self.pg.production('step : NUM DOT OPEN_BRACKET TRUE formula IMP_TRUE NUM')
        @self.pg.production('step : NUM DOT OPEN_BRACKET FALSE formula IMP_TRUE NUM')
        def Imp_true(p):
            token_line = p[0]
            token_true_value = p[3]
            token_formula = p[4]
            token_symbol_rule = p[5]
            token_reference1 = p[6]
            formula = token_formula[1] 
            
            ImpTrue = self.rule_factory.create_rule(RuleType.IMPLICATION_TRUE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
            self.symbol_table.add_branch(token_line.value)
            self.symbol_table.insert(ImpTrue)
            return token_line, formula

        @self.pg.production('step : NUM DOT FALSE formula IMP_FALSE NUM')
        @self.pg.production('step : NUM DOT TRUE formula IMP_FALSE NUM')
        def Imp_false(p):
            token_line = p[0]
            token_true_value = p[2]
            token_formula = p[3]
            token_symbol_rule = p[4]
            token_reference1 = p[5]
            formula = token_formula[1] 
            
            impFalse = self.rule_factory.create_rule(RuleType.IMPLICATION_FALSE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
            self.symbol_table.insert(impFalse)
            return token_line, formula

        
        @self.pg.production('step : NUM DOT TRUE formula NEG_TRUE NUM')
        @self.pg.production('step : NUM DOT FALSE formula NEG_TRUE NUM')
        @self.pg.production('step : NUM DOT FALSE formula NEG_FALSE NUM')
        @self.pg.production('step : NUM DOT TRUE formula NEG_FALSE NUM')
        def Neg(p):
            token_line = p[0]
            token_true_value = p[2]
            token_formula = p[3]
            token_symbol_rule = p[4]
            token_reference1 = p[5]
            formula = token_formula[1] 
            
            negation = self.rule_factory.create_rule(RuleType.NEGATION_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
            self.symbol_table.insert(negation)
            if (token_true_value.gettokentype() == 'TRUE' and token_symbol_rule.gettokentype() == 'NEG_TRUE') or (token_true_value.gettokentype() == 'FALSE' and token_symbol_rule.gettokentype() == 'NEG_FALSE') :  
              self.has_error = True
              deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, negation))              
            return token_line, formula

        @self.pg.production('step : NUM DOT formula CLOSED NUM COMMA NUM')
        def Rule_closed(p):
            token_line = p[0]
            token_formula = p[2]
            token_reference1 = p[4]
            token_reference2 = p[6]
            formula = token_formula[1] 
            closed = ClosedRule(token_line, token_formula, token_reference1, token_reference2)
            self.symbol_table.insert(closed)
            return token_line, formula


        @self.pg.production('step : CLOSE_BRACKET')
        def close_box(p):
            token = p[0]
            rule = self.symbol_table.get_last_rule_from_branch()
            if rule is None:
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE, token, rule))              
                return p[0], rule
            elif(self.symbol_table.get_box_start()):
                self.symbol_table.end_branch(rule.line)
            else:
                self.has_error = True
                deduction_result.add_error(self.get_error(constants.CLOSE_BRACKET_WITHOUT_BOX, token, rule))
            return token, None


        @self.pg.production('step : NUM DOT FALSE formula ALL_TRUE NUM')
        @self.pg.production('step : NUM DOT TRUE formula ALL_TRUE NUM')
        def For_ALL_TRUE(p):
          token_line = p[0]
          token_true_value = p[2]
          token_formula = p[3]
          token_symbol_rule = p[4]
          token_reference1 = p[5]
          formula = token_formula[1] 
          
          forall = ForAllTrueRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
          self.symbol_table.insert(forall)
          if token_true_value.gettokentype() == 'FALSE':  
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, forall))              
          return token_line, formula

        @self.pg.production('step : NUM DOT TRUE formula EXT_FALSE NUM')
        @self.pg.production('step : NUM DOT FALSE formula EXT_FALSE NUM')
        def Exists_FALSE(p):
          token_line = p[0]
          token_true_value = p[2]
          token_formula = p[3]
          token_symbol_rule = p[4]
          token_reference1 = p[5]
          formula = token_formula[1] 
          
          exists = ExistsFalseRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
          self.symbol_table.insert(exists)
          if token_true_value.gettokentype() == 'TRUE':  
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, exists))              
          return token_line, formula

        @self.pg.production('step : NUM DOT TRUE formula ALL_FALSE NUM')
        @self.pg.production('step : NUM DOT FALSE formula ALL_FALSE NUM')
        def For_ALL_FALSE(p):
          token_line = p[0]
          token_true_value = p[2]
          token_formula = p[3]
          token_symbol_rule = p[4]
          token_reference1 = p[5]
          formula = token_formula[1] 
          
          forall = RuleFactory.RuleFactory.create_rule(RuleType.RuleType.FOR_ALL_FALSE_RULE, token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
          self.symbol_table.insert(forall)
          if token_true_value.gettokentype() == 'TRUE':  
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, forall))              
          return token_line, formula

        @self.pg.production('step : NUM DOT FALSE formula EXT_TRUE NUM')
        @self.pg.production('step : NUM DOT TRUE formula EXT_TRUE NUM')
        def Exists_TRUE(p):
          token_line = p[0]
          token_true_value = p[2]
          token_formula = p[3]
          token_symbol_rule = p[4]
          token_reference1 = p[5]
          formula = token_formula[1] 
          
          existsTrue = ExistsTrueRule(token_line, token_true_value, token_formula, token_symbol_rule, token_reference1)
          self.symbol_table.insert(existsTrue)
          if token_true_value.gettokentype() == 'FALSE':  
            self.has_error = True
            deduction_result.add_error(self.get_error(constants.WRONG_TRUE_VALUE, token_true_value, existsTrue))              
          return token_line, formula


        @self.pg.production('formula : EXT formula')
        @self.pg.production('formula : ALL formula')
        @self.pg.production('formula : formula OR formula')
        @self.pg.production('formula : formula AND formula')
        @self.pg.production('formula : formula IMPLIE formula')
        @self.pg.production('formula : NOT formula')
        @self.pg.production('formula : ATHOM OPEN_PAREN variableslist CLOSE_PAREN')
        @self.pg.production('formula : ATHOM')
        @self.pg.production('formula : BOTTOM')
        def formula(p):
            if len(p) < 3:
                if p[0].gettokentype() == 'ATHOM':
                    return p[0], AthomFormula(key=p[0].value)
                elif p[0].gettokentype() == 'BOTTOM':
                    return p[0], AthomFormula(key=p[0].value)
                elif p[0].gettokentype() == 'NOT':
                    result = p[1]
                    return p[0], NegationFormula(formula=result[1])  
                elif type(p[0]) is not tuple:
                  result1 = p[0]
                  result2 = p[1]
                  # Universal Formula
                  if p[0].gettokentype() == 'EXT':  
                    var = p[0].value.split('E')[1]
                    return p[0], ExistentialFormula(variable=var, formula=p[1][1])
                  elif p[0].gettokentype() == 'ALL':  
                    var = p[0].value.split('A')[1]
                    return p[0], UniversalFormula(variable=var, formula=p[1][1])
            elif len(p)==4:
              # Predicate Formula
              varlist = p[2]
              return p[0], PredicateFormula(name=p[0].value,variables=varlist[1])            
            elif len(p) == 3:
              # Binary Formula
              result1 = p[0]
              result2 = p[2]
              if(p[1].value=='&'):
                return result1[0], AndFormula(left=result1[1], right=result2[1])
              elif(p[1].value=='|'):
                return result1[0], OrFormula(left=result1[1], right=result2[1])
              elif(p[1].value=='->'):
                return result1[0], ImplicationFormula(left=result1[1], right=result2[1])
              else:
                return result1[0], BinaryFormula(key=p[1].value, left=result1[1], right=result2[1])


        @self.pg.production('variableslist : VAR')
        @self.pg.production('variableslist : VAR COMMA variableslist')
        def variablesList(p):
             if len(p) == 1:
                 return p[0], [p[0].value]
             else:
                result = p[2]
             return p[0], [p[0].value] + result[1]



        @self.pg.production('formula : OPEN_PAREN formula CLOSE_PAREN')
        def paren_formula(p):
            result = p[1]
            return p[0], result[1]

        @self.pg.error
        def error_handle(token):
            productions = self.state.splitlines()
            error = ''  

            if(productions == ['']):
                error = t('ERROR_NONE_PROOF_SUBMITTED')
            if token.gettokentype() == '$end':
                error = t('ERROR_DEFINITION_NOT_COMPLETED')
            else:
                source_position = token.getsourcepos()
                error = t('ERROR_DEFINITION_NOT_COMPLETED')
                error += t('ERROR_SINTAX_ERROR')
                error += productions[source_position.lineno - 1]
                string = '\n'
                for i in range(source_position.colno -1):
                    string += ' '
                string += '^'
                if token.gettokentype() == 'OUT':
                    string += t('ERROR_SYMBOL_NOT_IN_LANGUAGE')
                error += string
                
            raise ValueError("@@"+error)

    def get_error(self, type_error, token_error, rule):
        productions = self.state.splitlines()
        column_error = token_error.getsourcepos().colno
        erro = t('ERROR_SYNTAX_ERROR_IN_LINE').format(line=token_error.getsourcepos().lineno)
        erro += productions[token_error.getsourcepos().lineno-1] + "\n"
        for i in range(column_error-1):
            erro += ' '
        if type_error == constants.INVALID_INITIAL_TABLEAU:
            erro += t('ERROR_INVALID_INITIAL_TABLEAU')
        elif type_error == constants.INVALID_RESULT:
            erro += t('ERROR_INVALID_RESULT').format(formula=rule.formula.toString())
        elif type_error == constants.UNEXPECT_RESULT:
            erro += t('ERROR_UNEXPECT_RESULT').format(formula=rule.formula.toString())
        elif type_error == constants.IS_NOT_DISJUNCTION_FALSE:
            erro += t('ERROR_IS_NOT_DISJUNCTION_FALSE').format(line=token_error.value)
        elif type_error == constants.IS_NOT_DISJUNCTION_TRUE:
            erro += t('ERROR_IS_NOT_DISJUNCTION_TRUE').format(line=token_error.value)
        elif type_error == constants.IS_NOT_CONJUNCTION_FALSE:
            erro += t('ERROR_IS_NOT_CONJUNCTION_FALSE').format(line=token_error.value)
        elif type_error == constants.IS_NOT_CONJUNCTION_TRUE:
            erro += t('ERROR_IS_NOT_CONJUNCTION_TRUE').format(line=token_error.value)
        elif type_error == constants.IS_NOT_NEGATION_FALSE:
            erro += t('ERROR_IS_NOT_NEGATION_FALSE').format(line=token_error.value)
        elif type_error == constants.IS_NOT_NEGATION_TRUE:
            erro += t('ERROR_IS_NOT_NEGATION_TRUE').format(line=token_error.value)
        elif type_error == constants.IS_NOT_IMPLICATION:
            erro += t('ERROR_IS_NOT_IMPLICATION').format(line=token_error.value)
        elif type_error == constants.INVALID_NEGATION:
            erro += t('ERROR_INVALID_NEGATION')
        elif type_error == constants.INVALID_LEFT_IMPLICATION:
            erro += t('ERROR_INVALID_LEFT_IMPLICATION').format(formula=rule.formula.toString())
        elif type_error == constants.INVALID_RIGHT_IMPLICATION:
            erro += t('ERROR_INVALID_RIGHT_IMPLICATION').format(formula=rule.formula.toString())
        elif type_error == constants.INVALID_LEFT_RIGHT_IMPLICATION:
            erro += t('ERROR_INVALID_LEFT_RIGHT_IMPLICATION').format(formula=rule.formula.toString())
        elif type_error == constants.INVALID_LEFT_CONJUNCTION:
            erro += t('ERROR_INVALID_LEFT_CONJUNCTION')
        elif type_error == constants.INVALID_RIGHT_CONJUNCTION:
            erro += t('ERROR_INVALID_RIGHT_CONJUNCTION')
        elif type_error == constants.INVALID_LEFT_OR_RIGHT_DISJUNCTION:
            erro += t('ERROR_INVALID_LEFT_OR_RIGHT_DISJUNCTION').format(line=token_error.value)
        elif type_error == constants.INVALID_LEFT_OR_RIGHT_CONJUNCTION:
            erro += t('ERROR_INVALID_LEFT_OR_RIGHT_CONJUNCTION').format(formula=rule.formula.toString(), line=token_error.value)
        elif type_error == constants.USING_DESCARTED_RULE:
            erro += t('ERROR_USING_DESCARTED_RULE').format(line=token_error.value)
        elif type_error == constants.REFERENCED_LINE_NOT_DEFINED:
            erro += t('ERROR_REFERENCED_LINE_NOT_DEFINED').format(line=token_error.value)
        elif type_error == constants.CLOSE_BRACKET_WITHOUT_BOX:
            erro += t('ERROR_CLOSE_BRACKET_WITHOUT_BOX')
        elif type_error == constants.BOX_MUST_BE_DISPOSED:
            erro += t('ERROR_BOX_MUST_BE_DISPOSED')
        elif type_error == constants.BOX_MUST_BE_DISPOSED_BY_RULE:
            erro += t('ERROR_BOX_MUST_BE_DISPOSED_BY_RULE')
        elif type_error == constants.INVALID_SUBSTITUTION_UNIVERSAL:
            erro += t('ERROR_INVALID_SUBSTITUTION_UNIVERSAL').format(formula=rule.formula.toString(), line=rule.reference1)
        elif type_error == constants.INVALID_UNIVERSAL_FORMULA:
            erro += t('ERROR_INVALID_UNIVERSAL_FORMULA').format(line=rule.reference1, value=rule.true_value)
        elif type_error == constants.INVALID_EXISTENCIAL_FORMULA:
            erro += t('ERROR_INVALID_EXISTENCIAL_FORMULA').format(line=rule.reference1, value=rule.true_value)
        elif type_error == constants.INVALID_SUBSTITUTION_EXISTENCIAL:
            erro += t('ERROR_INVALID_SUBSTITUTION_EXISTENCIAL').format(formula=rule.formula.toString(), line=rule.reference1)
        elif type_error == constants.VARIABLE_IS_NOT_FRESH_VARIABLE:
            erro += t('ERROR_VARIABLE_IS_NOT_FRESH_VARIABLE').format(formula=rule.formula.toString())
        elif type_error == constants.INVALID_TRUE_CONJUNCTION_NEXT:
            erro += t('ERROR_INVALID_TRUE_CONJUNCTION_NEXT').format(formula=rule.formula.right.toString())
        elif type_error == constants.INVALID_TRUE_CONJUNCTION_PREVIOUS:
            erro += t('ERROR_INVALID_TRUE_CONJUNCTION_PREVIOUS').format(formula=rule.formula.left.toString())
        elif type_error == constants.INVALID_FALSE_DISJUNCTION_NEXT:
            erro += t('ERROR_INVALID_FALSE_DISJUNCTION_NEXT').format(formula=rule.formula.right.toString())
        elif type_error == constants.INVALID_FALSE_DISJUNCTION_PREVIOUS:
            erro += t('ERROR_INVALID_FALSE_DISJUNCTION_PREVIOUS').format(formula=rule.formula.left.toString())
        elif type_error == constants.INVALID_FALSE_IMPLICATION_NEXT:
            erro += t('ERROR_INVALID_FALSE_IMPLICATION_NEXT').format(formula=rule.formula.right.toString())
        elif type_error == constants.INVALID_FALSE_IMPLICATION_PREVIOUS:
            erro += t('ERROR_INVALID_FALSE_IMPLICATION_PREVIOUS').format(formula=rule.formula.left.toString())
        elif type_error == constants.INVALID_TRUE_DISJUNCTION_NEXT:
            erro += t('ERROR_INVALID_TRUE_DISJUNCTION_NEXT').format(formula=rule.formula.right.toString())
        elif type_error == constants.INVALID_TRUE_DISJUNCTION_PREVIOUS:
            erro += t('ERROR_INVALID_TRUE_DISJUNCTION_PREVIOUS').format(formula=rule.formula.left.toString())
        elif type_error == constants.INVALID_TRUE_IMPLICATION_NEXT:
            erro += t('ERROR_INVALID_TRUE_IMPLICATION_NEXT').format(formula=rule.formula.right.toString())
        elif type_error == constants.INVALID_TRUE_IMPLICATION_PREVIOUS:
            erro += t('ERROR_INVALID_TRUE_IMPLICATION_PREVIOUS').format(formula=rule.formula.left.toString())
        elif type_error == constants.INVALID_FALSE_CONJUNCTION_NEXT:
            erro += t('ERROR_INVALID_FALSE_CONJUNCTION_NEXT').format(formula=rule.formula.right.toString())
        elif type_error == constants.INVALID_FALSE_CONJUNCTION_PREVIOUS:
            erro += t('ERROR_INVALID_FALSE_CONJUNCTION_PREVIOUS').format(formula=rule.formula.left.toString())
        elif type_error == constants.INVALID_BETA_RULE:
            erro += t('ERROR_INVALID_BETA_RULE')
        elif type_error == constants.ALREADY_USED_RULE_IN_BRANCH:
            erro += t('ERROR_ALREADY_USED_RULE_IN_BRANCH').format(line=rule.line)
        elif type_error == constants.PREMISSE_SHOULD_BE_TRUE:
            erro += t('ERROR_PREMISSE_SHOULD_BE_TRUE')
        elif type_error == constants.CONCLUSION_SHOULD_BE_FALSE:
            erro += t('ERROR_CONCLUSION_SHOULD_BE_FALSE')
        elif type_error == constants.RULE_CANNOT_BE_APPLIED:
            erro += t('ERROR_RULE_CANNOT_BE_APPLIED')
        elif type_error == constants.RULE_MUST_BE_BETA:
            erro += t('ERROR_RULE_MUST_BE_BETA')
        elif type_error == constants.RULE_MUST_BE_ALPHA:
            erro += t('ERROR_RULE_MUST_BE_ALPHA')
        elif type_error == constants.WRONG_TRUE_VALUE:
            if rule.token_true_value.gettokentype() == 'FALSE':  
              erro += t('ERROR_WRONG_TRUE_VALUE_SHOULD_BE_T')
            else:
              erro += t('ERROR_WRONG_TRUE_VALUE_SHOULD_BE_F')

        return erro
    
    def get_parser(self):
        return self.pg.build()

    @staticmethod
    def getProof(input_proof=''):
      lexer = Lexer().get_lexer()
      tokens = lexer.lex(input_proof)

      pg = ParserAnita(state=input_proof)
      pg.parse()
      parser = pg.get_parser()
      result = parser.parse(tokens)
      return result


    @staticmethod
    def toString(premisses,conclusion,parentheses=False):
      if (premisses==[]):
        return '|- '+conclusion.toString(parentheses=parentheses)
      else:
        return ", ".join(f.toString(parentheses=parentheses) for f in premisses)+' |- '+conclusion.toString(parentheses=parentheses)

    @staticmethod
    def toLatex(premisses,conclusion,parentheses=False):
      if (premisses==[]):
        return '\\vdash '+conclusion.toLatex(parentheses=parentheses)
      else:
        return ", ".join(f.toLatex(parentheses=parentheses) for f in premisses) +' \\vdash '+conclusion.toLatex(parentheses=parentheses)




def check_proof(input_proof, input_theorem=None, display_theorem=True, display_countermodel=True, display_latex=True):
  try:
      result = ParserAnita.getProof(input_proof)
      r = ''
      if(result.errors==[]):
        set_premisses = set()
        conclusion = None
        s_theorem = ParserAnita.toString(result.premisses, result.conclusion)
        set_premisses_result = set([p.toString() for p in result.premisses])

        if input_theorem is not None: 
          premisses, conclusion = ParserTheorem.getTheorem(input_theorem)
          if conclusion is None:
            return t('CHECK_PROOF_NOT_VALID_THEOREM_INPUT').format(theorem=input_theorem)
          set_premisses = set([p.toString() for p in premisses])

        if(result.is_closed):
          if(conclusion is None or (conclusion==result.conclusion and set_premisses==set_premisses_result)):
            r += t('CHECK_PROOF_VALID')
            if display_theorem:
              r += "\n"+s_theorem
          else:
            r += t('CHECK_PROOF_WRONG_THEOREM').format(proof_theorem=s_theorem, input_theorem=input_theorem)

          if display_latex: 
            r += "\n"+t('CHECK_PROOF_LATEX')+"\n"+str(result.latex)
            r += "\n"+t('CHECK_PROOF_COLORED_LATEX')+"\n"+str(result.colored_latex)
        else:
            if result.saturared_branches != []:
              if(conclusion is None or (conclusion==result.conclusion and set_premisses==set_premisses_result)):
                r += t('CHECK_PROOF_NOT_VALID_THEOREM')
                if display_theorem:
                  r += "\n"+result.theorem 
              if display_countermodel:
                r += "\n"+t('CHECK_PROOF_COUNTERMODELS')
                for s_v in result.counter_examples:
                    r += '\n  '+s_v
              if display_latex: 
                r += "\n"+t('CHECK_PROOF_LATEX')+"\n"+t('CHECK_PROOF_LATEX_THEOREM_NOT_VALID').format(theorem=result.latex_theorem)
                if display_countermodel:
                  r += "\n"+t('CHECK_PROOF_COUNTERMODELS')
                  r += "\n\\begin{itemize}"
                  for s_v in result.counter_examples:
                      r += '\n  \item $'+s_v+'$'
                  r += "\n\end{itemize}"
                r += "\n"+str(result.colored_latex)
            else: 
                r += t('CHECK_PROOF_NOT_COMPLETE')
                if display_theorem:
                  r += result.theorem
                r += "\n"+t('CHECK_PROOF_BRANCHES_NOT_SATURATED')
                for rules in result.open_branches:
                  r += "\n"+t('CHECK_PROOF_BRANCH')+"\n  "
                  r += '\n  '.join([r.toString() for r in reversed(rules)])
                if display_latex: 
                  r += "\n"+t('CHECK_PROOF_LATEX')+"\n"+str(result.latex)
                  r += "\n"+t('CHECK_PROOF_COLORED_LATEX')+"\n"+str(result.colored_latex)
      else:
        r += t('CHECK_PROOF_ERRORS_FOUND')+"\n"
        for error in result.errors:
          r += '\n'+str(error)
      return r
  except ValueError:
      s = traceback.format_exc()
      result = (s.split("@@"))[-1]
      r = t('CHECK_PROOF_ERRORS_FOUND')+"\n\n"
      r += result
      return r
  else:
    pass

    
# PARSER DE UM TEOREMA

class ParserTheorem():
    def __init__(self, state):
        self.state = state
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['COMMA', 'OPEN_PAREN', 'CLOSE_PAREN', 'NOT',
             'AND', 'OR',  'BOTTOM','ATHOM', 'IMPLIE', 'IFF',
             'VAR','EXT','ALL', 'V_DASH' ],
            #The precedence $\lnot,\forall,\exists,\land,\lor,\rightarrow,\leftrightarrow$
            precedence=[
                ('right', ['IFF']),
                ('right', ['IMPLIE']),
                ('right', ['OR']),
                ('right', ['AND']),
                ('right', ['EXT']),
                ('right', ['ALL']),
                ('right', ['NOT']),
            ]
        )

    def parse(self):
        @self.pg.production('program : formulaslist V_DASH formula')
        @self.pg.production('program : V_DASH formula')
        def program(p):
            if len(p) == 2:
              return [], p[1][1]
            else:
              return p[0][1], p[2][1]

        @self.pg.production('formula : EXT formula')
        @self.pg.production('formula : ALL formula')
        @self.pg.production('formula : formula OR formula')
        @self.pg.production('formula : formula AND formula')
        @self.pg.production('formula : formula IMPLIE formula')
        @self.pg.production('formula : formula IFF formula')
        @self.pg.production('formula : NOT formula')
        @self.pg.production('formula : ATHOM OPEN_PAREN variableslist CLOSE_PAREN')
        @self.pg.production('formula : ATHOM')
        @self.pg.production('formula : BOTTOM')
        def formula(p):
            if len(p) < 3:
                if p[0].gettokentype() == 'ATHOM':
                    return p[0], AthomFormula(key=p[0].value)
                elif p[0].gettokentype() == 'BOTTOM':
                    return p[0], AthomFormula(key=p[0].value)
                elif p[0].gettokentype() == 'NOT':
                    result = p[1]
                    return p[0], NegationFormula(formula=result[1])  
                elif type(p[0]) is not tuple:
                  result1 = p[0]
                  result2 = p[1]
                  # Universal Formula
                  if p[0].gettokentype() == 'EXT':  
                    var = p[0].value.split('E')[1]
                    return p[0], ExistentialFormula(variable=var, formula=p[1][1])
                  elif p[0].gettokentype() == 'ALL':  
                    var = p[0].value.split('A')[1]
                    return p[0], UniversalFormula(variable=var, formula=p[1][1])
            elif len(p)==4:
              # Predicate Formula
              varlist = p[2]
              return p[0], PredicateFormula(name=p[0].value,variables=varlist[1])            
            elif len(p) == 3:
              # Binary Formula
              result1 = p[0]
              result2 = p[2]
              if(p[1].value=='&'):
                return result1[0], AndFormula(left=result1[1], right=result2[1])
              elif(p[1].value=='|'):
                return result1[0], OrFormula(left=result1[1], right=result2[1])
              elif(p[1].value=='->'):
                return result1[0], ImplicationFormula(left=result1[1], right=result2[1])
              elif(p[1].value=='<->'):
                return result1[0], BiImplicationFormula(left=result1[1], right=result2[1])
              else:
                return result1[0], BinaryFormula(key=p[1].value, left=result1[1], right=result2[1])

        @self.pg.production('formula : OPEN_PAREN formula CLOSE_PAREN')
        def paren_formula(p):
            result = p[1]
            return p[0], result[1]

        @self.pg.production('variableslist : VAR')
        @self.pg.production('variableslist : VAR COMMA variableslist')
        def variablesList(p):
             if len(p) == 1:
                 return p[0], [p[0].value]
             else:
                result = p[2]
             return p[0], [p[0].value] + result[1]

        @self.pg.production('formulaslist : formula')
        @self.pg.production('formulaslist : formula COMMA formulaslist')
        def formulasList(p):
             if len(p) == 1:
                 return p[0], [p[0][1]]
             else:
                result = p[2]
             return p[0], [p[0][1]] + result[1]


        @self.pg.error
        def error_handle(token):
            productions = self.state.splitlines()
            error = ''  

            if(productions == ['']):
                error = t('ERROR_NONE_FORMULA_SUBMITTED')
            if token.gettokentype() == '$end':
                error = t('ERROR_NONE_FORMULA_SUBMITTED')
            else:
                source_position = token.getsourcepos()
                error = t('ERROR_THEOREM_DEFINITION_NOT_CORRECT')
                error += t('ERROR_SINTAX_ERROR')
                error += productions[source_position.lineno - 1]
                string = '\n'
                for i in range(source_position.colno -1):
                    string += ' '
                string += '^'
                if token.gettokentype() == 'OUT':
                    string += t('ERROR_SYMBOL_NOT_BELONG_LANGUAGE')
                error += string
                
            raise ValueError("@@"+error)

    def get_error(self, type_error, token_error, rule):
        productions = self.state.splitlines()
        column_error = token_error.getsourcepos().colno
        erro = t('ERROR_SYNTAX_ERROR_IN_LINE').format(line=token_error.getsourcepos().lineno)
        erro += productions[token_error.getsourcepos().lineno-1] + "\n"
        for i in range(column_error-1):
            erro += ' '
        
        return erro
    
    def get_parser(self):
        return self.pg.build()
    
    @staticmethod
    def getTheorem(input_text=''):
        try:
          lexer = Lexer().get_lexer()
          tokens = lexer.lex(input_text)
          pg = ParserTheorem(state=input_text)
          pg.parse()
          parser = pg.get_parser()
          formulas, conclusion = parser.parse(tokens)
          return formulas, conclusion
        except ValueError:
            return [], None
        else:
            return [], None
            pass

    @staticmethod
    def toString(premisses,conclusion,parentheses=False):
      if (premisses==[]):
        return '|- '+conclusion.toString(parentheses=parentheses)
      else:
        return ", ".join(f.toString(parentheses=parentheses) for f in premisses)+' |- '+conclusion.toString(parentheses=parentheses)

    @staticmethod
    def toLatex(premisses,conclusion,parentheses=False):
      if (premisses==[]):
        return '\\vdash '+conclusion.toLatex(parentheses=parentheses)
      else:
        return ", ".join(f.toLatex(parentheses=parentheses) for f in premisses) +' \\vdash '+conclusion.toLatex(parentheses=parentheses)



# PARSER DE UMA Fórmula

class ParserFormula():
    def __init__(self, state):
        self.state = state
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['COMMA', 'OPEN_PAREN', 'CLOSE_PAREN', 'NOT',
             'AND', 'OR',  'BOTTOM','ATHOM', 'IMPLIE', 'IFF',
             'VAR','EXT','ALL' ],
            #The precedence $\lnot,\forall,\exists,\land,\lor,\rightarrow,\leftrightarrow$
            precedence=[
                ('right', ['IFF']),
                ('right', ['IMPLIE']),
                ('right', ['OR']),
                ('right', ['AND']),
                ('right', ['EXT']),
                ('right', ['ALL']),
                ('right', ['NOT']),
            ]
        )

    def parse(self):
        @self.pg.production('program : formula')
        def program(p):
            return p[0][1]

        @self.pg.production('formula : EXT formula')
        @self.pg.production('formula : ALL formula')
        @self.pg.production('formula : formula OR formula')
        @self.pg.production('formula : formula AND formula')
        @self.pg.production('formula : formula IMPLIE formula')
        @self.pg.production('formula : formula IFF formula')
        @self.pg.production('formula : NOT formula')
        @self.pg.production('formula : ATHOM OPEN_PAREN variableslist CLOSE_PAREN')
        @self.pg.production('formula : ATHOM')
        @self.pg.production('formula : BOTTOM')
        def formula(p):
            if len(p) < 3:
                if p[0].gettokentype() == 'ATHOM':
                    return p[0], AthomFormula(key=p[0].value)
                elif p[0].gettokentype() == 'BOTTOM':
                    return p[0], AthomFormula(key=p[0].value)
                elif p[0].gettokentype() == 'NOT':
                    result = p[1]
                    return p[0], NegationFormula(formula=result[1])  
                elif type(p[0]) is not tuple:
                  result1 = p[0]
                  result2 = p[1]
                  # Universal Formula
                  if p[0].gettokentype() == 'EXT':  
                    var = p[0].value.split('E')[1]
                    return p[0], ExistentialFormula(variable=var, formula=p[1][1])
                  elif p[0].gettokentype() == 'ALL':  
                    var = p[0].value.split('A')[1]
                    return p[0], UniversalFormula(variable=var, formula=p[1][1])
            elif len(p)==4:
              # Predicate Formula
              varlist = p[2]
              return p[0], PredicateFormula(name=p[0].value,variables=varlist[1])            
            elif len(p) == 3:
              # Binary Formula
              result1 = p[0]
              result2 = p[2]
              if(p[1].value=='&'):
                return result1[0], AndFormula(left=result1[1], right=result2[1])
              elif(p[1].value=='|'):
                return result1[0], OrFormula(left=result1[1], right=result2[1])
              elif(p[1].value=='->'):
                return result1[0], ImplicationFormula(left=result1[1], right=result2[1])
              elif(p[1].value=='<->'):
                return result1[0], BiImplicationFormula(left=result1[1], right=result2[1])
              else:
                return result1[0], BinaryFormula(key=p[1].value, left=result1[1], right=result2[1])

        @self.pg.production('formula : OPEN_PAREN formula CLOSE_PAREN')
        def paren_formula(p):
            result = p[1]
            return p[0], result[1]

        @self.pg.production('variableslist : VAR')
        @self.pg.production('variableslist : VAR COMMA variableslist')
        def variablesList(p):
             if len(p) == 1:
                 return p[0], [p[0].value]
             else:
                result = p[2]
             return p[0], [p[0].value] + result[1]


        @self.pg.error
        def error_handle(token):
            productions = self.state.splitlines()
            error = ''  

            if(productions == ['']):
                error = t('ERROR_NONE_FORMULA_SUBMITTED')
            if token.gettokentype() == '$end':
                error = t('ERROR_NONE_FORMULA_SUBMITTED')
            else:
                source_position = token.getsourcepos()
                error = t('ERROR_FORMULA_DEFINITION_NOT_CORRECT')
                error += t('ERROR_SINTAX_ERROR')
                error += productions[source_position.lineno - 1]
                string = '\n'
                for i in range(source_position.colno -1):
                    string += ' '
                string += '^'
                if token.gettokentype() == 'OUT':
                    string += t('ERROR_SYMBOL_NOT_BELONG_LANGUAGE')
                error += string
                
            raise ValueError("@@"+error)

    def get_error(self, type_error, token_error, rule):
        productions = self.state.splitlines()
        column_error = token_error.getsourcepos().colno
        erro = t('ERROR_SYNTAX_ERROR_IN_LINE').format(line=token_error.getsourcepos().lineno)
        erro += productions[token_error.getsourcepos().lineno-1] + "\n"
        for i in range(column_error-1):
            erro += ' '
        
        return erro
    
    def get_parser(self):
        return self.pg.build()
    @staticmethod
    def getFormula(input_text=''):
        try:
          lexer = Lexer().get_lexer()
          tokens = lexer.lex(input_text)

          pg = ParserFormula(state=input_text)
          pg.parse()
          parser = pg.get_parser()
          result = parser.parse(tokens)
          return result
        except ValueError:
            return None
        else:
            return None
            pass