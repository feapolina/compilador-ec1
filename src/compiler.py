from .ast_nodes import *
from .parser import *

class Compiler:

    def __init__(self):
        self.version = "1.0"
        self.code = None
        self.tree = None

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

    def compile(self):

        def gerar_codigo(node, code):
            # node: instância de Number ou BinOp (definidos em BinTree)
            if node is None:
                return

            # Caso Programa
            if isinstance(node, Programa):
                gerar_codigo(node.declaracoes,code)
                gerar_codigo(node.expressaoFinal,code)
                return
            
            # Caso Declaração
            if isinstance(node, Declaracao):
                # if isinstance(node.expressao, BinOp):
                #     code[0] += f"\n    # {node.nomeVariavel} = {node.expressao.left} {node.expressao.op} {node.expressao.right}"
                gerar_codigo(node.expressao,code)
                return

            # Caso Var
            if isinstance(node,Var):
                code[0] += f"\n    mov %rax, {node.nomeVariavel}\n"
                return
            
            # Caso list
            if isinstance(node,list):
                for child in node:
                    gerar_codigo(child,code)
                return

            # Caso folha (número)
            if isinstance(node, Number):
                code[0] += f"\n    mov ${node.value}, %rax"
                return

            # Caso binário
            if isinstance(node, BinOp):

                gerar_codigo(node.left, code)
                code[0] += "\n    push %rax"
                gerar_codigo(node.right, code)
                code[0] += "\n    pop %rbx"

                op = node.op
                if op == '+':
                    code[0] += "\n    add %rbx, %rax"
                elif op == '-':
                    code[0] += "\n    mov %rax, %rcx"   
                    code[0] += "\n    mov %rbx, %rax"   
                    code[0] += "\n    sub %rcx, %rax"   
                elif op == '*':
                    code[0] += "\n    mul %rbx"
                elif op == '/':
                    code[0] += "\n    mov %rax, %rcx"  
                    code[0] += "\n    mov %rbx, %rax"  
                    code[0] += "\n    div %rcx"      
                else:
                    raise Exception(f"Operador desconhecido: {op}")
                return

            raise TypeError(f"Tipo de nó não suportado no gerador: {type(node).__name__}")

        def gerar_variaveis(node,code):
            if node is None:
                return
            for n in node:
                if isinstance(n,Declaracao):
                    code[0] += f"\n.lcomm {n.nomeVariavel}, 8"
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
        self.asmcode[0] +=".section .bss"
        gerar_variaveis(self.tree.declaracoes,self.asmcode)
        self.asmcode[0] += "\n\n.section .text"
        self.asmcode[0] += "\n.globl _start"
        self.asmcode[0] += "\n_start:"

        # Gera o código da expressão
        gerar_codigo(self.tree, self.asmcode)

        print(self.asmcode[0])

        self.asmcode[0] += "\n\n    call imprime_num"
            
        self.asmcode[0] += "\n    call sair"
        self.asmcode[0] += "\n.include \"../runtime/runtime.s\""

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
    except:
        print("Arquivo de Entrada inválido")


if __name__ == "__main__":
    main()
