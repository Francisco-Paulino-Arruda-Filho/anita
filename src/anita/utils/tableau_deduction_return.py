import json


class tableau_deduction_return:
    def __init__(self):
        self.latex = ''
        self.is_closed = False,
        self.errors = []
        self.premisses = []
        self.conclusion = None
        self.latex_theorem = ''
        self.theorem = ''
        self.counter_examples = None
        self.colored_latex = ''
        self.saturared_branches = []
        self.open_branches = []

    def add_error(self, error):
        self.errors.append(error)

    def to_json(self):
        result = {
            'latex': self.latex,
            'errors': self.errors,
            'premisses': self.premisses,
            'conclusion': self.conclusion,
            'is_closed': self.is_closed,
            'theorem':self.theorem,
            'latex_theorem': self.latex_theorem,
            'colored_latex': self.colored_latex,
            'counter_examples': self.counter_examples,
        }
        with open("result.json", "w", encoding='utf8') as f:
            f.write(json.dumps(result, sort_keys=True, indent=3, ensure_ascii=False))