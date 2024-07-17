import ply.lex as lex


class MyLexer:

    reserved = {
        'and': 'WAND',
        'or': 'WOR',
        'not': 'WNOT',
        'true': 'TRUE',
        'false': 'FALSE',
        'X': 'NEXT',
        'U': 'UNTIL',
        'F': 'EVENTUALLY',
        'G': 'GLOBALLY',
        'NEXT': 'UNEXT',
        'UNTIL': 'UUNTIL',
        'EVENTUALLY': 'UEVENTUALLY',
        'ALWAYS': 'UGLOBALLY',
        'next': 'LNEXT',
        'until': 'LUNTIL',
        'eventually': 'LEVENTUALLY',
        'always': 'LGLOBALLY'}
    # List of token names.   This is always required
    tokens = (
        'TERM',
        'NOT',
        'AND',
        'OR',
        'IMPLIES',
        'DIMPLIES',
        'LPAR',
        'RPAR'
    ) + tuple(reserved.values())

    # Regular expression rules for simple tokens
    t_TRUE = r'true'
    t_FALSE = r'false'
    t_AND = r'\&'
    t_WAND = 'and'
    t_OR = r'\|'
    t_WOR = 'or'
    t_IMPLIES = r'\->'
    t_DIMPLIES = r'\<->'
    t_NOT = r'\~'
    t_WNOT = 'not'
    t_LPAR = r'\('
    t_RPAR = r'\)'
    # FUTURE OPERATORS
    t_NEXT = r'X'
    t_UNTIL = r'U'
    t_EVENTUALLY = r'F'
    t_GLOBALLY = r'G'
    t_UNEXT = r'NEXT'
    t_UUNTIL = r'UNTIL'
    t_UEVENTUALLY = r'EVENTUALLY'
    t_UGLOBALLY = r'ALWAYS'
    t_LNEXT = r'next'
    t_LUNTIL = r'until'
    t_LEVENTUALLY = r'eventually'
    t_LGLOBALLY = r'always'
    t_ignore = r' ' + '\n'

    def t_TERM(self, t):
        r'(?<![a-z])(?!true|false)[_a-z0-9]+'
        t.type = MyLexer.reserved.get(t.value, 'TERM')
        return t  # Check for reserved words

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' in the input formula")
        t.lexer.skip(1)

    # Build the lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
