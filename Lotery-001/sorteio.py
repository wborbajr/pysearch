#!/usr/bin/env python
#-*-coding:UTF-8-*-

#Numeros sorteados

def geraNumeros(data):
	f = open("./files/result.txt", "r")
	f2 = f.readlines()
	f3 = [z.strip() for z in f2]
	f.close()
	numeros = []
	#conc = []
	for i, str in enumerate(f3):
		if data == str:
			#conc = f3[i-1]
			num = []
			for z in range(0,15):
				n = f3[i +1]
				i=i+1
				num.append(n)
			numeros = num[0:15]
			numeros.sort()
		
	return numeros

def conc(data):
	f = open("./files/result.txt", "r")
	f2 = f.readlines()
	f3 = [z.strip() for z in f2]
	f.close()
	concurso = []
	for i, str in enumerate(f3):
		if data == str:
			concurso = f3[i-1]
	return concurso
