
#-*-coding:UTF-8-*-

#Numeros sorteados
import sys
import os

numeros = []
f = open("./files/result.txt", "r")
f2 = f.readlines()
f3 = [z.strip() for z in f2]
#data = "18/05/2015"
data = raw_input("Digite a data do sorteio no formato (dd/mm/AAAA): \n")
for i, str in enumerate(f3):
	if str == data:
		print "\033[0;32mData:\033[0m"+str
		sorteio = f3[i-1]
		print "\033[0;33mSorteio: \033[0m"+sorteio
		numbers = []
		for z in range(0,15):
			n = f3[i +1]
			i=i+1
			numbers.append(n)
		num = numbers[0:15]
		num.sort()
		print num
def geraNumeros():
	#downsorteio = os.system("sh downresult.sh")
	f = open("./files/resultado", 'r')
	f2=list(f)
	f.close()
	f3 = [z.strip() for z in f2]
	result=f3[2:17]
	result.sort()
	for i in result:
		numeros.append(i)
	concurso = f3[0]
	data = f3[1]

	print ""
	print ""
	print "\033[0;31mRESULTADO LOTOFACIL \033[0m"
	print "\033[0;34mConcurso N°:\033[0m " +concurso
	print "\033[0;34mData: \033[0m" +data
	print "\033[0;34mNumeros: \033[0m"
	print numeros
	