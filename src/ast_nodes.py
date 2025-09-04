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
    def __init__(self, declaracoes, expressaoFinal):
        self.declaracoes = declaracoes
        self.expressaoFinal = expressaoFinal

class Declaracao:
    def __init__(self, nomeVariavel, expressao):
        self.nomeVariavel = nomeVariavel
        self.expressao = expressao
        
class Var:
    def __init__(self, nomeVariavel):
        self.nomeVariavel = nomeVariavel



# Exemplo de uso
# raiz = Node("Raiz")
# filho1 = Node("Filho 1")
# filho2 = Node("Filho 2")
# neto1 = Node("Neto 1")

# raiz.add_child(filho1)
# raiz.add_child(filho2)
# filho1.add_child(neto1)

# raiz.print_tree()
