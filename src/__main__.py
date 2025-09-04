# Importa a classe Compiler do módulo compiler.py
from .compiler import Compiler

def main():
    comp = Compiler()
    print(f"Compiler version {comp.version}")
    
    try:
        # O caminho do arquivo de entrada será relativo à raiz do projeto
        entrada = input("Digite o nome do arquivo de entrada (ex: tests/inputs/teste1.ec2):\n")
        comp.read_file(entrada)
        comp.compile()

        print("\nPrograma compilado com Sucesso!")
        print("Arquivo de saída gerado: saida.s")
    except FileNotFoundError:
        print(f"Erro: Arquivo de Entrada '{entrada}' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()