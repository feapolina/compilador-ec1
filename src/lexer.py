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

    def proximo_token(self):
        while self.pos < self.length and self.texto[self.pos].isspace():
            self.pos += 1

        if self.pos >= self.length:
            return None

        c = self.texto[self.pos]

        if c.isdigit():
            start = self.pos
            while self.pos < self.length and self.texto[self.pos].isdigit():
                self.pos += 1
            return Token("Numero", self.texto[start:self.pos], start)
        
        # Identificadores: começam com letra, podem conter números e letras
        elif c.isalpha():
            start = self.pos
            while self.pos < self.length and (self.texto[self.pos].isalnum()):
                self.pos += 1
            return Token("Id", self.texto[start:self.pos], start)

        elif c == '(':
            self.pos += 1
            return Token("ParenEsq", "(", self.pos - 1)

        elif c == ')':
            self.pos += 1
            return Token("ParenDir", ")", self.pos - 1)

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
        
        elif c == '=':
            self.pos += 1
            return Token("Igual", "=", self.pos - 1)
        
        elif c == ';':
            self.pos += 1
            return Token("PontoVirgula", ";", self.pos - 1)

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
    arquivo_entrada = "entrada.ec1"

    with open(arquivo_entrada, "r") as f:
        conteudo = f.read()

    lexer = Lexer(conteudo)
    try:
        tokens = lexer.analisar()
        for token in tokens:
            print(token)
    except Exception as e:
        print(e)
