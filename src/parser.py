from .ast_nodes import * 
from .lexer import *
import traceback
import sys

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
        # Dicionário de funções declaradas: nome -> Funcao
        funcoes_declaradas = {}
        erros = []
        
        def verificar_funcao(funcao, escopo_pai=None):
            """Verifica uma função individual com seu próprio escopo"""
            nonlocal erros
            
            # Criar novo escopo para a função
            escopo = {
                'parent': escopo_pai,
                'variaveis': set(),
                'parametros': set(funcao.parametros),
                'funcao_atual': funcao.nome
            }
            
            # Adicionar parâmetros ao escopo
            for param in funcao.parametros:
                escopo['variaveis'].add(param)
            
            def verificar_expr(expr, escopo_atual):
                """Verifica uma expressão dentro de um escopo"""
                nonlocal erros
                
                if isinstance(expr, Var):
                    # Verificar se variável existe no escopo atual ou pais
                    escopo_temp = escopo_atual
                    while escopo_temp:
                        if expr.nomeVariavel in escopo_temp['variaveis'] or expr.nomeVariavel in escopo_temp['parametros']:
                            return
                        escopo_temp = escopo_temp['parent']
                    erros.append(f"Variável '{expr.nomeVariavel}' não declarada na função '{escopo_atual['funcao_atual']}'")
                
                elif isinstance(expr, ChamadaFuncao):
                    # Verificar se função existe
                    if expr.nome not in funcoes_declaradas and expr.nome != escopo_atual['funcao_atual']:
                        erros.append(f"Função '{expr.nome}' não declarada")
                    
                    # Verificar número de argumentos
                    if expr.nome in funcoes_declaradas:
                        funcao_chamada = funcoes_declaradas[expr.nome]
                        if len(expr.argumentos) != len(funcao_chamada.parametros):
                            erros.append(f"Função '{expr.nome}' espera {len(funcao_chamada.parametros)} argumentos, mas {len(expr.argumentos)} foram fornecidos")
                    
                    # Verificar cada argumento
                    for arg in expr.argumentos:
                        verificar_expr(arg, escopo_atual)
                
                elif isinstance(expr, BinOp):
                    verificar_expr(expr.left, escopo_atual)
                    verificar_expr(expr.right, escopo_atual)
                
                elif isinstance(expr, Comparacao):
                    verificar_expr(expr.left, escopo_atual)
                    verificar_expr(expr.right, escopo_atual)
                
                elif isinstance(expr, Number):
                    pass  # Números são sempre válidos
                
                elif isinstance(expr, Return):
                    verificar_expr(expr.expressao, escopo_atual)
                
                else:
                    erros.append(f"Tipo de expressão não suportado: {type(expr).__name__}")
            
            def verificar_statement(stmt, escopo_atual):
                """Verifica um statement dentro de um escopo"""
                nonlocal erros
                
                if isinstance(stmt, Declaracao):
                    # Verificar a expressão da declaração
                    verificar_expr(stmt.expressao, escopo_atual)
                    
                    # Verificar se variável já foi declarada no mesmo escopo
                    if stmt.nomeVariavel in escopo_atual['variaveis'] or stmt.nomeVariavel in escopo_atual['parametros']:
                        erros.append(f"Variável '{stmt.nomeVariavel}' já declarada no escopo atual")
                    else:
                        escopo_atual['variaveis'].add(stmt.nomeVariavel)
                
                elif isinstance(stmt, Return):
                    verificar_expr(stmt.expressao, escopo_atual)
                
                elif isinstance(stmt, If):
                    verificar_expr(stmt.condicao, escopo_atual)
                    
                    # Verificar bloco if (com escopo separado para evitar conflitos)
                    escopo_if = {'parent': escopo_atual, 'variaveis': set(), 'parametros': set(), 'funcao_atual': escopo_atual['funcao_atual']}
                    for sub_stmt in stmt.bloco_if.statements:
                        verificar_statement(sub_stmt, escopo_if)  # Usar escopo_if, não escopo_atual
                    
                    # Verificar bloco else se existir
                    if stmt.bloco_else:
                        escopo_else = {'parent': escopo_atual, 'variaveis': set(), 'parametros': set(), 'funcao_atual': escopo_atual['funcao_atual']}
                        for sub_stmt in stmt.bloco_else.statements:
                            verificar_statement(sub_stmt, escopo_else)  # Usar escopo_else
                
                elif isinstance(stmt, While):
                    verificar_expr(stmt.condicao, escopo_atual)
                    
                    # Verificar bloco while (com escopo separado)
                    escopo_while = {'parent': escopo_atual, 'variaveis': set(), 'parametros': set(), 'funcao_atual': escopo_atual['funcao_atual']}
                    for sub_stmt in stmt.bloco.statements:
                        verificar_statement(sub_stmt, escopo_while)  # Usar escopo_while
                
                elif isinstance(stmt, Bloco):
                    # Bloco cria novo escopo
                    escopo_bloco = {'parent': escopo_atual, 'variaveis': set(), 'parametros': set(), 'funcao_atual': escopo_atual['funcao_atual']}
                    for sub_stmt in stmt.statements:
                        verificar_statement(sub_stmt, escopo_bloco)
                
                # ADICIONAR: Suporte a atribuições simples (sem 'var')
                elif isinstance(stmt, Declaracao) and not hasattr(stmt, 'tipo'):
                    # Isso é uma atribuição, não uma declaração
                    verificar_expr(stmt.expressao, escopo_atual)
                    # Verificar se variável existe
                    escopo_temp = escopo_atual
                    while escopo_temp:
                        if stmt.nomeVariavel in escopo_temp['variaveis'] or stmt.nomeVariavel in escopo_temp['parametros']:
                            break
                        escopo_temp = escopo_temp['parent']
                    else:
                        erros.append(f"Variável '{stmt.nomeVariavel}' não declarada")
                
                elif isinstance(stmt, ChamadaFuncao):
                    verificar_expr(stmt, escopo_atual)

                elif isinstance(stmt, Atribuicao):
                    # Verificar a expressão
                    verificar_expr(stmt.expressao, escopo_atual)
                    # Verificar se variável existe
                    escopo_temp = escopo_atual
                    while escopo_temp:
                        if stmt.nomeVariavel in escopo_temp['variaveis'] or stmt.nomeVariavel in escopo_temp['parametros']:
                            break
                        escopo_temp = escopo_temp['parent']
                    else:
                        erros.append(f"Variável '{stmt.nomeVariavel}' não declarada")
                
                else:
                    erros.append(f"Tipo de statement não suportado: {type(stmt).__name__}")

            
            # Verificar corpo da função
            for stmt in funcao.corpo.statements:
                verificar_statement(stmt, escopo)
        
        def verificar_funcao_main(funcao_main):
            """Verificações específicas para a função main"""
            nonlocal erros
            
            # Verificar se main não tem parâmetros
            if funcao_main.parametros:
                erros.append("Função 'main' não deve ter parâmetros")
            
            # Verificar se main tem return (opcional, mas recomendado)
            tem_return = any(isinstance(stmt, Return) for stmt in funcao_main.corpo.statements)
            if not tem_return:
                # Apenas um aviso, não um erro
                print("Aviso: função 'main' não tem instrução 'return'")
        
        # --- Análise semântica principal ---
        if not isinstance(node, Programa):
            raise Exception("AST não é um Programa")
        
        # Fase 1: Coletar declarações de funções
        for funcao in node.funcoes:
            if funcao.nome in funcoes_declaradas:
                erros.append(f"Função '{funcao.nome}' já declarada")
            else:
                funcoes_declaradas[funcao.nome] = funcao
        
        # Adicionar main às funções declaradas para permitir chamadas recursivas indiretas
        funcoes_declaradas['main'] = node.funcao_main
        
        # Fase 2: Verificar cada função individualmente
        for funcao in node.funcoes:
            verificar_funcao(funcao)
        
        # Verificar função main
        verificar_funcao(node.funcao_main)
        verificar_funcao_main(node.funcao_main)
        
        # Verificar se há chamadas a funções não declaradas
        # (já feito durante a verificação das expressões)
        
        # Reportar erros
        if erros:
            for erro in erros:
                print(f"Erro semântico: {erro}")
            raise Exception("Análise semântica falhou")
        
        print("Análise semântica concluída com sucesso!")

    def parse(self, tokens):
        
        def parse_expr(index):
            # Parse de expressões com precedência
            def parse_term(index):
                # Parse de termos (fatores com * e /)
                left, index = parse_factor(index)
                
                while index < len(tokens) and tokens[index] in ('*', '/', '%'):
                    op = tokens[index]
                    index += 1
                    right, index = parse_factor(index)
                    left = BinOp(left, op, right)
                
                return left, index
            
            def parse_factor(index):
                # Parse de fatores (números, variáveis, chamadas de função, ou expressões entre parênteses)
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
                
                # Chamada de função
                elif token.isidentifier() and index + 1 < len(tokens) and tokens[index + 1] == '(':
                    nome_funcao = token
                    index += 2  # pular nome e '('
                    argumentos = []
                    
                    # Parse dos argumentos (se houver)
                    if index < len(tokens) and tokens[index] != ')':
                        while True:
                            expr, index = parse_expr(index)
                            argumentos.append(expr)
                            
                            if index >= len(tokens) or tokens[index] != ',':
                                break
                            index += 1  # pular a vírgula
                    
                    if index >= len(tokens) or tokens[index] != ')':
                        raise SyntaxError("Esperado ')' após argumentos da função")
                    index += 1
                    
                    return ChamadaFuncao(nome_funcao, argumentos), index
                
                # Variável
                elif token.isidentifier():
                    return Var(token), index + 1
                
                # Número
                elif token.isdigit() or (token[0] == '-' and token[1:].isdigit() and (index == 0 or tokens[index-1] in ('(', '+', '-', '*', '/'))):
                    return Number(int(token)), index + 1
                
                else:
                    raise SyntaxError(f"Token inesperado em expressão: {token}")
            
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
        
        def parse_declaracao_variavel(index):
            # 'var' <ident> '=' <exp> ';'
            if tokens[index] != 'var':
                raise SyntaxError("Esperado 'var' antes da declaração de variável")
            index += 1
            
            if index >= len(tokens) or not tokens[index].isidentifier():
                raise SyntaxError("Esperado identificador após 'var'")
            
            nome = tokens[index]
            index += 1
            
            if index >= len(tokens) or tokens[index] != '=':
                raise SyntaxError("Esperado '=' em declaração")
            index += 1
            
            expr, index = parse_expr(index)
            
            if index >= len(tokens) or tokens[index] != ';':
                raise SyntaxError("Esperado ';' ao final da declaração")
            index += 1
            
            return Declaracao(nome, expr, 'var'), index
        
        def parse_bloco(index):
            # Parse de um bloco entre chaves { }
            if index >= len(tokens) or tokens[index] != '{':
                raise SyntaxError("Esperado '{' para início de bloco")
            
            index += 1  # Pular '{'
            statements = []
            
            while index < len(tokens) and tokens[index] != '}':
                if tokens[index] == 'var':
                    # Declaração de variável
                    decl, index = parse_declaracao_variavel(index)
                    statements.append(decl)
                elif tokens[index] in ('if', 'while', 'return'):
                    # Statement de controle
                    stmt, index = parse_statement(index)
                    statements.append(stmt)
                elif tokens[index] == '{':
                    # Bloco aninhado
                    bloco, index = parse_bloco(index)
                    statements.append(bloco)
                else:
                    # Expressão simples (atribuição ou chamada de função)
                    if (index + 1 < len(tokens) and tokens[index].isidentifier() and 
                        (tokens[index + 1] == '=' or tokens[index + 1] == '(')):
                        stmt, index = parse_statement(index)
                        statements.append(stmt)
                    else:
                        raise SyntaxError(f"Statement inválido no bloco: {tokens[index]}")
            
            if index >= len(tokens) or tokens[index] != '}':
                raise SyntaxError("Esperado '}' ao final do bloco")
            index += 1  # Pular '}'
            
            return Bloco(statements), index
        
        def parse_statement(index):
            # Parse de um statement
            if index >= len(tokens):
                raise SyntaxError("Fim inesperado dos tokens")
            
            token = tokens[index]
            
            # Statement IF
            if token == 'if':
                index += 1
                if index >= len(tokens) or tokens[index] != '(':
                    raise SyntaxError("Esperado '(' após 'if'")
                index += 1
                
                condicao, index = parse_comparacao(index)
                
                if index >= len(tokens) or tokens[index] != ')':
                    raise SyntaxError("Esperado ')' após condição do if")
                index += 1
                
                bloco_if, index = parse_bloco(index)
                
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
                
                condicao, index = parse_comparacao(index)
                
                if index >= len(tokens) or tokens[index] != ')':
                    raise SyntaxError("Esperado ')' após condição do while")
                index += 1
                
                bloco, index = parse_bloco(index)
                
                return While(condicao, bloco), index
            
            # Statement RETURN
            elif token == 'return':
                index += 1
                expr, index = parse_expr(index)
                if index < len(tokens) and tokens[index] == ';':
                    index += 1
                return Return(expr), index
            
            elif token == 'var':
                return parse_declaracao_variavel(index)

            # Atribuição de variável (sem 'var')
            elif token.isidentifier() and index + 1 < len(tokens) and tokens[index + 1] == '=':
                nome = token
                index += 2  # pular nome e '='
                expr, index = parse_expr(index)
                if index < len(tokens) and tokens[index] == ';':
                    index += 1
                return Atribuicao(nome, expr), index
            
            # Chamada de função como statement
            elif token.isidentifier() and index + 1 < len(tokens) and tokens[index + 1] == '(':
                chamada, index = parse_expr(index)  # Reusa parse_expr para chamadas
                if index < len(tokens) and tokens[index] == ';':
                    index += 1
                return chamada, index
            
            else:
                raise SyntaxError(f"Statement inválido: {token}")
        
        def parse_parametros_funcao(index):
            # Parse da lista de parâmetros: (var id1, var id2, ...)
            if index >= len(tokens) or tokens[index] != '(':
                raise SyntaxError("Esperado '(' para parâmetros da função")
            index += 1
            
            parametros = []
            
            # Se não há parâmetros
            if index < len(tokens) and tokens[index] == ')':
                return parametros, index + 1
            
            # Parse dos parâmetros
            while index < len(tokens):
                if tokens[index] != 'var':
                    raise SyntaxError("Esperado 'var' antes do parâmetro")
                index += 1
                
                if index >= len(tokens) or not tokens[index].isidentifier():
                    raise SyntaxError("Esperado nome do parâmetro após 'var'")
                
                parametros.append(tokens[index])
                index += 1
                
                if index < len(tokens) and tokens[index] == ')':
                    break
                elif index < len(tokens) and tokens[index] == ',':
                    index += 1
                else:
                    raise SyntaxError("Esperado ',' ou ')' após parâmetro")
            
            if index >= len(tokens) or tokens[index] != ')':
                raise SyntaxError("Esperado ')' após parâmetros")
            index += 1
            
            return parametros, index
        
        def parse_funcao(index):
            # 'fun' <ident> '(' parametros ')' bloco
            if tokens[index] != 'fun':
                raise SyntaxError("Esperado 'fun' para declaração de função")
            index += 1
            
            if index >= len(tokens) or not tokens[index].isidentifier():
                raise SyntaxError("Esperado nome da função após 'fun'")
            
            nome = tokens[index]
            index += 1
            
            # Parse dos parâmetros
            parametros, index = parse_parametros_funcao(index)
            
            # Parse do corpo da função
            corpo, index = parse_bloco(index)
            
            return Funcao(nome, parametros, corpo), index
        
        # --- Parse principal do programa ---
        index = 0
        funcoes = []
        funcao_main = None
        
        # Parse de todas as funções
        while index < len(tokens) and tokens[index] == 'fun':
            funcao, index = parse_funcao(index)
            
            if funcao.nome == 'main':
                if funcao_main is not None:
                    raise SyntaxError("Só pode haver uma função 'main'")
                funcao_main = funcao
            else:
                funcoes.append(funcao)
        
        if funcao_main is None:
            raise SyntaxError("Função 'main' não encontrada")
        
        # Verificar se sobrou algum token
        if index != len(tokens):
            raise SyntaxError(f"Tokens restantes após parse: {tokens[index:]}")
        
        return Programa(funcoes, funcao_main)

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
            tb = e.__traceback__
            ultimo_frame = traceback.extract_tb(tb)[-1]
            print(f"""
                  Erro ao imprimir árvore: {e}\nLocal: {ultimo_frame.filename}\nLinha: {ultimo_frame.line}
""")

    def build_tree_lines(self, node):
        if node is None:
            return [""], 0, 1, 0
        
        # Suporte para Programa
        if isinstance(node, Programa):
            lines = ["Programa"]
            children_lines = []
            for func in node.funcoes:
                func_lines, _, _, _ = self.build_tree_lines(func)
                children_lines += ["    " + l for l in func_lines]
            
            if node.funcao_main:
                main_lines, _, _, _ = self.build_tree_lines(node.funcao_main)
                children_lines += ["    " + l for l in main_lines]
            
            lines += children_lines
            width = max(len(line) for line in lines)
            return lines, width, len(lines), width // 2
        
        # Suporte para Funcao

        if isinstance(node, Funcao):
            lines = [f"Funcao {node.nome}"]

            if node.parametros:
                lines.append("    Parametros:")
                for p in node.parametros:
                    lines.append(f"        {p}")
            
            if node.corpo:
                lines.append("    Corpo:")
                corpo_lines, _, _, _ = self.build_tree_lines(node.corpo)
                lines += ["        " + l for l in corpo_lines]
                
            width = max(len(line) for line in lines)
            return lines, width, len(lines), width // 2

        # Suporte para Declaracao
        if isinstance(node, Declaracao):
            lines = [f"Declaracao {node.nomeVariavel}"]
            expr_lines, _, _, _ = self.build_tree_lines(node.expressao)
            lines += ["    " + l for l in expr_lines]
            width = max(len(line) for line in lines)
            return lines, width, len(lines), width // 2
        
        # Suporte para Atribuicao
        if isinstance(node, Atribuicao):
            lines = [f"Atribuicao {node.nomeVariavel}"]
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
    with open("./tests/test4.cmd", "r") as f:
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