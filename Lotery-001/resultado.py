#!/usr/bin/env python
#-*-unicode: UTF-8-*-

a11 = "3.00"
a12 = "6.00"
a13 = "12.00"
a14 = "1000.00"
a15 = "10e6"

def resultado(numj,nums):
	counter = 0
	result =[]
	for i in numj:
		for z in nums:
			if i == z:
				counter = counter + 1
				result.append(i)
				
	if counter == 11:
		message = "Ganhou R$ %s"%a11
	elif counter == 12:
		message = "Ganhou R$ %s "%a12
	elif counter == 13:
		message = "Ganhou R$ %s "%a13
	elif counter == 14:
		message = "Ganhou R$ %s "%a14
	elif counter >= 15:
		message = "\033[0;34mGanhou R$ %s \033[0m"%a15
	else:
		message = "Tente Novamente!"
	
	print 25*"*"
	print "\t\033[0;31mRESULTADO\033[0m"
	print 25*"*"
	print result
	print "\033[0;31m%i Acertos\033[0m" %counter
	print message