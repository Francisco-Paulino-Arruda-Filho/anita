from rply import LexerGenerator
from anita.utils.i18n import t


class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        #Comma
        self.lexer.add('COMMA', r'\,')

        # Dot
        self.lexer.add('DOT', r'\.')

        # Vdash
        self.lexer.add('V_DASH', r'\|-|\|=')

        # Parentheses
        self.lexer.add('OPEN_PAREN', r'\(')
        self.lexer.add('CLOSE_PAREN', r'\)')

        #Brackets
        self.lexer.add('OPEN_BRACKET', r'\{')
        self.lexer.add('CLOSE_BRACKET', r'\}')

        #rules
        self.lexer.add('IMP_FALSE', r'->F')
        self.lexer.add('IMP_TRUE', r'->T')
        self.lexer.add('OR_FALSE', r'\|F')
        self.lexer.add('OR_TRUE', r'\|T')
        self.lexer.add('AND_TRUE', r'&T')
        self.lexer.add('AND_FALSE', r'&F')
        self.lexer.add('NEG_TRUE', r'~T')
        self.lexer.add('NEG_FALSE', r'~F')

        # Connectives
        self.lexer.add('BOTTOM', r'@')
        self.lexer.add('NOT', r'~')
        self.lexer.add('AND', r'&')
        self.lexer.add('OR', r'\|')
        self.lexer.add('IMPLIE', r'->')
        self.lexer.add('IFF', r'<->')

        #First order rules
        self.lexer.add('EXT_FALSE', r'EF')
        self.lexer.add('EXT_TRUE', r'ET')
        self.lexer.add('ALL_FALSE', r'AF')
        self.lexer.add('ALL_TRUE', r'AT')

        #First order connectives
        self.lexer.add('EXT', r'E[a-z][a-z0-9]*')
        self.lexer.add('ALL', r'A[a-z][a-z0-9]*')

        # definitions
        self.lexer.add('TRUE', r'T')
        self.lexer.add('FALSE', r'F')

        # Number
        self.lexer.add('NUM', r'\d+')

        #justification
        self.lexer.add('PREMISSE', r'pre')
        self.lexer.add('CONCLUSION', t('PREMISE_CONCLUSION'))
        self.lexer.add('CLOSED', t('PREMISE_CLOSED'))

        #Variable
        self.lexer.add('VAR', r'(?!pre)[a-z][a-z0-9]*')

        # Athom
        self.lexer.add('ATHOM', r'[A-Z][A-Z0-9]*' )

        # Ignore spaces and comments
        self.lexer.ignore('##[^##]*##')
        self.lexer.ignore('#[^\n]*\n?')
        self.lexer.ignore('\s+')  

        # Detect symbols out of grammar
        self.lexer.add('OUT', r'.*' )      

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()