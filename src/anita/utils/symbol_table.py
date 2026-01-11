from anita.formula.athom_formula.AtomFormula import AthomFormula
from anita.formula.predicate_formula.PredicateFormula import PredicateFormula
from anita.rules.AndTrueRule import AndTrueRule
from anita.rules.ClosedRule import ClosedRule
from anita.rules.ConclusionRule import ConclusionRule
from anita.rules.ImpFalseRule import ImpFalseRule
from anita.rules.OrFalseRule import OrFalseRule
from anita.rules.PremisseRule import PremisseRule


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