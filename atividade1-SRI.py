# -*- coding: UTF-8 -*-
# encoding: iso-8859-1
# encoding: win-1252

import string
import re

#metodo que le o arquivo wikipedia
def leWiki():
    arq = open('ptwiki-v2.trec', 'r')
    texto = arq.read()
    arq.close()
    return texto.lower()
    
#metodo para retirar os caracteres indesejados do arquivo
def cleanText(arquivo):    
    arquivo = re.sub(r"&.{2,4};"," ", arquivo)
    arquivo = re.sub(r"\\{\\{!\\}\\}", " ", arquivo)
    arquivo = arquivo.replace("[[", " ")
    arquivo = arquivo.replace("]]", " ")
    arquivo = re.sub("{{.*?}}", "", arquivo)
    arquivo = re.sub("<.*?>", "", arquivo)
    arquivo = re.sub("[^a-z0-9çáéíóúàãõâêô-]", " ", arquivo)
    arquivo = re.sub(r"\n","", arquivo)	
    return arquivo.split(" ")
    
"""neste metodo eu irei criar primeiramente um dicionario onde as chaves sao os numeros dos documentos e os valores sao as palavras que
compoem esse documento """
def criaDict(texto):
	palavras = texto
	dicionario = {}
	while palavras != '':
		if palavras.find('<docno>') != -1: #percorrer o documento enquanto houver a tag <docno>
			
			posI = palavras.find('<docno>') + 7
			posF = palavras.find('</docno>') 
			
			chave = palavras[posI:posF] #pegando o numero de cada documento, o que esta entre a tag <docno>
			
			posI2 = palavras.find('<headline>') + 10
			posF2 = palavras.find('</headline')
			
			titulo = palavras [posI2:posF2] #pegando o titulo de cada documento, o que esta entre a tag <headline>
			
			dicionario[chave] = [titulo]
			
			posI3 = palavras.find('<p>') + 3
			posF3 = palavras.find('</p>')
			
			conteudo = palavras [posI3:posF3] #pegando o texto de cada documento, o que esta entre a tag <p>
			
			conteudo = cleanText(conteudo) #tirando os caracteres indesejados
			
			for palavra in conteudo:  #o conteudo fica como uma lista de palavras, por isso percorrer essa lista e adicionar ao dicionario
				if palavra != "":	  #tirando os vazios que existem na lista
					dicionario[chave].append(palavra)
				
			
			palavras = palavras[posF3 + 4:] #o conteudo a ser percorrido agora é o que vem depois da tag </p>
			
		else:
			palavras = ''
	
	return dicionario
		
"""Com um dicionario criado a partir dos documentos existentes, irei criar o indice invertido e escreve-lo num arquivo .txt"""
def criaIndiceInvertido(texto):
	dic = criaDict(texto)
	indice_invertido = {}
	arq = open("indice_invertido.txt", "w")
	
	
	"""Percorro as chaves e valores do dicionario e vejo se o novo dicionario (indice_invertido) já possui uma determinada chave,
	o seja, verifico se aquela palavra ja eh uma chave do indice invertido. Se ja for, adiciono aquele documento aos seus valores,
	se nao crio uma nova chave no indice_invertido"""
	for k,v in dic.iteritems(): 
		for palavra in v:
			if indice_invertido.has_key(palavra):
				if k not in indice_invertido[palavra]: #verifico se o documento ja esta nos valores de determinada chave e so insiro ele nos valores se não estiver
					indice_invertido[palavra].append(int(k))
			else:
				indice_invertido[palavra] = [int(k)]
	
	#loop para escrever o documento .txt	
	for key,valor in indice_invertido.iteritems():
		arq.write(key +": [")
		valor = sorted(list(set(valor))) 
		for i in range(len(valor)):
			if i != len(valor) -1:
				arq.write(str(valor[i]) + ', ')
			else:
				arq.write(str(valor[i]))	#se for o ultimo item, nao adiciono a virgula
		arq.write("]\n")
		
	arq.close()
			
	return indice_invertido
	
def algoritmoAND(dic, palavra1, palavra2): #recebe o dicionario que representa os indices invertidos e as palavras desejadas
	palavra1 = palavra1.lower() #deixando as palavras em minusculo para que possam ser reconhecidas como chaves do dicionario
	palavra2 = palavra2.lower()
	
	if dic.has_key(palavra1) != True or dic.has_key(palavra2) != True: #verifica se as duas palavras existem nos documentos
		return "Nenhum documento contem essas duas palavras"
		
	docs_palavra1 = sorted(dic[palavra1]) #recupera a lista ordenada de documentos que contem a palavra 1
	docs_palavra2 = sorted(dic[palavra2]) #recupera a lista ordenada de documentos que contem a palavra 2
	
	ind1 = 0
	ind2 = 0

	docs_em_comum = []

#Algoritmo do Merge
	while ind1 != len(docs_palavra1) and ind2 != len(docs_palavra2): #enquanto os contadores não estao no final das listas
		
		if docs_palavra1[ind1] == docs_palavra2[ind2]:  #verifico se o documento atual da palavra 1 eh igual ao da palavra 2
			docs_em_comum.append(int(docs_palavra1[ind1])) #se sim, adiciono esse documento na lista dos docs em comum dessas palavras
			ind1 += 1
			ind2 += 1
		elif docs_palavra1[ind1] < docs_palavra2[ind2]: #se nao, verifico qual indice eh menor para que eu possa incrementa-lo
			ind1 += 1
		else:
			ind2 += 1
	
	if len(docs_em_comum) == 0:  #caso a lista de documentos em comum esteja vazia, significa que nao existe documento em que as duas estejam
		return "Essas palavras nao existem em um mesmo documento"
	
	docs_em_comum = list(set(docs_em_comum))
	return sorted(docs_em_comum)
	
def algoritmoOR(dic, palavra1, palavra2):
	palavra1 = palavra1.lower()   #deixando as palavras em minusculo para que possam ser reconhecidas como chaves do dicionario
	palavra2 = palavra2.lower()
	
	docs_palavra12 = []
	
	if dic.has_key(palavra1) != True and dic.has_key(palavra2) != True: #verifica se as duas palavras existem nos documentos
		return "Nenhum documento contem alguma dessas palavras"
	
	if dic.has_key(palavra1):
		docs_palavra12 += sorted(dic[palavra1]) #adiciona aa lista vazia a lista ordenada de documentos que contem a palavra 1
	elif dic.has_key(palavra2):
		docs_palavra12 += sorted(dic[palavra2]) #adiciona aa lista vazia a lista ordenada de documentos que contem a palavra 2
	
	docs_palavra12 = list(set(docs_palavra12))
	
	for doc in range(len(docs_palavra12)):
		docs_palavra12[doc] = int(docs_palavra12[doc])
	
	return sorted(docs_palavra12)	


 
#Exemplo de Execucao
dic = criaIndiceInvertido(leWiki())

print "nomes OR bíblicos"  
print algoritmoOR(dic, 'nomes', 'bíblicos')
print "\n"
print "nomes AND bíblicos"
print algoritmoAND(dic, 'nomes', 'bíblicos')
print "\n"
print "Estados OR Unidos"
print algoritmoOR(dic, 'Estados', 'Unidos')
print "\n"
print "Estados AND Unidos"
print algoritmoAND(dic, 'Estados', 'Unidos')
print "\n"
print "Winston OR Churchill"
print algoritmoOR(dic, 'Winston', 'Churchill')
print "\n"
print "Winston AND Churchill"
print algoritmoAND(dic, 'Winston', 'Churchill')


