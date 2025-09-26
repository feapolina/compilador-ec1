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
    def __init__(self, declaracoes, expressaoFinal=None):  # expressaoFinal é opcional
        self.declaracoes = declaracoes
        self.expressaoFinal = expressaoFinal

class Declaracao:
    def __init__(self, nomeVariavel, expressao):
        self.nomeVariavel = nomeVariavel
        self.expressao = expressao
        
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

# Exemplo de uso
# raiz = Node("Raiz")
# filho1 = Node("Filho 1")
# filho2 = Node("Filho 2")
# neto1 = Node("Neto 1")

# raiz.add_child(filho1)
# raiz.add_child(filho2)
# filho1.add_child(neto1)

# raiz.print_tree()
