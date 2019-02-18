#!/usr/bin/env python
#-*-coding: UTF-8-*-
import sorteio_edit
import sorteio 
from sorteio import *
import jogo 
from downresult import *
from resultado import *
from implista import imprimeLista 

"""
choice = raw_input('Digitar novos numeros? \n1 - Nao, 2 - Sim')

if choice == 2:
	n = []
	for i in range(0,14):
		num = raw_input("Digite o numero")
		n.append(num)
	f=open('./files/jogo', 'w')
	f2.write(f)
"""

#data = "25/05/2015"
data = raw_input("Digite a data do sorteio: ")
choice2 = int(raw_input("Os numeros foram digitados? \n1-sim, 2-nao\n"))
if choice2 == 1:
	erro = 2
	erroData = 2
else:
	erro = ping()
	down(erro)
	erroData = verifData(data)

if erroData == 0:
	dia = data
	geraNumeros(dia)
	concurso = conc(dia)
	a = jogo.numeros
	b = geraNumeros(dia)
	result = []
	numJogados = a
	numSorteados= b
	erroData = 0
elif erroData == 2:
	dia = data
	concurso = sorteio_edit.conc
	a = jogo.numeros
	b = sorteio_edit.numeros
	result = []
	numJogados = a
	numSorteados= b
	erroData = 0
	
else:
	erroData = 1

print ""
print ""
if erroData == 0:
	print "\033[0;31mRESULTADO LOTOFACIL \033[0m"
	print "\033[0;34mData: \033[0m" +dia
	print "\033[0;34mConcurso N°:\033[0m " +concurso
	print b
	print "\n"
	print 30*"*"
	print "\t\033[0;31mNUMEROS JOGADOS\033[0m"
	print 30*"*"
	imprimeLista(numJogados)
	print "\n"
	print 30*"*"
	print "\t\033[0;31mNUMEROS SORTEADOS\033[0m"
	print 30*"*"
	imprimeLista(numSorteados)
	print "\n"
	resultado(numJogados,numSorteados)
else:
	print """\033[0;31mData: %s não encontrada no arquivo result.txt!\033[0m\n
	\033[0;31mTente o Download novamente!!!\033[0m""" % data
