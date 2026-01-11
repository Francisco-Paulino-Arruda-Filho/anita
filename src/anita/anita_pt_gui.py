import json
import os

STRINGS_PATH = os.path.join(os.path.dirname(__file__), 'anita_pt_gui_strings.json')
with open(STRINGS_PATH, encoding='utf-8') as f:
    PT_STRINGS = json.load(f)


def t(key):
    return PT_STRINGS.get(key, key)


import ipywidgets as widgets
from IPython.display import display, Markdown, HTML
import traceback
from anita.anita_pt_fo import ParserAnita, ParserTheorem, ParserFormula


def anita(input_proof='', input_text_assumptions=[], input_text_conclusion='', height_layout='300px'):
  layout = widgets.Layout(width='90%', height=height_layout)
  run = widgets.Button(description=t('BTN_VERIFY'))
  input = widgets.Textarea(
      value=input_proof,
      placeholder=t('ANITA_INPUT_PROOF_PLACEHOLDER'),
      description='',
      layout=layout
      )
  cLatex = widgets.Checkbox(value=False, description=t('CHECKBOX_SHOW_LATEX'))
  output = widgets.Output()
  wButtons = widgets.HBox([run, cLatex])
  if input_text_conclusion!='':
    display(Markdown(t('ANITA_CONSIDER_ASSUMPTIONS_TITLE')))
    q_assumptions =''
    i = 1
    for assumption in input_text_assumptions:
      q_assumptions += f'\n1. {assumption}'
      i+=1
    display(Markdown(q_assumptions))
    display(Markdown(t('ANITA_CONSIDER_CONCLUSION_TEXT')))
    q_conclusion =f'\n{i}. {input_text_conclusion}'
    display(Markdown(q_conclusion))
    display(Markdown(t('ANITA_REPRESENT_AND_PROVE_TEXT')))
    if input_proof=='':
      input.value = t('ANITA_REPRESENT_FORMULAS_HEADER')
      i = 1
      for assumption in input_text_assumptions:
        input.value += f"\n# {i}. ... {t('ANITA_REPRESENT_FOR')} \"{assumption}\""
        i+=1
      input.value += f"\n# {i}. ... {t('ANITA_REPRESENT_FOR')} \"{input_text_conclusion}\""
      input.value += f"\n{t('ANITA_SHOW_VALID_REASONING')}"
      input.value += '\n# ...'
  else:  
    display(Markdown(t('ANITA_TYPE_PROOF_TITLE')))
  display(input, wButtons, output)

  def on_button_run_clicked(_):
    output.clear_output()
    with output:
      try:
          result = ParserAnita.getProof(input.value)
          if(result.errors==[]):
            msg = []
            if(result.is_closed):
              display(HTML(t('ANITA_PROOF_CORRECT').format(theorem=result.theorem)))
            else:
              if result.saturared_branches!=[]:
                display(HTML(t('ANITA_THEOREM_NOT_VALID').format(theorem=result.theorem))) 
                msg.append(t('ANITA_COUNTEREXAMPLES_LABEL'))
                for s_v in result.counter_examples:
                  msg.append(s_v)                  
              else:
                display(HTML(t('ANITA_PROOF_INCOMPLETE').format(theorem=result.theorem))) 
                msg.append(t('ANITA_UNSATURATED_BRANCHES_LABEL'))
                for rules in result.open_branches:
                  msg.append(t('ANITA_BRANCH_LABEL'))
                  msg.append('<br>'.join([r.toString() for r in reversed(rules)]))
            if(cLatex.value):
              msg.append(t('ANITA_LATEX_CODE_LABEL'))
              msg.append('%'+result.latex_theorem)
              msg.append(result.colored_latex)
            display(widgets.HTML('<br>'.join(msg)))       
          else:
            display(HTML(t('ANITA_PROOF_ERRORS_TITLE')))
            for error in result.errors:
                print(error)
      except ValueError:
          s = traceback.format_exc()
          result = (s.split('@@'))[-1]
          print (f'{result}')
      else:
          pass
  run.on_click(on_button_run_clicked)


def anita_theorem(input_theorem, input_proof='', height_layout='300px',default_gentzen=False, default_fitch=False):
  layout = widgets.Layout(width='90%', height=height_layout)
  run = widgets.Button(description=t('ANITA_THEOREM_BUTTON_VERIFY'))
  input = widgets.Textarea(
      value=input_proof,
      placeholder=t('ANITA_THEOREM_INPUT_PLACEHOLDER'),
      description='',
      layout=layout
      )
  premisses, conclusion = ParserTheorem.getTheorem(input_theorem)
  if conclusion is None:
    display(HTML(t('ANITA_THEOREM_INVALID').format(theorem=input_theorem)))
    return
  cLatex = widgets.Checkbox(value=False, description=t('ANITA_THEOREM_CHECKBOX_LATEX'))
  output = widgets.Output()
  wButtons = widgets.HBox([run, cLatex])
  
  display(widgets.HTML(t('ANITA_THEOREM_TITLE').format(theorem=input_theorem)), 
          input, wButtons, output)
  
  def on_button_run_clicked(_):
    output.clear_output()
    with output:
      try:
          result = ParserAnita.getProof(input.value)
          if(result.errors==[]):
              set_premisses = set([p.toString() for p in premisses])
              set_premisses_result = set([p.toString() for p in result.premisses])
              if(conclusion==result.conclusion and set_premisses==set_premisses_result):
                msg = []
                if(result.is_closed):
                  display(HTML(t('ANITA_THEOREM_CORRECT').format(theorem=result.theorem)))
                else:
                  if result.saturared_branches!=[]:
                    display(HTML(t('ANITA_THEOREM_NOT_VALID_2').format(theorem=result.theorem)))              
                    msg.append(t('ANITA_THEOREM_COUNTEREXAMPLES_LABEL'))
                    for s_v in result.counter_examples:
                      msg.append(s_v)                  
                  else:
                    display(HTML(t('ANITA_THEOREM_INCOMPLETE').format(theorem=result.theorem)))              
                    msg.append(t('ANITA_THEOREM_UNSATURATED_BRANCHES_LABEL'))
                    for rules in result.open_branches:
                      msg.append(t('ANITA_THEOREM_BRANCH_LABEL'))
                      msg.append('<br>'.join([r.toString() for r in reversed(rules)]))
                if(cLatex.value):
                  msg.append(t('ANITA_THEOREM_LATEX_CODE_LABEL'))
                  msg.append('%'+result.latex_theorem)
                  msg.append(result.colored_latex)
                display(widgets.HTML('<br>'.join(msg)))       
              else:
                display(HTML(t('ANITA_THEOREM_WRONG_PROOF').format(theorem=result.theorem, input_theorem=input_theorem)))
          else:
            display(HTML(t('ANITA_THEOREM_ERRORS_TITLE')))
            for error in result.errors:
                print(error)
      except ValueError:
          s = traceback.format_exc()
          result = (s.split('@@'))[-1]
          print (f'{result}')
      else:
          pass
  run.on_click(on_button_run_clicked)


def is_substitutable(input_formula='', input_var ='x', input_term='a'):
  run = widgets.Button(description=t('SUBSTITUTABLE_BUTTON_VERIFY'))
  cResult = widgets.RadioButtons(
    options=[t('SUBSTITUTABLE_OPTIONS_YES'), t('SUBSTITUTABLE_OPTIONS_NO')],
    value=None, 
    description=t('SUBSTITUTABLE_ANSWER_LABEL'),
    disabled=False
)
  output = widgets.Output()
  wButtons = widgets.HBox([run])
  
  display(HTML(t('SUBSTITUTABLE_QUESTION').format(var=input_var, term=input_term, formula=input_formula)))
  display(cResult, wButtons, output)

  def on_button_run_clicked(_):
    output.clear_output()
    with output:
      try:
          f = ParserFormula.getFormula(input_formula)
          if(f is not None):
            if (f.is_substitutable(input_var,input_term) and cResult.value==t('SUBSTITUTABLE_OPTIONS_YES')):
              display(HTML(t('SUBSTITUTABLE_RIGHT_ANSWER')))              
              display(HTML(t('SUBSTITUTABLE_RIGHT_ANSWER_IS').format(var=input_var, term=input_term, formula=input_formula)))              
            elif not f.is_substitutable(input_var,input_term) and cResult.value==t('SUBSTITUTABLE_OPTIONS_NO'):
              display(HTML(t('SUBSTITUTABLE_RIGHT_ANSWER')))              
              display(HTML(t('SUBSTITUTABLE_RIGHT_ANSWER_IS_NOT').format(var=input_var, term=input_term, formula=input_formula))) 
            else:
              display(HTML(t('SUBSTITUTABLE_WRONG_ANSWER')))
          else:
            display(HTML(t('SUBSTITUTABLE_INVALID_FORMULA')))
      except ValueError:
          s = traceback.format_exc()
          result = (s.split('@@'))[-1]
          print (f'{result}')
      else:
          pass
  run.on_click(on_button_run_clicked)


def verify_variables(input_string='', input_formula = ''):
  layout = widgets.Layout(width='90%')
  run = widgets.Button(description=t('VERIFY_VARIABLES_BUTTON_VERIFY'))
  input = widgets.Text(
      value=input_string,
      placeholder=t('VERIFY_VARIABLES_PLACEHOLDER'),
      description='',
      layout=layout
      )
  output = widgets.Output()
  wButtons = widgets.HBox([run])
  
  display(HTML(t('VERIFY_VARIABLES_PROMPT').format(formula=input_formula)))
  display(HTML(t('VERIFY_VARIABLES_HINT')))
  display(input, wButtons, output)

  def on_button_run_clicked(_):
    output.clear_output()
    with output:
      try:
          result = ParserFormula.getFormula(input_formula)
          variables = set([x.strip() for x in input.value.strip().split(';')])
          if(result is not None):
            if variables==result.all_variables():
              display(HTML(t('VERIFY_VARIABLES_RIGHT_ANSWER')))              
            else:
              display(HTML(t('VERIFY_VARIABLES_WRONG_ANSWER')))
          else:
            display(HTML(t('VERIFY_VARIABLES_INVALID_FORMULA')))
      except ValueError:
          s = traceback.format_exc()
          result = (s.split('@@'))[-1]
          print (f'{result}')
      else:
          pass
  run.on_click(on_button_run_clicked)


def verify_free_variables(input_string='', input_formula = ''):
  layout = widgets.Layout(width='90%')
  run = widgets.Button(description=t('VERIFY_FREE_VARIABLES_BUTTON_VERIFY'))
  input = widgets.Text(
      value=input_string,
      placeholder=t('VERIFY_FREE_VARIABLES_PLACEHOLDER'),
      description='',
      layout=layout
      )
  output = widgets.Output()
  wButtons = widgets.HBox([run])
  
  display(HTML(t('VERIFY_FREE_VARIABLES_PROMPT').format(formula=input_formula)))
  display(HTML(t('VERIFY_FREE_VARIABLES_HINT')))
  display(input, wButtons, output)

  def on_button_run_clicked(_):
    output.clear_output()
    with output:
      try:
          result = ParserFormula.getFormula(input_formula)
          variables = set([x.strip() for x in input.value.strip().split(';')])
          if(result is not None):
            if variables==result.free_variables():
              display(HTML(t('VERIFY_FREE_VARIABLES_RIGHT_ANSWER')))              
            else:
              display(HTML(t('VERIFY_FREE_VARIABLES_WRONG_ANSWER')))
          else:
            display(HTML(t('VERIFY_FREE_VARIABLES_INVALID_FORMULA')))
      except ValueError:
          s = traceback.format_exc()
          result = (s.split('@@'))[-1]
          print (f'{result}')
      else:
          pass
  run.on_click(on_button_run_clicked)


def verify_bound_variables(input_string='', input_formula = ''):
  layout = widgets.Layout(width='90%')
  run = widgets.Button(description=t('VERIFY_BOUND_VARIABLES_BUTTON_VERIFY'))
  input = widgets.Text(
      value=input_string,
      placeholder=t('VERIFY_BOUND_VARIABLES_PLACEHOLDER'),
      description='',
      layout=layout
      )
  output = widgets.Output()
  wButtons = widgets.HBox([run])
  
  display(HTML(t('VERIFY_BOUND_VARIABLES_PROMPT').format(formula=input_formula)))
  display(HTML(t('VERIFY_BOUND_VARIABLES_HINT')))
  display(input, wButtons, output)

  def on_button_run_clicked(_):
    output.clear_output()
    with output:
      try:
          result = ParserFormula.getFormula(input_formula)
          variables = set([x.strip() for x in input.value.strip().split(';')])
          if(result is not None):
            if variables==result.bound_variables():
              display(HTML(t('VERIFY_BOUND_VARIABLES_RIGHT_ANSWER')))              
            else:
              display(HTML(t('VERIFY_BOUND_VARIABLES_WRONG_ANSWER')))
          else:
            display(HTML(t('VERIFY_BOUND_VARIABLES_INVALID_FORMULA')))
      except ValueError:
          s = traceback.format_exc()
          result = (s.split('@@'))[-1]
          print (f'{result}')
      else:
          pass
  run.on_click(on_button_run_clicked)


def verify_substitution(input_string='', input_formula = '', input_var ='x', input_term='a'):
  layout = widgets.Layout(width='90%')
  run = widgets.Button(description=t('VERIFY_SUBSTITUTION_BUTTON_VERIFY'))
  input = widgets.Text(
      value=input_string,
      placeholder=t('VERIFY_SUBSTITUTION_PLACEHOLDER'),
      description='',
      layout=layout
      )
  cParentheses = widgets.Checkbox(value=False, description=t('VERIFY_SUBSTITUTION_CHECKBOX_PARENTHESES'))
  cLatex = widgets.Checkbox(value=False, description=t('VERIFY_SUBSTITUTION_CHECKBOX_LATEX'))
  output = widgets.Output()
  wButtons = widgets.HBox([run, cParentheses, cLatex])
  
  display(HTML(t('VERIFY_SUBSTITUTION_PROMPT').format(var=input_var, term=input_term, formula=input_formula)))
  display(input, wButtons, output)

  def on_button_run_clicked(_):
    output.clear_output()
    with output:
      try:
          f = ParserFormula.getFormula(input_formula)
          result = ParserFormula.getFormula(input.value)
          if(result is not None):
            if result==f.substitution(input_var,input_term):
              display(HTML(t('VERIFY_SUBSTITUTION_RIGHT_ANSWER')))              
              if(cLatex.value):
                s = result.toLatex(parentheses=cParentheses.value)
                display(Markdown(rf'${s}$'))
              else:
                display(HTML(rf'{result.toString(parentheses=cParentheses.value)}'))
            else:
              display(HTML(t('VERIFY_SUBSTITUTION_WRONG_ANSWER').format(result=result.toString(), var=input_var, term=input_term, formula=input_formula)))
          else:
            display(HTML(t('VERIFY_SUBSTITUTION_INVALID_FORMULA')))
      except ValueError:
          s = traceback.format_exc()
          result = (s.split('@@'))[-1]
          print (f'{result}')
      else:
          pass
  run.on_click(on_button_run_clicked)


def verify_valid_conclusion(input_assumptions, input_conclusion, result_value=False):
  layout = widgets.Layout(width='40%')
  run = widgets.Button(description=t('VERIFY_VALID_CONCLUSION_BUTTON_VERIFY'))
  output = widgets.Output()
  wButtons = widgets.HBox([run])
  cResult = widgets.RadioButtons(
    options=[t('VERIFY_VALID_CONCLUSION_OPTIONS_YES'), t('VERIFY_VALID_CONCLUSION_OPTIONS_NO')],
    value=None, 
    description=t('VERIFY_VALID_CONCLUSION_ANSWER_LABEL'),
    disabled=False
)
  questao = t('VERIFY_VALID_CONCLUSION_INTRO')
  i = 1
  for assumption in input_assumptions:
    questao += f'\n1. {assumption}'
    i+=1
  questao+='\n'+t('VERIFY_VALID_CONCLUSION_QUESTION')
  questao+=f'\n{i}. {input_conclusion}'
  display(HTML(questao))
  display(widgets.HBox([cResult,wButtons]), output)

  def on_button_run_clicked(_):
    output.clear_output()
    with output:
      if (cResult.value is None):
        display(HTML(t('VERIFY_VALID_CONCLUSION_CHOOSE_OPTION')))
      elif(result_value==(cResult.value==t('VERIFY_VALID_CONCLUSION_OPTIONS_YES'))):
        display(HTML(t('VERIFY_VALID_CONCLUSION_RIGHT_ANSWER')))
      else:
        display(HTML(t('VERIFY_VALID_CONCLUSION_WRONG_ANSWER')))
  run.on_click(on_button_run_clicked)


def verify_formula(input_string=''):
  layout = widgets.Layout(width='90%')
  run = widgets.Button(description=t('VERIFY_FORMULA_BUTTON_VERIFY'))
  input = widgets.Text(
      value=input_string,
      placeholder=t('VERIFY_FORMULA_PLACEHOLDER'),
      description='',
      layout=layout
      )
  cParentheses = widgets.Checkbox(value=False, description=t('VERIFY_FORMULA_CHECKBOX_PARENTHESES'))
  cLatex = widgets.Checkbox(value=False, description=t('VERIFY_FORMULA_CHECKBOX_LATEX'))
  output = widgets.Output()
  wButtons = widgets.HBox([run, cParentheses, cLatex])
  
  display(HTML(t('VERIFY_FORMULA_PROMPT')))
  display(input, wButtons, output)

  def on_button_run_clicked(_):
    output.clear_output()
    with output:
      try:
          result = ParserFormula.getFormula(input.value)
          if(result is not None):
              display(HTML(t('VERIFY_FORMULA_RIGHT_ANSWER')))
              if(cLatex.value):
                s = result.toLatex(parentheses=cParentheses.value)
                display(Markdown(rf'${s}$'))
              else:
                display(HTML(rf'{result.toString(parentheses=cParentheses.value)}'))
          else:
            display(HTML(t('VERIFY_VARIABLES_INVALID_FORMULA')))
      except ValueError:
          s = traceback.format_exc()
          result = (s.split('@@'))[-1]
          print (f'{result}')
      else:
          pass
  run.on_click(on_button_run_clicked)

