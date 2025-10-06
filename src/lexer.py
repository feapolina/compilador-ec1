import re

class Token:
    def __init__(self, tipo, lexema, posicao):
        self.tipo = tipo
        self.lexema = lexema
        self.posicao = posicao

    def __repr__(self):
        return f"<{self.tipo}, \"{self.lexema}\", {self.posicao}>"

class Lexer:
    def __init__(self, texto):
        self.texto = texto
        self.pos = 0
        self.length = len(texto)
        
        # Palavras-chave da linguagem
        self.palavras_chave = {
            'fun': 'Fun',
            'var': 'Var', 
            'main': 'Main',
            'return': 'Return',
            'if': 'If',
            'else': 'Else',
            'while': 'While'
        }

    def proximo_token(self):
        while self.pos < self.length and self.texto[self.pos].isspace():
            self.pos += 1

        if self.pos >= self.length:
            return None

        c = self.texto[self.pos]

        # Números
        if c.isdigit():
            start = self.pos
            while self.pos < self.length and self.texto[self.pos].isdigit():
                self.pos += 1
            return Token("Numero", self.texto[start:self.pos], start)
        
        # Identificadores e palavras-chave
        elif c.isalpha() or c == '_':
            start = self.pos
            # Permite letras, números e underscores
            while self.pos < self.length and (self.texto[self.pos].isalnum() or self.texto[self.pos] == '_'):
                self.pos += 1
            
            palavra = self.texto[start:self.pos]
            
            # Verifica se é palavra-chave
            if palavra in self.palavras_chave:
                return Token(self.palavras_chave[palavra], palavra, start)
            else:
                return Token("Id", palavra, start)

        # Operadores e símbolos (mantendo o código existente)
        elif c == '(':
            self.pos += 1
            return Token("ParenEsq", "(", self.pos - 1)

        elif c == ')':
            self.pos += 1
            return Token("ParenDir", ")", self.pos - 1)

        elif c == '{':
            self.pos += 1
            return Token("ChaveEsq", "{", self.pos - 1)

        elif c == '}':
            self.pos += 1
            return Token("ChaveDir", "}", self.pos - 1)

        elif c == '+':
            self.pos += 1
            return Token("Soma", "+", self.pos - 1)

        elif c == '-':
            self.pos += 1
            return Token("Sub", "-", self.pos - 1)

        elif c == '*':
            self.pos += 1
            return Token("Mult", "*", self.pos - 1)

        elif c == '/':
            self.pos += 1
            return Token("Div", "/", self.pos - 1)
        
        elif c == '%':
            self.pos += 1
            return Token("Mod", "%", self.pos - 1)
        
        elif c == '=':
            self.pos += 1
            if self.pos < self.length and self.texto[self.pos] == "=":
                self.pos += 1
                return Token("IgualIgual", "==", self.pos - 2)
            else:
                return Token("Igual", "=", self.pos - 1)

        elif c == '>':
            self.pos += 1
            if self.pos < self.length and self.texto[self.pos] == "=":
                self.pos += 1
                return Token("MaiorIgual", ">=", self.pos - 2)
            else:
                return Token("Maior", ">", self.pos - 1)

        elif c == '<':
            self.pos += 1
            if self.pos < self.length and self.texto[self.pos] == "=":
                self.pos += 1
                return Token("MenorIgual", "<=", self.pos - 2)
            else:
                return Token("Menor", "<", self.pos - 1)
        
        elif c == '!':
            self.pos += 1
            if self.pos < self.length and self.texto[self.pos] == "=":
                self.pos += 1
                return Token("Diferente", "!=", self.pos - 2)
            else:
                raise Exception(f"Erro léxico na posição {self.pos}: '!' deve ser seguido de '='")
        
        elif c == ';':
            self.pos += 1
            return Token("PontoVirgula", ";", self.pos - 1)

        elif c == ',':
            self.pos += 1
            return Token("Virgula", ",", self.pos - 1)

        else:
            raise Exception(f"Erro léxico na posição {self.pos}: caractere inválido '{c}'")

    def analisar(self):
        tokens = []
        while True:
            token = self.proximo_token()
            if token is None:
                break
            tokens.append(token)
        return tokens

# Teste básico
if __name__ == "__main__":
    arquivo_entrada = "tests/test4.cmd"

    with open(arquivo_entrada, "r") as f:
        conteudo = f.read()

    lexer = Lexer(conteudo)
    try:
        tokens = lexer.analisar()
        for token in tokens:
            print(token)
    except Exception as e:
        print(e)
