from .ast_nodes import * 
from .lexer import *

#from ast_nodes import * 
#from lexer import *

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

    def semantic_analysis(self, node):
        simbolos = set()

        def check_expr(expr):
            if isinstance(expr, Var):
                if expr.nomeVariavel not in simbolos:
                    raise Exception(f"Erro: variável '{expr.nomeVariavel}' não declarada")
            elif isinstance(expr, BinOp):
                check_expr(expr.left)
                check_expr(expr.right)
            elif isinstance(expr, Number):
                pass
            elif isinstance(expr, Comparacao):
                check_expr(expr.left)
                check_expr(expr.right)
            elif isinstance(expr, Return):
                check_expr(expr.expressao)
            # Adicione outros tipos de nós se necessário

        if isinstance(node, Programa):
            for decl in node.declaracoes:
                if isinstance(decl, Declaracao):
                    check_expr(decl.expressao)
                    simbolos.add(decl.nomeVariavel)
                elif isinstance(decl, If):
                    check_expr(decl.condicao)
                    # Verificar bloco if
                    for stmt in decl.bloco_if.statements:
                        if isinstance(stmt, Declaracao):
                            check_expr(stmt.expressao)
                            simbolos.add(stmt.nomeVariavel)
                    # Verificar bloco else se existir
                    if decl.bloco_else:
                        for stmt in decl.bloco_else.statements:
                            if isinstance(stmt, Declaracao):
                                check_expr(stmt.expressao)
                                simbolos.add(stmt.nomeVariavel)
                elif isinstance(decl, While):
                    check_expr(decl.condicao)
                    for stmt in decl.bloco.statements:
                        if isinstance(stmt, Declaracao):
                            check_expr(stmt.expressao)
                            simbolos.add(stmt.nomeVariavel)
                elif isinstance(decl, Bloco):
                    for stmt in decl.statements:
                        if isinstance(stmt, Declaracao):
                            check_expr(stmt.expressao)
                            simbolos.add(stmt.nomeVariavel)
                        elif isinstance(stmt, Return):
                            check_expr(stmt.expressao)
            
            # Verificar expressão final se existir
            if node.expressaoFinal:
                check_expr(node.expressaoFinal)
        else:
            raise Exception("AST não é um Programa")

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
                
                # Variável
                elif token.isidentifier():
                    return Var(token), index + 1
                
                # Número
                elif token.isdigit() or (token[0] == '-' and token[1:].isdigit() and (index == 0 or tokens[index-1] in ('(', '+', '-', '*', '/'))):
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
        
        def parse_comparacao(index):
            # Parse de comparações: expr OP expr
            left, index = parse_expr(index)
            
            if index < len(tokens) and tokens[index] in ('<', '>', '==', '!=', '<=', '>='):
                op = tokens[index]
                index += 1
                right, index = parse_expr(index)
                return Comparacao(left, op, right), index
            
            return left, index
        
        def parse_statement(index):
            # Parse de um statement (declaração, if, while, etc.)
            if index >= len(tokens):
                raise SyntaxError("Fim inesperado dos tokens")
            
            token = tokens[index]
            
            # Statement IF
            if token == 'if':
                index += 1
                if index >= len(tokens) or tokens[index] != '(':
                    raise SyntaxError("Esperado '(' após 'if'")
                index += 1
                
                # Parse da condição
                condicao, index = parse_comparacao(index)
                
                if index >= len(tokens) or tokens[index] != ')':
                    raise SyntaxError("Esperado ')' após condição do if")
                index += 1
                
                # Parse do bloco if
                bloco_if, index = parse_bloco(index)
                
                # Parse do else (opcional)
                bloco_else = None
                if index < len(tokens) and tokens[index] == 'else':
                    index += 1
                    bloco_else, index = parse_bloco(index)
                
                return If(condicao, bloco_if, bloco_else), index
            
            # Statement WHILE
            elif token == 'while':
                index += 1
                if index >= len(tokens) or tokens[index] != '(':
                    raise SyntaxError("Esperado '(' após 'while'")
                index += 1
                
                # Parse da condição
                condicao, index = parse_comparacao(index)
                
                if index >= len(tokens) or tokens[index] != ')':
                    raise SyntaxError("Esperado ')' após condição do while")
                index += 1
                
                # Parse do bloco
                bloco, index = parse_bloco(index)
                
                return While(condicao, bloco), index
            
            # Statement RETURN
            elif token == 'return':
                index += 1
                expr, index = parse_expr(index)
                if index < len(tokens) and tokens[index] == ';':
                    index += 1
                return Return(expr), index
            
            # Declaração de variável
            elif token.isidentifier() and index + 1 < len(tokens) and tokens[index + 1] == '=':
                return parse_declaracao(index)
            
            # Expressão simples (como um bloco {})
            elif token == '{':
                return parse_bloco(index)
            
            else:
                raise SyntaxError(f"Statement inválido: {token}")
        
        def parse_bloco(index):
            # Parse de um bloco entre chaves { }
            if index >= len(tokens) or tokens[index] != '{':
                # Bloco de uma única instrução (sem chaves)
                statement, index = parse_statement(index)
                return Bloco([statement]), index
            
            index += 1  # Pular '{'
            statements = []
            
            while index < len(tokens) and tokens[index] != '}':
                statement, index = parse_statement(index)
                statements.append(statement)
            
            if index >= len(tokens) or tokens[index] != '}':
                raise SyntaxError("Esperado '}' ao final do bloco")
            index += 1  # Pular '}'
            
            return Bloco(statements), index
        
        def parse_declaracao(index):
            # <ident> '=' <exp> ';'
            nome = tokens[index]
            index += 1
            if index >= len(tokens) or tokens[index] != '=':
                raise SyntaxError("Esperado '=' em declaração")
            index += 1
            expr, index = parse_expr(index)
            if index >= len(tokens) or tokens[index] != ';':
                raise SyntaxError("Esperado ';' ao final da declaração")
            index += 1
            return Declaracao(nome, expr), index
            
        # --- Aqui começa o parse do programa ---
        index = 0
        statements = []
        
        # Parse de todas as declarações e statements
        while index < len(tokens):
            if tokens[index].isidentifier() and index + 1 < len(tokens) and tokens[index + 1] == '=':
                # É uma declaração de variável
                decl, index = parse_declaracao(index)
                statements.append(decl)
            else:
                # É um statement de controle de fluxo ou bloco
                statement, index = parse_statement(index)
                statements.append(statement)
        
        # Verificar se sobrou algum token
        if index != len(tokens):
            raise SyntaxError(f"Tokens restantes após o fim do programa: {tokens[index:]}")
        
        return Programa(statements, None)  # Expressão final é opcional

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
            
            if node.expressaoFinal:
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

        # Suporte para If
        if isinstance(node, If):
            lines = ["If"]
            cond_lines, _, _, _ = self.build_tree_lines(node.condicao)
            lines += ["    Cond: " + l for l in cond_lines]
            
            lines.append("    Then:")
            for stmt in node.bloco_if.statements:
                stmt_lines, _, _, _ = self.build_tree_lines(stmt)
                lines += ["        " + l for l in stmt_lines]
            
            if node.bloco_else:
                lines.append("    Else:")
                for stmt in node.bloco_else.statements:
                    stmt_lines, _, _, _ = self.build_tree_lines(stmt)
                    lines += ["        " + l for l in stmt_lines]
            
            width = max(len(line) for line in lines)
            return lines, width, len(lines), width // 2

        # Suporte para While
        if isinstance(node, While):
            lines = ["While"]
            cond_lines, _, _, _ = self.build_tree_lines(node.condicao)
            lines += ["    Cond: " + l for l in cond_lines]
            
            lines.append("    Body:")
            for stmt in node.bloco.statements:
                stmt_lines, _, _, _ = self.build_tree_lines(stmt)
                lines += ["        " + l for l in stmt_lines]
            
            width = max(len(line) for line in lines)
            return lines, width, len(lines), width // 2

        # Suporte para Return
        if isinstance(node, Return):
            lines = ["Return"]
            expr_lines, _, _, _ = self.build_tree_lines(node.expressao)
            lines += ["    " + l for l in expr_lines]
            width = max(len(line) for line in lines)
            return lines, width, len(lines), width // 2

        # Suporte para Bloco
        if isinstance(node, Bloco):
            lines = ["Bloco"]
            for stmt in node.statements:
                stmt_lines, _, _, _ = self.build_tree_lines(stmt)
                lines += ["    " + l for l in stmt_lines]
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

        if isinstance(node, Comparacao):
            left_lines, left_width, left_height, left_middle = self.build_tree_lines(node.left)
            right_lines, right_width, right_height, right_middle = self.build_tree_lines(node.right)

            val_str = f"Comp {node.op}"
            val_width = len(val_str)

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

            height = max(left_height, right_height)
            left_lines += [' ' * left_width] * (height - left_height)
            right_lines += [' ' * right_width] * (height - right_height)

            combined = []
            for i in range(height):
                left_line = left_lines[i] if i < left_height else ' ' * left_width
                right_line = right_lines[i] if i < right_height else ' ' * right_width
                combined.append(left_line + ' ' * val_width + right_line)

            return [first_line, second_line] + combined, left_width + val_width + right_width, height + 2, left_width + val_width // 2

        raise TypeError(f"Tipo de nó não suportado: {type(node).__name__}")
    
    # Fim

def main():
    parser = Parser()
   
    arquivo = None
    with open("./tests/test3.cmd", "r") as f:
        arquivo = f.read()


    parser.lexic_analyse(arquivo)
   
    root = parser.parse(parser.tokenlist)
    
     # Análise semântica
    try:
        parser.semantic_analysis(root)
        print("Análise semântica concluída sem erros.")
    except Exception as e:
        print(e)

    parser.print_ast_tree(root)


if __name__ == "__main__":
    main()
    input()