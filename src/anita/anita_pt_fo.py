import traceback
from rply import ParserGenerator
from rply import Token
import sys

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
from anita.formula.quantifier_formula.QuantifierFormula import QuantifierFormula
from anita.formula.quantifier_formula.UniversalFormula import UniversalFormula
from anita.formula.quantifier_formula.ExistentialFormula import ExistentialFormula
from anita.lexer.lexer import Lexer
from anita.constants.constants import constants
from anita.utils.tableau_deduction_return import tableau_deduction_return

## File symbol_table.py

class SymbolTable:
    def __init__(self):
        self.symbol_table = {
            'branch_0': {
                'name': 'branch_0',
                'parent': None,
                'children': [],
                'rules': [],
                'variable': None,
                'start_line': '1',
                'end_line': None
            }
        }
        self.current_branch = 'branch_0'

    def insert(self, rule):
        self.symbol_table[self.current_branch]['rules'].append(rule)

    def start_branch(self, branch):
        self.current_branch = branch

    def end_branch(self, end_line):
        self.symbol_table[self.current_branch]['end_line'] = end_line
        if(self.symbol_table[self.current_branch]['parent'] is not None):
            self.current_branch = self.symbol_table[self.current_branch]['parent']

    def add_branch(self, start_line, variable=None):
        branch = 'branch_{}'.format(len(self.symbol_table))
        self.symbol_table[branch] = {
            'name': branch,
            'parent': self.current_branch,
            'children': [],
            'rules': [],
            'variable': variable,
            'start_line': start_line,
            'end_line': None 
            }
        self.symbol_table[self.current_branch]['children'].append(self.symbol_table[branch])
        self.start_branch(branch)

    def branch_to_latex(self, branch, rules=[], color='red'):
      i = 0
      l = []
      initial_tableau = '[.{'
      n_rules = len(branch['rules']) 
      while i< n_rules:
        if isinstance(branch['rules'][i],PremisseRule):
          if (branch['rules'][i] in rules):
            initial_tableau += '\color{'+color+'}{$'+branch['rules'][i].toLatex(self)+'$} \\\\ '
          else:
            initial_tableau += '$'+branch['rules'][i].toLatex(self)+'$ \\\\ '
        elif isinstance(branch['rules'][i],ConclusionRule):
          if (branch['rules'][i] in rules):
            initial_tableau += '\color{'+color+'}{$'+branch['rules'][i].toLatex(self)+'$}}'
          else:
            initial_tableau += '$'+branch['rules'][i].toLatex(self)+'$}'
          l.append(initial_tableau)
        elif isinstance(branch['rules'][i],AndTrueRule):
          if (branch['rules'][i] in rules):
            s = '[.{{\color{'+color+'}$'+branch['rules'][i].toLatex(self)+'$}'
          else:
            s = '[.{$'+branch['rules'][i].toLatex(self)+'$'
          if i+1< n_rules and isinstance(branch['rules'][i+1],AndTrueRule) and branch['rules'][i].reference1==branch['rules'][i+1].reference1:            
            if (branch['rules'][i+1] in rules):
              s+=' \\\\ {\color{'+color+'}$'+branch['rules'][i+1].toLatex(self)+'$}'
            else:  
              s+=' \\\\ '+'$'+branch['rules'][i+1].toLatex(self)+'$'
            i+=1
          l.append(s+'}')
        elif isinstance(branch['rules'][i],OrFalseRule):
          if (branch['rules'][i] in rules):
            s = '[.{{\color{'+color+'}$'+branch['rules'][i].toLatex(self)+'$}'
          else:
            s = '[.{$'+branch['rules'][i].toLatex(self)+'$'
          if i+1< n_rules and isinstance(branch['rules'][i+1],OrFalseRule) and branch['rules'][i].reference1==branch['rules'][i+1].reference1:            
            if (branch['rules'][i+1] in rules):
              s+=' \\\\ {\color{'+color+'}$'+branch['rules'][i+1].toLatex(self)+'$}'
            else:  
              s+=' \\\\ '+'$'+branch['rules'][i+1].toLatex(self)+'$'
            i+=1
          l.append(s+'}')
        elif isinstance(branch['rules'][i],ImpFalseRule):
          if (branch['rules'][i] in rules):
            s = '[.{{\color{'+color+'}$'+branch['rules'][i].toLatex(self)+'$}'
          else:
            s = '[.{$'+branch['rules'][i].toLatex(self)+'$'
          if i+1< n_rules and isinstance(branch['rules'][i+1],ImpFalseRule) and branch['rules'][i].reference1==branch['rules'][i+1].reference1:            
            if (branch['rules'][i+1] in rules):
              s+=' \\\\ {\color{'+color+'}$'+branch['rules'][i+1].toLatex(self)+'$}'
            else:  
              s+=' \\\\ '+'$'+branch['rules'][i+1].toLatex(self)+'$'
            i+=1
          l.append(s+'}')
        else:
          if (branch['rules'][i] in rules):
            l.append('[.{\color{'+color+'}{$'+branch['rules'][i].toLatex(self)+'$}}') 

          else:
            l.append('[.{$'+branch['rules'][i].toLatex(self)+'$}') 
        i+=1
      s = ' '.join(l)
      for s_children in branch['children']:
        s+= ' '+self.branch_to_latex(s_children,rules=rules,color=color)
      s += ''.join([' ]' for r in range(len(l))])
      return s
    
    def toLatex(self, rules=[], color='red'):
      return '\Tree '+self.branch_to_latex(self.symbol_table['branch_0'],rules,color)

    def toString(self):
      for i in range(len(self.symbol_table)):
        print(self.symbol_table['branch_{}'.format(i)])

    def len_symbol_table(self):
      r = 0
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['branch_{}'.format(i)]['rules']:
          r+=1
      return r

    def find_token(self, line):
      for i in range(len(self.symbol_table)):
        for j in range(len(self.symbol_table['branch_{}'.format(i)]['rules'])):
          if (self.symbol_table['branch_{}'.format(i)]['rules'][j].line==line):
            return self.symbol_table['branch_{}'.format(i)]['rules'][j].line
      return None

    def find_branch(self, line):
        for key, branch in self.symbol_table.items():
            for rule in branch['rules']:
                if rule and (rule.line == line):
                    return key 
        #Verifica se a linha não tem fórmula (introdução do universal)
        for key, branch in self.symbol_table.items():
          if(int(branch['start_line'])==int(line)):
            return key
        return None

    def lookup_formula_by_line(self, rule_line, line):
    # Returns only if the line is visible
        branch = self.find_branch(rule_line)
        while branch is not None:
            for rule in self.symbol_table[branch]['rules']:
                if rule.line == line:
                    return rule.formula
            branch = self.symbol_table[branch]['parent']
        return None

    def lookup_true_value_by_line(self, rule_line, line):
    # Returns only if the line is visible
        branch = self.find_branch(rule_line)
        while branch is not None:
            for rule in self.symbol_table[branch]['rules']:
                if rule.line == line:
                  if (isinstance(rule,ClosedRule)):
                    return None
                  else:
                    return rule.true_value
            branch = self.symbol_table[branch]['parent']
        return None        

    def check_branch_delimiter(self, line1, line2):
        for key, branch in self.symbol_table.items():
            if key != 'branch_0':
                if(branch['start_line'] == line1 and branch['end_line'] == line2):
                    start_rule = branch['rules'][0].formula if branch['rules'][0] is not None else None
                    end_rule = branch['rules'][-1].formula if branch['rules'][-1] is not None else None
                    return (start_rule, end_rule)
        return None, None

    def get_box_start(self):
        if self.current_branch != 'branch_0':
            return self.symbol_table[self.current_branch]['start_line']
        return None

    def get_box_end(self):
        if self.current_branch != 'branch_0':
            return self.symbol_table[self.current_branch]['end_line']
        return None               

    def get_last_rule_from_branch(self):
        if self.symbol_table[self.current_branch]['rules']==[]: 
          return None
        return self.symbol_table[self.current_branch]['rules'][-1]

    def get_rule(self, rule_line):
      for i in range(len(self.symbol_table)):
        for j in range(len(self.symbol_table['branch_{}'.format(i)]['rules'])):
          if (self.symbol_table['branch_{}'.format(i)]['rules'][j].line==rule_line):
            return self.symbol_table['branch_{}'.format(i)]['rules'][j]
      return None

    def check_is_visible(self, formula1_line, formula2_line):
      #Find formula1_line branch.
      if (int(formula1_line) <= int(formula2_line)): 
        return False
      current_branch = None
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['branch_{}'.format(i)]['rules']:
          if rule and (rule.line == formula1_line):
            current_branch = self.symbol_table['branch_{}'.format(i)]
            break
        if current_branch is not None: 
          break
      #Check if formula2_line in formula1_line branch 
      while current_branch is not None:
        for rule in current_branch['rules']:
          if rule and (rule.line == formula2_line):
            return True
        current_branch = self.symbol_table[current_branch['parent']] if 'parent' in current_branch else None
      return False


    # Returns True if the variable of the line is a fresh variable, i.e., it did not occur before this branch. 
    def is_fresh_variable(self, line, variable):
      return variable not in self.get_free_variables_before_branch(line)

    def get_free_variables_before_branch(self, line):
      free_variables = set()
      #Find formula1_line branch.
      branch = self.find_branch(line)
      while branch is not None:
          for rule in self.symbol_table[branch]['rules']:
            if (int(rule.line) < int(line)):
              free_variables = free_variables.union(rule.formula.free_variables())
            #Adds the variable for the universal introduction rule, i.e., if the line does not have a formula
            if (int(self.symbol_table[branch]['start_line'])<int(line) and self.symbol_table[branch]['variable']):
              free_variables = free_variables.union(set(self.symbol_table[branch]['variable']))
          branch = self.symbol_table[branch]['parent']
      return free_variables
      
    def get_branch_rules(self, line):
      rules = []
      current_branch = self.find_branch(line)
      while current_branch is not None:
        aux_rules = []
        for rule in self.symbol_table[current_branch]['rules']:
          if rule and (int(rule.line) <= int(line)):
            aux_rules.append(rule)
        aux_rules.reverse()        
        rules =  rules + aux_rules
        current_branch = self.symbol_table[current_branch]['parent']# if self.symbol_table[current_branch] else None
      return rules

    def count_used_rule_in_the_branch(self, rule):
      rules = self.get_branch_rules(rule.line)
      i = 0
      for r in rules:
        if hasattr(rule, 'reference1') and hasattr(r, 'reference1'):
          if(rule.reference1==r.reference1):
            i+= 1
      return i

    def branch_not_used_rules(self, rules):
      not_used_rules = []
      for rule in rules:
        if(not (isinstance(rule, ClosedRule) or isinstance(rule.formula,AthomFormula) or isinstance(rule.formula,PredicateFormula))):
          rule_used = False
          for rule_reference in rules:
            # Se a regra não for uma premissa, conclusão ou um átomo
            if(not (isinstance(rule_reference, PremisseRule) or isinstance(rule_reference, ConclusionRule)) ):
              if(rule_reference.reference1== rule.line):
                rule_used = True
                break
              if(isinstance(rule_reference, ClosedRule)):
                if(rule_reference.reference2== rule.line):
                  rule_used = True
                  break
          if(not rule_used):
            not_used_rules.append(rule)
      return not_used_rules

    def branch_has_contradiction(self, rules):
      for rule in rules:
        for rule_aux in rules:
          if(rule.formula==rule_aux.formula and rule.true_value!=rule_aux.true_value):
            return True
      return False

    def branch_is_saturaded(self,rules):
      return self.branch_not_used_rules(rules)==[]

    def get_open_tableau_branches(self):
      open = []
      for branch in self.get_last_branch_branchs():
        if(not isinstance(branch['rules'][-1], ClosedRule)): 
          open.append(branch)
      return open

    def get_closed_rule_branches(self):
      closed = []
      for branch in self.get_last_branch_branchs():
        if(isinstance(branch['rules'][-1], ClosedRule)): 
          closed.append(branch['rules'][-1])
      return closed

    def get_reference_closed_rule(self):
      reference_rules = []
      closed_rules = self.get_closed_rule_branches()
      for c in closed_rules:
        r1 = self.get_rule(c.reference1)
        r2 = self.get_rule(c.reference2)
        if r1 not in reference_rules:
          reference_rules.append(r1)
        if r2 not in reference_rules:
          reference_rules.append(r2)
      return reference_rules


    def get_open_saturated_branches(self):
      saturated_branches = []
      nonsaturated_branches = []
      branchs = self.get_open_tableau_branches()
      for branch in branchs:
        rules = self.get_branch_rules(branch['rules'][-1].line)
        # Test if a first-order branch
        is_first_order = False
        for r in rules:
          if(r.formula.is_first_order_formula()):
            is_first_order = True
            break
        if is_first_order:
          nonsaturated_branches.append(rules)
        elif self.branch_is_saturaded(rules) and not self.branch_has_contradiction(rules):
          saturated_branches.append(rules)
        else:
          nonsaturated_branches.append(rules)
      return saturated_branches, nonsaturated_branches

    def truth_values_toString(self,v):
      v.keys()
      return ''.join(v)

    def get_truth_values(self, saturated_branch):
      v = {}
      for rule in saturated_branch:
        if(isinstance(rule.formula, AthomFormula)):
          v[rule.formula.toString()] = rule.true_value
      return v

    def get_counter_examples_toString(self):
      return [self.counter_example_toString(v) for v in self.get_counter_examples()]
    
    def counter_example_toString(self, v):
      return ', '.join(['v('+key+')='+v[key] for key in sorted(list(v.keys()))])

    def get_counter_examples(self):
      counter_examples = []
      saturated_branches, nonsaturated_branches = self.get_open_saturated_branches()
      for rules in saturated_branches:
        counter_examples.append(self.get_truth_values(rules))
      return counter_examples

    def is_closed_tableau(self):
      return self.get_open_tableau_branches()==[]

    def get_last_branch_branchs(self):
      result = []
      for key, branch in self.symbol_table.items():
        is_last = True
        for key_aux, branch_aux in self.symbol_table.items():
          if(branch_aux['parent']==key and branch_aux!=branch):
            is_last = False
            break
        if is_last :
          result.append(branch)
      return result

    def is_valid_initial_tableau(self):
      has_conclusion = False
      for key, branch in self.symbol_table.items():
        if (key=='branch_0'):# O Tableau inicial deve ter uma sequência de premissas seguida da conclusão.
          for rule in branch['rules']:
              if(isinstance(rule, PremisseRule)): 
                if(has_conclusion):
                  return False
              elif(isinstance(rule, ConclusionRule)):
                has_conclusion = True
        else: # Premissas ou conclusão só podem ocorrer no tableau inicial.
          for rule in branch['rules']:
              if(isinstance(rule, PremisseRule) or isinstance(rule, ConclusionRule)): 
                return False
      return has_conclusion
      
    def getPremisses(self):
      lines = []
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['branch_{}'.format(i)]['rules']:
          if(isinstance(rule, PremisseRule) ):
            lines.append(rule.line)
      return lines

    def getPremissesFormulas(self):
      formulas = []
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['branch_{}'.format(i)]['rules']:
          if(isinstance(rule, PremisseRule) and rule.formula not in formulas):
            formulas.append(rule.formula)
      return formulas

    def getConclusionFormula(self):
      for rule in self.symbol_table['branch_0']['rules']:
          if(isinstance(rule, ConclusionRule)):
            return rule.formula
      return None
    
    def theoremToString(self,parentheses=False):
      premissas = sorted([p.toString(parentheses=parentheses) for p in self.getPremissesFormulas()])
      fConclusion = self.getConclusionFormula()
      if(fConclusion):
        return (', '.join(premissas)+' |- '+fConclusion.toString(parentheses=parentheses))

    def theoremToLatex(self,parentheses=False):
      premisses = ([p.toLatex(parentheses=parentheses) for p in self.getPremissesFormulas()])
      fConclusion = self.getConclusionFormula()
      if(fConclusion):
        return (', '.join(premisses)+' \\vdash '+fConclusion.toLatex(parentheses=parentheses))

    def is_closed_branchs(self):
      for key, branch in self.symbol_table.items():
        if (key=='branch_0'): 
          continue
        if(branch['end_line'] is None): 
          return False
      return True

    def find_branch_variable(self, line):
        branch = self.find_branch(line)
        if branch is not None:
          return self.symbol_table[branch]['variable']
        #Verifica se a linha não tem fórmula (introdução do universal)
        for key, branch in self.symbol_table.items():
          if(int(branch['start_line'])==int(line)):
            return branch['variable']          
        return None

    def check_branch_is_valid(self, branch):
        current_branch = self.current_branch
        while current_branch is not None:
            if current_branch == branch:
                return True
            current_branch = self.symbol_table[current_branch]['parent']
        return False


## dados_json.py

## File analisys.py

deduction_result = tableau_deduction_return()

def value_error_handle(exctype, value, tb):
    deduction_result.add_error(str(value))
    deduction_result.to_json()

sys.excepthook = value_error_handle

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
                error = 'Nenhuma demonstração foi recebida, verifique a entrada.'
            if token.gettokentype() == '$end':
                error = 'Uma das definições não está completa, verifique se todas regras foram aplicadas corretamente.\nLembre-se que uma regra de inferência sempre inicia com um número seguido de um . (linha de referência), o valor-verdade da fórmula (T ou F), tem uma fórmula e uma justificativa (premissa, hipóteses ou uma das regras de inferência com suas respectivas referências para fórmulas anteriores).'
            else:
                source_position = token.getsourcepos()
                error = 'Uma das definições não está completa, verifique se todas regras foram aplicadas corretamente.\nLembre-se que uma regra de inferência sempre inicia com um número seguido de um . (linha de referência), o valor-verdade da fórmula (T ou F), tem uma fórmula e uma justificativa (premissa, hipóteses ou uma das regras de inferência com suas respectivas referências para fórmulas anteriores).\n'
                error += "Erro de sintaxe:\n"
                error += productions[source_position.lineno - 1]
                string = '\n'
                for i in range(source_position.colno -1):
                    string += ' '
                string += '^'
                if token.gettokentype() == 'OUT':
                    string += ' Símbolo não pertence a linguagem.'
                error += string
                
            raise ValueError("@@"+error)

    def get_error(self, type_error, token_error, rule):
        productions = self.state.splitlines()
        column_error = token_error.getsourcepos().colno
        erro = "Erro de sintaxe na linha {}:\n".format(token_error.getsourcepos().lineno)
        erro += productions[token_error.getsourcepos().lineno-1] + "\n"
        for i in range(column_error-1):
            erro += ' '
        if type_error == constants.INVALID_INITIAL_TABLEAU:
            erro += "^, O Tableau inicial deverá conter apenas as premissas (nas primeiras linhas) seguidas da conclusão. Após o Tableau inicial, não é permitido adicionar premissas ou conclusão."
        elif type_error == constants.INVALID_RESULT:
            erro += "^, A fórmula {} não é um resultado válido para esta regra.".format(rule.formula.toString())
        elif type_error == constants.UNEXPECT_RESULT:
            erro += "^, A fórmula {} não é um resultado válido para a regra aplicada.".format(rule.formula.toString())
        elif type_error == constants.IS_NOT_DISJUNCTION_FALSE:
            erro += "^, A fórmula referenciada na linha {} não é disjunção com valor-verdade F.".format(token_error.value)
        elif type_error == constants.IS_NOT_DISJUNCTION_TRUE:
            erro += "^, A fórmula referenciada na linha {} não é disjunção com valor-verdade T.".format(token_error.value)
        elif type_error == constants.IS_NOT_CONJUNCTION_FALSE:
            erro += "^, A fórmula referenciada na linha {} não é conjunção com valor-verdade F.".format(token_error.value)
        elif type_error == constants.IS_NOT_CONJUNCTION_TRUE:
            erro += "^, A fórmula referenciada na linha {} não é conjunção com valor-verdade T.".format(token_error.value)
        elif type_error == constants.IS_NOT_NEGATION_FALSE:
            erro += "^, A fórmula referenciada na linha {} não é negação com valor-verdade F.".format(token_error.value)
        elif type_error == constants.IS_NOT_NEGATION_TRUE:
            erro += "^, A fórmula referenciada na linha {} não é negação com valor-verdade T.".format(token_error.value)
        elif type_error == constants.IS_NOT_IMPLICATION:
            erro += "^, A fórmula referenciada na linha {} não é implicação.".format(token_error.value)
        elif type_error == constants.INVALID_NEGATION:
            erro += "^, Nenhuma das fórmulas referencias pelas linhas contradiz a outra fórmula."
        elif type_error == constants.INVALID_LEFT_IMPLICATION:
            erro += "^, A fórmula {} (conclusão da regra) deve ser o antecedente da implicação da fórmula referenciada com valor-verdade F.".format(rule.formula.toString())
        elif type_error == constants.INVALID_RIGHT_IMPLICATION:
            erro += "^, A fórmula {} (conclusão da regra) deve ser o consequente da implicação da fórmula referenciada com valor-verdade T.".format(rule.formula.toString())
        elif type_error == constants.INVALID_LEFT_RIGHT_IMPLICATION:
            erro += "^, A fórmula {} (conclusão da regra) deve ser o antecedente ou o consequente da implicação da fórmula referenciada.".format(rule.formula.toString())
        elif type_error == constants.INVALID_LEFT_CONJUNCTION:
            erro += "^, A fórmula à esquerda fórmula da conclusão não é demonstrada por nenhuma das linhas referenciadas nesta regra."
        elif type_error == constants.INVALID_RIGHT_CONJUNCTION:
            erro += "^, A fórmula à direita da fórmula da conclusão não é demonstrada por nenhuma das linhas referenciadas nesta regra."
        elif type_error == constants.INVALID_LEFT_OR_RIGHT_DISJUNCTION:
            erro += "^, A fórmula à direita ou à equerda da fórmula da conclusão deve ser a mesma da fórmula referencia na linha {}.".format(token_error.value)
        elif type_error == constants.INVALID_LEFT_OR_RIGHT_CONJUNCTION:
            erro += "^, A fórmula {} (conclusão da regra) deve ser a mesma da direita ou da equerda da fórmula da linha {}.".format(rule.formula.toString(),token_error.value)
        elif type_error == constants.USING_DESCARTED_RULE:
            erro += "^, a referência a fórmula da linha {} não pode ser utilizada, pois esta fórmula não pertence a este ramo.".format(token_error.value)
        elif type_error == constants.REFERENCED_LINE_NOT_DEFINED:
            erro += "^, a referência a fórmula da linha {} não pode ser utilizada, pois todas as referências devem ocorrer antes desta regra.".format(token_error.value)
        elif type_error == constants.CLOSE_BRACKET_WITHOUT_BOX:
            erro += "^, Fechamento de ramos sem ramo aberto."
        elif type_error == constants.BOX_MUST_BE_DISPOSED:
            erro += "^, O ramo aberto deve ser fechado."
        elif type_error == constants.BOX_MUST_BE_DISPOSED_BY_RULE:
            erro += "^, Esta caixa dever ser fechada após a aplicação de pelo menos uma regra."
        elif type_error == constants.INVALID_SUBSTITUTION_UNIVERSAL:
            erro += "^, A fórmula {} não é uma substituição válida da fórmula universal refenciada na linha {}.".format(rule.formula.toString(), rule.reference1)
        elif type_error == constants.INVALID_UNIVERSAL_FORMULA:
            erro += "^, A fórmula referenciada na linha {} não é uma fórmula do tipo universal com o valor de verdade {}.".format(rule.reference1, rule.true_value)
        elif type_error == constants.INVALID_EXISTENCIAL_FORMULA:
            erro += "^, A fórmula referenciada na linha {} não é uma fórmula do tipo existencial com o valor de verdade {}.".format(rule.reference1, rule.true_value)
        elif type_error == constants.INVALID_SUBSTITUTION_EXISTENCIAL:
            erro += "^, A fórmula {} não é uma substituição válida da fórmula existencial refenciada na linha {}.".format(rule.formula.toString(), rule.reference1)
        elif type_error == constants.VARIABLE_IS_NOT_FRESH_VARIABLE:
            erro += "^, A variável utilizada nesta fórmula {} é uma variável livre de uma fórmula definida anteriormente e, portanto, não pode ser utilizada nesta regra.".format(rule.formula.toString())
        elif type_error == constants.INVALID_TRUE_CONJUNCTION_NEXT:
            erro += "^, A próxima linha deveria ser a regra &T com a fórmula {}.".format(rule.formula.right.toString())
        elif type_error == constants.INVALID_TRUE_CONJUNCTION_PREVIOUS:
            erro += "^, A linha anterior deveria ser a regra &T com a fórmula {}.".format(rule.formula.left.toString())
        elif type_error == constants.INVALID_FALSE_DISJUNCTION_NEXT:
            erro += "^, A próxima linha deveria ser a regra |F com a fórmula {}.".format(rule.formula.right.toString())
        elif type_error == constants.INVALID_FALSE_DISJUNCTION_PREVIOUS:
            erro += "^, A linha anterior deveria ser a regra |F com a fórmula {}.".format(rule.formula.left.toString())
        elif type_error == constants.INVALID_FALSE_IMPLICATION_NEXT:
            erro += "^, A próxima linha deveria ser a regra ->F com a fórmula {}.".format(rule.formula.right.toString())
        elif type_error == constants.INVALID_FALSE_IMPLICATION_PREVIOUS:
            erro += "^, A linha anterior deveria ser a regra ->F com a fórmula {}.".format(rule.formula.left.toString())
        elif type_error == constants.INVALID_TRUE_DISJUNCTION_NEXT:
            erro += "^, Deveria haver um próximo ramo, iniciando com a regra |T com a fórmula {}.".format(rule.formula.right.toString())
        elif type_error == constants.INVALID_TRUE_DISJUNCTION_PREVIOUS:
            erro += "^, Deveria haver um ramo anterior, iniciando com a regra |T com a fórmula {}.".format(rule.formula.left.toString())
        elif type_error == constants.INVALID_TRUE_IMPLICATION_NEXT:
            erro += "^, Deveria haver um próximo ramo, iniciando com a regra ->T com a fórmula {}.".format(rule.formula.right.toString())
        elif type_error == constants.INVALID_TRUE_IMPLICATION_PREVIOUS:
            erro += "^, Deveria haver um ramo anterior, iniciando com a regra ->T com a fórmula {}.".format(rule.formula.left.toString())
        elif type_error == constants.INVALID_FALSE_CONJUNCTION_NEXT:
            erro += "^, Deveria haver um próximo ramo, iniciando com a regra &F com a fórmula {}.".format(rule.formula.right.toString())
        elif type_error == constants.INVALID_FALSE_CONJUNCTION_PREVIOUS:
            erro += "^, Deveria haver um ramo anterior, iniciando com a regra &F com a fórmula {}.".format(rule.formula.left.toString())
        elif type_error == constants.INVALID_BETA_RULE:
            erro += "^, Uma regra do tipo beta tem que ter exatamente dois ramos."
        elif type_error == constants.ALREADY_USED_RULE_IN_BRANCH:
            erro += "^, A regra referência na linha {} só pode ser utilizada uma única vez neste ramo.".format(rule.line)
        elif type_error == constants.PREMISSE_SHOULD_BE_TRUE:
            erro += "^, A premissa deve ter valor-verdade T."
        elif type_error == constants.CONCLUSION_SHOULD_BE_FALSE:
            erro += "^, A conclusão deve ter valor-verdade F."
        elif type_error == constants.RULE_CANNOT_BE_APPLIED:
            erro += "^, Não é possível aplicar regra a um átomo ou predicado."
        elif type_error == constants.RULE_MUST_BE_BETA:
            erro += "^, A regra deve ser do tipo beta."
        elif type_error == constants.RULE_MUST_BE_ALPHA:
            erro += "^, A regra deve ser do tipo alpha."
        elif type_error == constants.WRONG_TRUE_VALUE:
            if rule.token_true_value.gettokentype() == 'FALSE':  
              erro += "^, O valor-verdade deveria ser T para esta regra."
            else:
              erro += "^, O valor-verdade deveria ser F para esta regra."

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
            return f'{input_theorem} não é um teorema válido!'
          set_premisses = set([p.toString() for p in premisses])

        if(result.is_closed):
          if(conclusion is None or (conclusion==result.conclusion and set_premisses==set_premisses_result)):
            r += "A demonstração está correta."
            if display_theorem:
              r += "\n"+s_theorem
          else:
            r += f"Sua demostração de {s_theorem} é válida, mas é diferente da demonstração solicitada {input_theorem}"                   

          if display_latex: 
            r += "\nLatex:\n"+str(result.latex)
            r += "\nLatex com cor:\n"+str(result.colored_latex)
        else:
            if result.saturared_branches != []:
              if(conclusion is None or (conclusion==result.conclusion and set_premisses==set_premisses_result)):
                r += "O Teorema não é válido."
                if display_theorem:
                  r += "\n"+result.theorem 
              if display_countermodel:
                r += "\nSão contra-exemplos:"
                for s_v in result.counter_examples:
                    r += '\n  '+s_v
              if display_latex: 
                r += "\nLatex:\nO Teorema ${}$ não é válido.\n".format(result.latex_theorem)
                if display_countermodel:
                  r += "\nSão contra-exemplos:"
                  r += "\n\\begin{itemize}"
                  for s_v in result.counter_examples:
                      r += '\n  \item $'+s_v+'$'
                  r += "\n\end{itemize}"
                r += "\n"+str(result.colored_latex)
            else: 
                r += "\nA demonstração do teorema não está completa.\n"
                if display_theorem:
                  r += result.theorem
                r += "\nOs ramos abaixo não estão saturados:"
                for rules in result.open_branches:
                  r += "\nRamo:\n  "
                  r += '\n  '.join([r.toString() for r in reversed(rules)])
                if display_latex: 
                  r += "\nLatex:\n"+str(result.latex)
                  r += "\nLatex com cor:\n"+str(result.colored_latex)
      else:
        r += "Os seguintes erros foram encontrados:\n"
        for error in result.errors:
          r += '\n'+str(error)
      return r
  except ValueError:
      s = traceback.format_exc()
      result = (s.split("@@"))[-1]
      r = "Os seguintes erros foram encontrados:\n\n"
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
                error = 'Nenhuma fórmula foi recebida, verifique a entrada.'
            if token.gettokentype() == '$end':
                error = 'Nenhuma fórmula foi recebida, verifique a entrada.'
            else:
                source_position = token.getsourcepos()
                error = 'A definição da fórmula não está correta, verifique se todas regras foram aplicadas corretamente.\nLembre-se que uma uma fórmula é definida pela seguinte BNF:\nF :== P | ~ P | P & Q | P | Q | P -> Q | P <-> Q | (P), onde P,Q são átomos.\n'
                error += "Erro de sintaxe:\n"
                error += productions[source_position.lineno - 1]
                string = '\n'
                for i in range(source_position.colno -1):
                    string += ' '
                string += '^'
                if token.gettokentype() == 'OUT':
                    string += ' Símbolo não pertence a linguagem.'
                error += string
                
            raise ValueError("@@"+error)

    def get_error(self, type_error, token_error, rule):
        productions = self.state.splitlines()
        column_error = token_error.getsourcepos().colno
        erro = "Erro de sintaxe na linha {}:\n".format(token_error.getsourcepos().lineno)
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
                error = 'Nenhuma fórmula foi recebida, verifique a entrada.'
            if token.gettokentype() == '$end':
                error = 'Nenhuma fórmula foi recebida, verifique a entrada.'
            else:
                source_position = token.getsourcepos()
                error = 'A definição da fórmula não está correta, verifique se todas regras foram aplicadas corretamente.\nLembre-se que uma uma fórmula é definida pela seguinte BNF:\nF :== P | ~ P | P & Q | P | Q | P -> Q | P <-> Q | (P), onde P,Q são átomos.\n'
                error += "Erro de sintaxe:\n"
                error += productions[source_position.lineno - 1]
                string = '\n'
                for i in range(source_position.colno -1):
                    string += ' '
                string += '^'
                if token.gettokentype() == 'OUT':
                    string += ' Símbolo não pertence a linguagem.'
                error += string
                
            raise ValueError("@@"+error)

    def get_error(self, type_error, token_error, rule):
        productions = self.state.splitlines()
        column_error = token_error.getsourcepos().colno
        erro = "Erro de sintaxe na linha {}:\n".format(token_error.getsourcepos().lineno)
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