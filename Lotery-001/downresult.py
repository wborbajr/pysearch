#!/usr/bin/env python
#-*-coding:utf:8 -*-
# Substituir as tags html

import re 
import os 
import urllib

""" 
Testar a conexão com o site,
Baixar o arquivo zipado com os resultados, criar o diretorio files,
criar o arquivo de leitura dos resultados
"""

url = "http://www1.caixa.gov.br/loterias/_arquivos/loterias/D_lotfac.zip"
zipy = "D_lotfac.zip"
zipfile = "D_lotfac.zip"
down = url

print 40*"="
print " \033[0;34mBaixando arquivo com os resultados\033[0m"
print 40*"="

def ping():
	try:
		#site = urllib2.urlopen(url)
		#urllib.urlretrieve(url,zipfile)
		os.system("wget http://www1.caixa.gov.br/loterias/_arquivos/loterias/D_lotfac.zip")
		erro = 0
	
	except:
		#print "\033[0;31mNão foi possível baixar o arquivo\033[0m"
		erro = 1

	return erro

def down(erro):
	if erro == 1:
		print "\033[0;31mNão foi possível baixar o arquivo\033[0m"
	else:
		#print "\033[0;31mNão foi possível baixar o arquivo\033[0m"
		
		print " \033[0;32mDownload Concluido!\033[0m"
		os.system("rm -r files")
		os.system("mkdir files") 
		print "\033[0;36m Movendo arquivo para a pasta files\033[0m "
		os.system("mv D_lotfac.zip files/")
		print " Extraindo os arquivos ..."
		os.system("cd files/ && unzip D_lotfac.zip && rm D_lotfac.zip")
		print "\033[0;35m Pronto!\033[0m"
		file = "./files/D_LOTFAC.HTM"
		f = open(file, "r")
		f2 = f.read()
		f.close()
		txt = open("./files/result.txt", "wa")
		htm = re.sub("<.*?>","",f2)
		txt.write(htm)
		txt.close()
		#os.system("tail -48 ./files/result.txt > ./files/resultado"

def verifData(data):
	f = open("./files/result.txt", "r")
	f2 = f.readlines()
	f3 = [z.strip() for z in f2]
	f.close()
	if data in f3:
		erroData = 0
	else:
		erroData = 1
	return erroData
	
	
	
