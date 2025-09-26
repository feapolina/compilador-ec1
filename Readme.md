
Grupo:
FELIPE CAVALCANTI APOLINARIO
GIANCARLO SILVEIRA CAVALCANTE
HERLAN ALEF DE LIMA NASCIMENTO
PEDRO HENRIQUE DE ARAUJO LIMA

Atualização da linguagem suportada pelo compilador de EV para CMD.

Com isso tivemos mudanças na estrutura lexica e semantica da linguagem fazendo versões antigas não funcionarem nessa nova versão do compilador.

Sintaxe utilizada foi a mesma do exemplo do professor. Ex: 
 x = (7 + 4) * 12;
 y = x * 3 + 11;
 = (x * y) + (x * 11) + (y * 13)

Diferenças da versão CMD do grupo:
"<Staments>" do tipo if e while precisam ter sua declaração em ()
Ex:
if (x > 10) {
    <codigo>
}

Modo de uso:
Execute o arquivo exec.sh para compilar e entre com o nome do arquivo de entrada

Foi incluido arquivos test[].cmd para testes
Obs: Os arquivos "bin" são sempre gerados com o mesmo nome por isso ao compilar versões antigas são substituidas!