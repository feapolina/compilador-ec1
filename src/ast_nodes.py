class Node:
    pass

class Number(Node):
    def __init__(self, value):
        self.value = value

class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Programa:
    def __init__(self, funcoes, funcao_main):
        self.funcoes = funcoes  # lista de Funcao
        self.funcao_main = funcao_main  # Funcao (a main)

class Declaracao:
    def __init__(self, nomeVariavel, expressao, tipo='var'):
        self.nomeVariavel = nomeVariavel
        self.expressao = expressao
        self.tipo = tipo  # 'var' para declarações com var

class Var:
    def __init__(self, nomeVariavel):
        self.nomeVariavel = nomeVariavel

class If(Node):
    def __init__(self, condicao, bloco_if, bloco_else=None):
        self.condicao = condicao
        self.bloco_if = bloco_if  # lista de statements
        self.bloco_else = bloco_else  # lista de statements (opcional)

class While(Node):
    def __init__(self, condicao, bloco):
        self.condicao = condicao
        self.bloco = bloco  # lista de statements

class Comparacao(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Bloco(Node):
    def __init__(self, statements):
        self.statements = statements  # lista de statements

class Return(Node):
    def __init__(self, expressao):
        self.expressao = expressao

class Funcao(Node):
    def __init__(self, nome, parametros, corpo):
        self.nome = nome
        self.parametros = parametros  # lista de strings com nomes dos parâmetros
        self.corpo = corpo  # Bloco (contém statements da função)

class ChamadaFuncao(Node):
    def __init__(self, nome, argumentos):
        self.nome = nome
        self.argumentos = argumentos  # lista de expressões (argumentos passados)

class Parametro(Node):
    def __init__(self, nome, tipo='var'):
        self.nome = nome
        self.tipo = tipo

# Removido Exemplos de Uso