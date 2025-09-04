# Executa o compilador como um módulo a partir da pasta raiz
# O Python irá procurar e executar o arquivo src/__main__.py
python3 -m src

as --64 -o saida.o saida.s
ld -o saida saida.o
./saida