import ply.yacc as yacc
from Lexer import MyLexer


class MyParser(object):

    precedence = (
        ('left', 'AND', 'WAND', 'OR', 'WOR', 'IMPLIES', 'DIMPLIES', 'UNTIL', 'UUNTIL', 'LUNTIL'),
        ('right', 'NEXT', 'UNEXT', 'LNEXT', 'EVENTUALLY', 'UEVENTUALLY', 'LEVENTUALLY', 'GLOBALLY', 'UGLOBALLY', 'LGLOBALLY'),
        ('right', 'NOT', 'WNOT'),
        ('nonassoc', 'LPAR', 'RPAR')
    )

    def __init__(self):
        self.lexer = MyLexer()
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)
        self.change = {
                    'and': '&',
                    'or': '|',
                    'not': '~',
                    '&': '&',
                    '|': '|',
                    '~': '~',
                    '->': '->',
                    '<->': '<->',
                    'X': 'X',
                    'U': 'U',
                    'F': 'F',
                    'G': 'G',
                    'NEXT': 'X',
                    'UNTIL': 'U',
                    'EVENTUALLY': 'F',
                    'ALWAYS': 'G',
                    'next': 'X',
                    'until': 'U',
                    'eventually': 'F',
                    'always': 'G'}

    def __call__(self, s, **kwargs):
        return self.parser.parse(s, lexer=self.lexer.lexer, debug=False)

    def p_formula(self, p):
        '''
        formula : formula AND formula
                | formula WAND formula
                | formula OR formula
                | formula WOR formula
                | formula IMPLIES formula
                | formula DIMPLIES formula
                | formula UNTIL formula
                | formula LUNTIL formula
                | formula UUNTIL formula
                | NEXT formula
                | LNEXT formula
                | UNEXT formula
                | EVENTUALLY formula
                | LEVENTUALLY formula
                | UEVENTUALLY formula
                | GLOBALLY formula
                | LGLOBALLY formula
                | UGLOBALLY formula
                | NOT formula
                | WNOT formula
                | TRUE
                | FALSE
                | TERM 
        '''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[1] = self.change[p[1]]
            p[0] = (p[1], p[2])

        elif len(p) == 4:
            p[2] = self.change[p[2]]
            if p[2] == '->':
                p[0] = ('|', ('~', p[1]), p[3])
            elif p[2] == '<->':
                p[0] = ('&', ('|', ('~', p[1]), p[3]), ('|', ('~', p[3]), p[1]))
            else:
                p[0] = (p[2], p[1], p[3])
        else:
            raise ValueError

    def p_expr_group(self, p):
        '''
        formula : LPAR formula RPAR
        '''
        p[0] = p[2]

    def p_error(self, p):
        raise ValueError(f"Syntax error in input! {p}")
