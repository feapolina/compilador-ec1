from os import system
from BinTree import * 
from atv4 import *

class Parser:

    def __init__(self):
        self.obj = None
        self.ast_test = None
        self.code = None
        self.tokens = []
        self.tokenlist = []
    
    def lexic_analyse(self, text=""): # Deve retornar os tokens
        self.lexer = Lexer(text)
        self.tokens.clear()
        self.tokenlist.clear()
        
        try:
            self.tokens = self.lexer.analisar()
            self.tokenlist = [token.lexema for token in self.tokens]
        except Exception as e:
            print(e)

    def parse(self, tokens):
        def parse_expr(index):
            # Parse de expressões com precedência
            def parse_term(index):
                # Parse de termos (fatores com * e /)
                left, index = parse_factor(index)
                
                while index < len(tokens) and tokens[index] in ('*', '/'):
                    op = tokens[index]
                    index += 1
                    right, index = parse_factor(index)
                    left = BinOp(left, op, right)
                
                return left, index
            
            def parse_factor(index):
                # Parse de fatores (números ou expressões entre parênteses)
                if index >= len(tokens):
                    raise SyntaxError("Fim inesperado dos tokens")
                
                token = tokens[index]

                # Parênteses
                if token == '(':
                    index += 1
                    expr, index = parse_expr(index)
                    if index >= len(tokens) or tokens[index] != ')':
                        raise SyntaxError(f"Esperado ')', mas achou {tokens[index] if index < len(tokens) else 'EOF'}")
                    return expr, index + 1
                
                #Variável
                elif token.isidentifier():
                    return Var(token), index + 1
                
                # Número
                elif token.isdigit() or (token[0] == '-' and token[1:].isdigit() and (index == 0 or tokens[index-1] in ('(', '+', '-', '*', '/'))):
                    # Números (incluindo números negativos quando a1priado)
                    return Number(int(token)), index + 1
                
                else:
                    raise SyntaxError(f"Token inesperado: {token}")
            
            # Parse da expressão principal (termos com + e -)
            left, index = parse_term(index)
            
            while index < len(tokens) and tokens[index] in ('+', '-'):
                op = tokens[index]
                index += 1
                right, index = parse_term(index)
                left = BinOp(left, op, right)
            
            return left, index
        
        def parse_declaracao(index):
            # <ident> '=' <exp> ';'
            nome = tokens[index]
            index += 1
            if tokens[index] != '=':
                raise SyntaxError("Esperado '=' em declaração")
            index += 1
            expr, index = parse_expr(index)
            if tokens[index] != ';':
                raise SyntaxError("Esperado ';' ao final da declaração")
            index += 1
            return Declaracao(nome, expr), index

        def parse_resultado(index):
            # '=' <exp>
            if tokens[index] != '=':
                raise SyntaxError("Esperado '=' no início do resultado")
            index += 1
            expr, index = parse_expr(index)
            return expr, index
            
        # --- Aqui começa o parse do programa ---
        index = 0
        declaracoes = []
        while index < len(tokens) and tokens[index].isidentifier():
            decl, index = parse_declaracao(index)
            declaracoes.append(decl)
        if index >= len(tokens) or tokens[index] != '=':
            raise SyntaxError("Esperado '=' para expressão final")
        expFinal, index = parse_resultado(index)
        if index != len(tokens):
            raise SyntaxError("Tokens restantes após o fim do programa")
        return Programa(declaracoes, expFinal)
        
        try:
            if not tokens:
                return None
                
            ast, next_index = parse_expr(0)
            if next_index != len(tokens):
                raise SyntaxError(f"Tokens restantes após o fim da análise: {tokens[next_index:]}")
            return ast
        except Exception as e:
            print(f"Erro na análise sintática: {e}")
            return None

    def print_ast(self, node, indent=0, last=False):
        if node is None:
            return
            
        prefix = ' ' * indent
        connector = "└── " if last else "├── "
        print(prefix + connector, end="")

        
        if isinstance(node, Programa):
            print("Programa")
            for i, decl in enumerate(node.declaracoes):
                self.print_ast(decl, indent + 4, False)
            self.print_ast(node.expFinal, indent + 4, True)
        elif isinstance(node, Declaracao):
            print(f"Declaracao {node.nome_variavel}")
            self.print_ast(node.expressao, indent + 4, True)
        elif isinstance(node, Var):
            print(f"Var {node.nome_variavel}")
        elif isinstance(node, Number):
            print(f"{node.value}")
        elif isinstance(node, BinOp):
            print(f"{node.op}")
            self.print_ast(node.left, indent + 4, False)
            self.print_ast(node.right, indent + 4, True)
        elif isinstance(node, list):
            print(f"Group")
            for i, child in enumerate(node):
                self.print_ast(child, indent + 4, i == len(node) - 1)
        else:
            print(f"Desconhecido: {type(node)}")

    def build_tree_lines(self, node):
        if node is None:
            return [""], 0, 1, 0
        
        # Suporte para Programa
        if isinstance(node, Programa):
            lines = ["Programa"]
            children_lines = []
            for decl in node.declaracoes:
                decl_lines, _, _, _ = self.build_tree_lines(decl)
                children_lines += ["    " + l for l in decl_lines]
            exp_lines, _, _, _ = self.build_tree_lines(node.expressaoFinal)
            children_lines += ["    " + l for l in exp_lines]
            lines += children_lines
            width = max(len(line) for line in lines)
            return lines, width, len(lines), width // 2

        # Suporte para Declaracao
        if isinstance(node, Declaracao):
            lines = [f"Declaracao {node.nomeVariavel}"]
            expr_lines, _, _, _ = self.build_tree_lines(node.expressao)
            lines += ["    " + l for l in expr_lines]
            width = max(len(line) for line in lines)
            return lines, width, len(lines), width // 2

        # Suporte para Var
        if isinstance(node, Var):
            s = f"Var {node.nomeVariavel}"
            width = len(s)
            return [s], width, 1, width // 2
            
        if isinstance(node, Number):
            s = str(node.value)
            width = len(s)
            return [s], width, 1, width // 2

        if isinstance(node, BinOp):
            left_lines, left_width, left_height, left_middle = self.build_tree_lines(node.left)
            right_lines, right_width, right_height, right_middle = self.build_tree_lines(node.right)

            val_str = str(node.op)
            val_width = len(val_str)

            # Corrigindo a formatação da árvore
            first_line = (
                ' ' * left_middle +
                ' ' * (left_width - left_middle) +
                val_str +
                ' ' * right_middle +
                ' ' * (right_width - right_middle)
            )

            second_line = (
                ' ' * left_middle + '/' +
                ' ' * (left_width - left_middle - 1 + val_width) + '\\' +
                ' ' * (right_middle)
            )

            # Ajustar as linhas para terem a mesma altura
            height = max(left_height, right_height)
            left_lines += [' ' * left_width] * (height - left_height)
            right_lines += [' ' * right_width] * (height - right_height)

            # Combinar as linhas
            combined = []
            for i in range(height):
                left_line = left_lines[i] if i < left_height else ' ' * left_width
                right_line = right_lines[i] if i < right_height else ' ' * right_width
                combined.append(left_line + ' ' * val_width + right_line)

            return [first_line, second_line] + combined, left_width + val_width + right_width, height + 2, left_width + val_width // 2

        elif isinstance(node, list):
            if not node:
                return [""], 0, 1, 0
            lines = ["Group"]
            total_width = len("Group")
            max_height = 1
            return lines, total_width, max_height, total_width // 2
        
        raise TypeError(f"Tipo de nó não suportado: {type(node).__name__}")

    def print_ast_tree(self, node):
        try:
            if node is None:
                print("Árvore sintática vazia")
                return
                
            lines, *_ = self.build_tree_lines(node)
            for line in lines:
                print(line)
        except Exception as e:
            print(f"Erro ao imprimir árvore: {e}")


def main():
    paser = Parser()
   
    arquivo = None
    with open("tests/teste5.ec1", "r") as f:
        arquivo = f.read()


    paser.lexic_analyse(arquivo)
   
    root = paser.parse(paser.tokenlist)
    
    paser.print_ast_tree(root)


if __name__ == "__main__":
    main()
    input()