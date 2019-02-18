#!/usr/bin/env python
import re

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
		 
		
		
		
		
