fun imcremento_dez(var a){
var c = 0;
while (c <= 9){
	c += 1;
	a += 1;
}
return a;
}

fun main(){
var b = 100;
b = imcremento_dez(b);
return b;
}