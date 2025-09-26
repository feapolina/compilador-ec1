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

        def gerar_codigo(node, code):
            if node is None:
                return

            # Caso Programa
            if isinstance(node, Programa):
                # Gerar código para todas as declarações
                for decl in node.declaracoes:
                    gerar_codigo(decl, code)
                
                # Gerar código para expressão final se existir
                if node.expressaoFinal:
                    gerar_codigo(node.expressaoFinal, code)
                return
            
            # Caso Declaração
            if isinstance(node, Declaracao):
                # Gerar código para a expressão (resultado em RAX)
                gerar_codigo(node.expressao, code)
                # Armazenar resultado na variável
                code[0] += f"\n    mov %rax, {node.nomeVariavel}"
                return

            # Caso Var
            if isinstance(node, Var):
                code[0] += f"\n    mov {node.nomeVariavel}, %rax"
                return
            
            # Caso Number
            if isinstance(node, Number):
                code[0] += f"\n    mov ${node.value}, %rax"
                return

            # Caso BinOp
            if isinstance(node, BinOp):
                gerar_codigo(node.left, code)
                code[0] += "\n    push %rax"
                gerar_codigo(node.right, code)
                code[0] += "\n    pop %rbx"

                op = node.op
                if op == '+':
                    code[0] += "\n    add %rbx, %rax"
                elif op == '-':
                    code[0] += "\n    sub %rbx, %rax"   
                elif op == '*':
                    code[0] += "\n    imul %rbx"
                elif op == '/':
                    code[0] += "\n    mov %rax, %rcx"  
                    code[0] += "\n    mov %rbx, %rax"  
                    code[0] += "\n    xor %rdx, %rdx"  # Limpar RDX para divisão
                    code[0] += "\n    idiv %rcx"      
                else:
                    raise Exception(f"Operador desconhecido: {op}")
                return

            # Caso Comparacao - VERSÃO CORRIGIDA
            if isinstance(node, Comparacao):
                # CORREÇÃO: Gerar código para o lado ESQUERDO primeiro
                gerar_codigo(node.left, code)
                code[0] += "\n    push %rax"
                # Depois gerar código para o lado DIREITO
                gerar_codigo(node.right, code)
                code[0] += "\n    pop %rbx"
                
                # CORREÇÃO: Agora comparamos left (RBX) com right (RAX)
                code[0] += "\n    cmp %rax, %rbx"  # Compara left (RBX) com right (RAX)
                
                # Configurar RAX com 0 ou 1 baseado na comparação
                op = node.op
                if op == '==':
                    code[0] += "\n    sete %al"
                elif op == '<':
                    code[0] += "\n    setl %al"    # set if left < right
                elif op == '>':
                    code[0] += "\n    setg %al"    # set if left > right
                else:
                    raise Exception(f"Operador de comparação desconhecido: {op}")
                
                # Extender AL para RAX (convertendo byte para quadword)
                code[0] += "\n    movzx %al, %rax"
                return

            # Caso If
            if isinstance(node, If):
                label_false = self.novo_label()
                label_end = self.novo_label()
                
                # Gerar código para a condição
                gerar_codigo(node.condicao, code)
                
                # Verificar se condição é falsa (0)
                code[0] += f"\n    cmp $0, %rax"
                code[0] += f"\n    je {label_false}"
                
                # Bloco if (verdadeiro)
                gerar_codigo(node.bloco_if, code)
                
                # Pular para o final se necessário
                if node.bloco_else:
                    code[0] += f"\n    jmp {label_end}"
                
                # Label para bloco else
                code[0] += f"\n{label_false}:"
                
                # Bloco else (se existir)
                if node.bloco_else:
                    gerar_codigo(node.bloco_else, code)
                    code[0] += f"\n{label_end}:"
                return

            # Caso While
            if isinstance(node, While):
                label_start = self.novo_label()
                label_end = self.novo_label()
                
                code[0] += f"\n{label_start}:"
                
                # Gerar código para a condição
                gerar_codigo(node.condicao, code)
                
                # Verificar se condição é falsa (0)
                code[0] += f"\n    cmp $0, %rax"
                code[0] += f"\n    je {label_end}"
                
                # Bloco do while
                gerar_codigo(node.bloco, code)
                
                # Voltar para o início
                code[0] += f"\n    jmp {label_start}"
                code[0] += f"\n{label_end}:"
                return

            # Caso Bloco
            if isinstance(node, Bloco):
                for statement in node.statements:
                    gerar_codigo(statement, code)
                return

            # Caso Return
            if isinstance(node, Return):
                gerar_codigo(node.expressao, code)
                # Em assembly, o valor de retorno fica em RAX
                # Para um programa simples, podemos apenas deixar o valor em RAX
                return

            raise TypeError(f"Tipo de nó não suportado no gerador: {type(node).__name__}")

        def gerar_variaveis(node, code):
            """Gera declarações de variáveis na seção .bss"""
            variaveis = set()
            
            def coletar_variaveis(n):
                if isinstance(n, Declaracao):
                    variaveis.add(n.nomeVariavel)
                elif isinstance(n, Programa):
                    for decl in n.declaracoes:
                        coletar_variaveis(decl)
                elif isinstance(n, If):
                    coletar_variaveis(n.bloco_if)
                    if n.bloco_else:
                        coletar_variaveis(n.bloco_else)
                elif isinstance(n, While):
                    coletar_variaveis(n.bloco)
                elif isinstance(n, Bloco):
                    for stmt in n.statements:
                        coletar_variaveis(stmt)
            
            coletar_variaveis(node)
            
            for var in variaveis:
                code[0] += f"\n.lcomm {var}, 8"

        try:
            self.obj_parser = Parser()
            self.obj_parser.lexic_analyse(self.code)
            self.tree = self.obj_parser.parse(self.obj_parser.tokenlist)
            
            if self.tree is None:
                print("Erro: a árvore AST é None — verifique se o parser construiu a árvore corretamente.")
                return
            
            self.obj_parser.semantic_analysis(self.tree)
        except Exception as e:
            raise Exception(f"Erro: {e}")
            
        # Cabeçalho do assembly
        self.asmcode = [""]
        self.asmcode[0] += ".section .bss"
        gerar_variaveis(self.tree, self.asmcode)
        self.asmcode[0] += "\n\n.section .text"
        self.asmcode[0] += "\n.globl _start"
        self.asmcode[0] += "\n_start:"

        # Gera o código do programa
        gerar_codigo(self.tree, self.asmcode)

        # Se não há expressão final, usar 0 como código de saída
        if self.tree.expressaoFinal is None:
            # Correção de BUG do print
            #self.asmcode[0] += "\n    mov $0, %rax"
            pass

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