from .ast_nodes import *
from .parser import *

#from ast_nodes import *
#from parser import *

class Compiler:

    def __init__(self):
        self.version = "1.0"
        self.code = None
        self.tree = None
        self.label_counter = 0  # Contador para labels únicos

    def io(self, text="Hello World!\nCompilers", filename="exemple.s"):
        try:
            obj_file = open(filename, "x")
            obj_file.close()
        except:
            print("Erro: Arquivo com esse nome já existe (ou não foi possível criar com 'x')")

        obj_file = open(filename, "w")
        obj_file.write(text)
        obj_file.close()

    def read_file(self, path):
        with open(path, "r") as f:
            self.code = f.read()

    def novo_label(self):
        """Gera um novo label único"""
        self.label_counter += 1
        return f"L{self.label_counter}"

    def compile(self):

        def gerar_codigo_funcao(funcao, code):
            """Gera código para uma função individual"""
            nonlocal label_counter
            
            code[0] += f"\n\n# Função {funcao.nome}"
            code[0] += f"\n.globl {funcao.nome}"
            code[0] += f"\n{funcao.nome}:"
            
            # Prologue
            code[0] += "\n    push %rbp"
            code[0] += "\n    mov %rsp, %rbp"
            
            # Calcular espaço para variáveis locais
            variaveis_locais = []
            for stmt in funcao.corpo.statements:
                if isinstance(stmt, Declaracao):
                    variaveis_locais.append(stmt.nomeVariavel)
            
            if variaveis_locais:
                code[0] += f"\n    sub ${len(variaveis_locais) * 8}, %rsp"
            
            # Mapeamento de variáveis
            mapa_variaveis = {}
            
            # Parâmetros: [rbp+16], [rbp+24], etc.
            for i, param in enumerate(funcao.parametros):
                mapa_variaveis[param] = 16 + i * 8
            
            # Variáveis locais: [rbp-8], [rbp-16], etc.
            for i, var_name in enumerate(variaveis_locais):
                mapa_variaveis[var_name] = -8 * (i + 1)
            
            # Gerar código para cada statement
            for stmt in funcao.corpo.statements:
                if isinstance(stmt, Declaracao):
                    # Gerar expressão do lado direito
                    gerar_codigo_expr(stmt.expressao, code, mapa_variaveis, funcao.nome)
                    # Armazenar na variável local
                    code[0] += f"\n    mov %rax, {mapa_variaveis[stmt.nomeVariavel]}(%rbp)"
                
                elif isinstance(stmt, Return):
                    gerar_codigo_expr(stmt.expressao, code, mapa_variaveis, funcao.nome)
                    code[0] += f"\n    jmp {funcao.nome}_fim"
                
                else:
                    gerar_codigo_stmt(stmt, code, mapa_variaveis, funcao.nome)
            
            # Epilogue
            code[0] += f"\n{funcao.nome}_fim:"
            code[0] += "\n    mov %rbp, %rsp"
            code[0] += "\n    pop %rbp"
            code[0] += "\n    ret"

        def gerar_codigo_expr(expr, code, mapa_variaveis, nome_funcao):
            """Gera código para uma expressão"""
            if isinstance(expr, Number):
                code[0] += f"\n    mov ${expr.value}, %rax"
            
            elif isinstance(expr, Var):
                if expr.nomeVariavel in mapa_variaveis:
                    offset = mapa_variaveis[expr.nomeVariavel]
                    code[0] += f"\n    mov {offset}(%rbp), %rax"
                else:
                    code[0] += f"\n    mov {expr.nomeVariavel}, %rax"
            
            elif isinstance(expr, BinOp):
                gerar_codigo_expr(expr.left, code, mapa_variaveis, nome_funcao)
                code[0] += "\n    push %rax"
                gerar_codigo_expr(expr.right, code, mapa_variaveis, nome_funcao)
                code[0] += "\n    pop %rbx"

                op = expr.op
                if op == '+':
                    code[0] += "\n    add %rbx, %rax"
                elif op == '-':
                    code[0] += "\n    sub %rbx, %rax"   
                elif op == '*':
                    code[0] += "\n    imul %rbx"
                elif op == '/':
                    code[0] += "\n    mov %rax, %rcx"  
                    code[0] += "\n    mov %rbx, %rax"  
                    code[0] += "\n    xor %rdx, %rdx"
                    code[0] += "\n    idiv %rcx"
            
            # ⚠️ ADICIONAR SUPORTE PARA COMPARACAO
            elif isinstance(expr, Comparacao):
                gerar_codigo_expr(expr.left, code, mapa_variaveis, nome_funcao)
                code[0] += "\n    push %rax"
                gerar_codigo_expr(expr.right, code, mapa_variaveis, nome_funcao)
                code[0] += "\n    pop %rbx"
                
                code[0] += "\n    cmp %rax, %rbx"  # Compara right (RAX) com left (RBX)
                
                op = expr.op
                if op == '==':
                    code[0] += "\n    sete %al"
                elif op == '!=':
                    code[0] += "\n    setne %al"
                elif op == '<':
                    code[0] += "\n    setl %al"    # set if left < right
                elif op == '>':
                    code[0] += "\n    setg %al"    # set if left > right
                elif op == '<=':
                    code[0] += "\n    setle %al"
                elif op == '>=':
                    code[0] += "\n    setge %al"
                else:
                    raise Exception(f"Operador de comparação desconhecido: {op}")
                
                code[0] += "\n    movzx %al, %rax"  # Extender para 64 bits
            
            elif isinstance(expr, ChamadaFuncao):
                # Salvar registradores caller-saved
                code[0] += "\n    push %rbx"
                code[0] += "\n    push %rcx"
                code[0] += "\n    push %rdx"
                code[0] += "\n    push %rsi"
                code[0] += "\n    push %rdi"
                
                # Empilhar argumentos na ordem inversa
                for arg in reversed(expr.argumentos):
                    gerar_codigo_expr(arg, code, mapa_variaveis, nome_funcao)
                    code[0] += "\n    push %rax"
                
                # Chamar função
                code[0] += f"\n    call {expr.nome}"
                
                # Limpar argumentos da pilha
                if expr.argumentos:
                    code[0] += f"\n    add ${len(expr.argumentos) * 8}, %rsp"
                
                # Restaurar registradores
                code[0] += "\n    pop %rdi"
                code[0] += "\n    pop %rsi"
                code[0] += "\n    pop %rdx"
                code[0] += "\n    pop %rcx"
                code[0] += "\n    pop %rbx"
            
            else:
                raise Exception(f"Tipo de expressão não suportado: {type(expr).__name__}")

        def gerar_codigo_stmt(stmt, code, mapa_variaveis, nome_funcao):
            """Gera código para um statement"""
            nonlocal label_counter
            
            if isinstance(stmt, If):
                label_false = f"L{label_counter}"; label_counter += 1
                label_end = f"L{label_counter}"; label_counter += 1
                
                # ⚠️ CORREÇÃO: Usar gerar_codigo_expr para a condição (que pode ser Comparacao)
                gerar_codigo_expr(stmt.condicao, code, mapa_variaveis, nome_funcao)
                code[0] += f"\n    cmp $0, %rax"
                code[0] += f"\n    je {label_false}"
                
                # Bloco if
                for sub_stmt in stmt.bloco_if.statements:
                    if isinstance(sub_stmt, Declaracao):
                        gerar_codigo_expr(sub_stmt.expressao, code, mapa_variaveis, nome_funcao)
                        code[0] += f"\n    mov %rax, {mapa_variaveis[sub_stmt.nomeVariavel]}(%rbp)"
                    else:
                        gerar_codigo_stmt(sub_stmt, code, mapa_variaveis, nome_funcao)
                
                if stmt.bloco_else:
                    code[0] += f"\n    jmp {label_end}"
                
                code[0] += f"\n{label_false}:"
                
                # Bloco else
                if stmt.bloco_else:
                    for sub_stmt in stmt.bloco_else.statements:
                        if isinstance(sub_stmt, Declaracao):
                            gerar_codigo_expr(sub_stmt.expressao, code, mapa_variaveis, nome_funcao)
                            code[0] += f"\n    mov %rax, {mapa_variaveis[sub_stmt.nomeVariavel]}(%rbp)"
                        else:
                            gerar_codigo_stmt(sub_stmt, code, mapa_variaveis, nome_funcao)
                    code[0] += f"\n{label_end}:"
              
            elif isinstance(stmt, While):
                label_start = f"L{label_counter}"; label_counter += 1
                label_end = f"L{label_counter}"; label_counter += 1
                
                code[0] += f"\n{label_start}:"
                gerar_codigo_expr(stmt.condicao, code, mapa_variaveis, nome_funcao)
                code[0] += f"\n    cmp $0, %rax"
                code[0] += f"\n    je {label_end}"
                
                # Corpo do while
                for sub_stmt in stmt.bloco.statements:
                    if isinstance(sub_stmt, Declaracao):
                        gerar_codigo_expr(sub_stmt.expressao, code, mapa_variaveis, nome_funcao)
                        code[0] += f"\n    mov %rax, {mapa_variaveis[sub_stmt.nomeVariavel]}(%rbp)"
                    else:
                        gerar_codigo_stmt(sub_stmt, code, mapa_variaveis, nome_funcao)
                
                code[0] += f"\n    jmp {label_start}"
                code[0] += f"\n{label_end}:"
            
            elif isinstance(stmt, Bloco):
                for sub_stmt in stmt.statements:
                    if isinstance(sub_stmt, Declaracao):
                        gerar_codigo_expr(sub_stmt.expressao, code, mapa_variaveis, nome_funcao)
                        # Nota: variáveis em blocos aninhados precisariam de escopo separado
                        code[0] += f"\n    mov %rax, {mapa_variaveis[sub_stmt.nomeVariavel]}(%rbp)"
                    else:
                        gerar_codigo_stmt(sub_stmt, code, mapa_variaveis, nome_funcao)
            
            elif isinstance(stmt, ChamadaFuncao):
                # Chamada como statement (ignorar retorno)
                gerar_codigo_expr(stmt, code, mapa_variaveis, nome_funcao)

        # Contador global de labels
        label_counter = 0

        try:
            self.obj_parser = Parser()
            self.obj_parser.lexic_analyse(self.code)
            self.tree = self.obj_parser.parse(self.obj_parser.tokenlist)
            
            if self.tree is None:
                print("Erro: a árvore AST é None")
                return
            
            self.obj_parser.semantic_analysis(self.tree)
        except Exception as e:
            raise Exception(f"Erro: {e}")
        
        # Cabeçalho do assembly
        self.asmcode = [".section .text"]
        
        # Gerar código para todas as funções (incluindo main)
        for funcao in self.tree.funcoes:
            gerar_codigo_funcao(funcao, self.asmcode)
        
        # Gerar código para main
        gerar_codigo_funcao(self.tree.funcao_main, self.asmcode)
        
        # Ponto de entrada COM SUPPORTE A IMPRESSÃO
        self.asmcode[0] += "\n\n# Ponto de entrada do programa"
        self.asmcode[0] += "\n.globl _start"
        self.asmcode[0] += "\n_start:"
        self.asmcode[0] += "\n    call main"
        
        # IMPRIMIR o resultado antes de sair
        self.asmcode[0] += "\n    # Imprimir resultado"
        self.asmcode[0] += "\n    mov %rax, %rdi      # salvar resultado"
        self.asmcode[0] += "\n    call imprime_num    # imprimir valor"
        self.asmcode[0] += "\n    mov %rdi, %rax      # restaurar resultado para exit"
        
        self.asmcode[0] += "\n    mov %rax, %rdi    # código de saída"
        self.asmcode[0] += "\n    call sair         # terminar programa"
        
        print("Código assembly gerado:")
        print(self.asmcode[0])
        
        # Chamar função de impressão se necessário
        self.asmcode[0] += "\n\n    call imprime_num"
        self.asmcode[0] += "\n    call sair"
        self.asmcode[0] += "\n.include \"./runtime/runtime.s\""

        

        with open("saida.s", "w") as f:
            f.write(self.asmcode[0])


def main():
    comp = Compiler()
    print(comp.version)
    print("Digite o nome do arquivo de entrada:\n")
    entrada = input()
    try:
        comp.read_file(entrada)
        comp.compile()
        print("Programa compilado com sucesso!")
    except Exception as e:
        print(f"Erro durante a compilação: {e}")


if __name__ == "__main__":
    main()