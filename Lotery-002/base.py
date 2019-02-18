#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Copyright 2011 Thomas Jefferson Pereira Lopes <thomas@thlopes.com>
#       Parte integrante do projeto PyLottery (https://bitbucket.org/THLopes/pylottery)
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.

import os
import socket
import urllib2
import cookielib
import shelve
from datetime import date
import re
import random
import math

PROJECT_PATH = os.path.dirname(__file__)

# timeout em segundos
socket.setdefaulttimeout(20)

# user agent para funcionar como um browser comum
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu/13.04 Chromium/30.0.1599.114 Chrome/31.0.1650.57 Safari/537.36"

# cookiejar para tratar corretamente os cookies enviados pelo servidor
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
# Dica do WagnerLuis1982, presente no gval (https://github.com/wagnerluis1982/gval/blob/master/src/gval/util.py)
opener.addheaders.append(("Cookie", "security=true"))
urllib2.install_opener(opener)

# algumas funções que vão ajudar ao longo do código:

def string_to_list(string_list, transform=None):
    """Recebe uma string with separadores (virgula, espaço, ponto-e-virgula, ponto) e retorna uma List. """

    def base_transform(item):
        if type(item) in (str, unicode):
            item = item.strip()
        if transform and hasattr(transform, '__call__'):
            return transform(item)
        return item

    if type(string_list) not in (str,list,tuple,unicode):
        return None
    if type(string_list) in (str, unicode):
        # TODO: podemos fazer esses replaces de uma forma bem melhor...
        string_list = string_list.strip().replace(' ',',').replace(';',',').replace('.',',').replace('|',',').replace('-',',').replace('/',',').replace(',,',',')
        string_list = string_list.split(',')

    return [base_transform(item) for item in string_list ] #if len(item) > 0

def ensure_date(date_string):
    if type(date_string) == date:
        return date
    dia,mes,ano = string_to_list(date_string, transform=int)
    return date(day=dia,month=mes,year=ano)

def ordinal_from_date(date_string):
    date = ensure_date(date_string)
    return date.toordinal()

def checa_jogo(sorteio, jogo):
    """ Retorna o número de acertos dentro do dado jogo comparando com o sorteio """
    acertos = 0
    sorteio = string_to_list(sorteio, int)
    jogo = string_to_list(jogo, int)
    for numero in sorteio:
        if (numero in jogo):
            acertos += 1
    return acertos

def _wrap_with(code):
    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;%s" % c
        return "\033[%sm%s\033[0m" % (c, text)
    return inner

red = _wrap_with('31')
green = _wrap_with('32')
yellow = _wrap_with('33')
blue = _wrap_with('34')
magenta = _wrap_with('35')
cyan = _wrap_with('36')
white = _wrap_with('37')
bold = _wrap_with('1')

# Classes base da aplicação

class LoteriaBase(object):
    """ Tipo básico de Loteria, inspirado na Lotofácil """
    def __init__(self,
                 name="lotofacil",
                 total_dezenas=25, min_acertos=11, max_acertos=15,
                 arquivo="lotofacil.txt",
                 url_base="http://www1.caixa.gov.br/loterias/loterias/lotofacil/lotofacil_pesquisa_new.asp",
                 intervalo_medio=2,
                 mensagens=False,
                 colors=True,    # TODO: verificar como checar o atributo colors sem ter que embutir o código na classe
                 cache=True):
        self.name = name
        self.total_dezenas = total_dezenas
        self.min_acertos = min_acertos
        self.max_acertos = max_acertos
        self.arquivo = os.path.join(PROJECT_PATH, arquivo)
        self.enable_cache = cache
        self.external_cache = False

        # TODO: lidar com esse bloco de forma que não interrompa a pyLottery de
        # rodar quando não houver conexão com a Internet
        # montando urls, anotando hosts e ip
        self._hostname = urllib2.urlparse.urlparse(url_base).netloc
        try:
            self._hostip = urllib2.socket.gethostbyname(self._hostname)
            self.url_base = url_base.replace(self._hostname, self._hostip)
        except:
            self.url_base = url_base

        self.url_ultimo = "%s?app=1296579402701" % self.url_base
        self.url_numerado = "%s?submeteu=sim&opcao=concurso&txtConcurso=" % (self.url_base)

        self.intervalo_medio = intervalo_medio
        self.mensagens = mensagens
        self.jogos_coletados = None
        self._cache_object = None


    def _log(self, message):
        if self.mensagens:
            print message

    def _open_cache(self):
        """ Singleton que vai retornar o objeto Shelve de cache (completo) para os demais métodos e atributos do cache """
        if not self.enable_cache:
            return None
        if not self._cache_object:
            # TODO: implementar aqui uma checagem para ver se já há um arquivo do cache aberto ou não.
            # Idéias de como fazer: criar um arquivo indicador (.mutex, por exemplo)
            # Tendo esse arquivo criado, não abrir um novo cache
            # Caso o programa seja interrompido e o mutex não seja apagado, alertar o usuário para que ele verifique manualmente
            cache_file_name = os.path.join(PROJECT_PATH, ".pylottery_cache")
            self._cache_object = shelve.open(cache_file_name, writeback=True)
        return self._cache_object

    def carregar_cache_externo(self, cache):
        """ Carrega os dados informados no cache da classe """
        # processar cache externo somente se estiver no formato correto
        if not type(cache) == dict:
            return False
        if not (cache.has_key(self.name)):
            return False
        if not (cache[self.name].has_key('resultados') and cache[self.name].has_key('concursos')):
            return False
        # habilita o cache para que as demais chamadas funcionem.
        self.enable_cache = True
        self.external_cache = True
        # TODO: Checar se o cache esta aberto e fechar antes
        self._cache_object = cache
        return True

    @property
    def cache(self):
        resultados_cache = self._open_cache()
        if not resultados_cache:
            return None
        if not resultados_cache.has_key(self.name):
            self.preparar_cache()
        return resultados_cache[self.name]

    # TODO: criar um metodo para preencher totalmente o cache sozinho, baseado no numero do ultimo concurso encontrado buscando diretamente no site

    @property
    def jogos(self):
        if self.jogos_coletados and len(self.jogos_coletados) > 0:
            return self.jogos_coletados

        # exemplo da estrutura de dados retornada
        [
         # concurso_inicial, concurso_final, [dezenas do jogo], linha_do_arquivo
         ("Nome 1", 880, 889, [1,2,3,4,5], 45),     # Jogo com concurso inicial e final definidos
         ("Nome 2", 890, 899, [1,2,3,4,5], 15),     # Jogo com concurso inicial e final definidos
         ("Nome 3", 890, None, [1,2,3,4,5], 15),    # Jogo para apenas um concurso
         ("Nome 3", 890, 890, [1,2,3,4,5], 15),    # Jogo para apenas um concurso
         ("Nome 4", None, None, [1,2,3,4,5], 15),   # Jogo para todo e qualquer concurso
         ]

        linhas = self.abrir_arquivo().readlines()
        numero_da_linha = 0
        linhas_coletadas = []
        rotulo_atual = ""

        for linha in linhas:
            numero_da_linha += 1
            if len(linha) < 2:
                pass
            elif "[" in linha or "]" in linha:
                # linha de rotulo de jogos
                rotulo_bloco = linha.strip().replace('[','').replace(']','').split(',')
                try:
                    jogo_inicial = int(rotulo_bloco[1])
                except IndexError:
                    jogo_inicial = 0
                try:
                    jogo_final = int(rotulo_bloco[2])
                except IndexError:
                    if jogo_inicial in (0, None, '', 'None'):
                        jogo_final = None
                    else:
                        jogo_final = jogo_inicial

                rotulo_atual = rotulo_bloco[0]
            else:
                jogo = string_to_list(linha, transform=int)
                linhas_coletadas.append((rotulo_atual, jogo_inicial, jogo_final, jogo, numero_da_linha))

        self.jogos_coletados = linhas_coletadas
        return linhas_coletadas

    def checa_cache(self, concurso=None, data=None):
        loteria = str(self.name)
        resultados_cache = self._open_cache()

        if not resultados_cache:
            return False

        if resultados_cache.has_key(loteria):
            resultados_concursos = resultados_cache[loteria]['resultados']
            if concurso:
                concurso = str(concurso)
                if resultados_concursos.has_key(concurso):
                    return  resultados_concursos[concurso]
            if data:
                datas_concursos = resultados_cache[loteria]['concursos']
                if datas_concursos.has_key(data):
                    concurso = datas_concursos[data]
                    return  resultados_concursos[concurso], concurso
                else:
                    return None,None

        return False

    def preparar_cache(self):
        resultados_cache = self._open_cache()
        if not resultados_cache:
            return None

        if not resultados_cache.has_key(self.name) or resultados_cache[self.name] == {}:
            resultados_cache[self.name] = {"resultados": {}, "concursos": {}}

    def atualiza_cache(self, concurso, resultado, data=None):
        if not resultado or resultado in ('',' '):
            return False

        loteria = str(self.name)
        resultados_cache = self._open_cache()

        if not resultados_cache:
            return False

        self.preparar_cache()

        if resultados_cache.has_key(loteria):
            resultados_loteria = resultados_cache[loteria]
            resultados_concursos = resultados_loteria['resultados']
            datas_concursos = resultados_loteria['concursos']
            if concurso:
                concurso = str(concurso)
                resultados_concursos[concurso] = resultado
            if data:
                datas_concursos[data] = concurso

            resultados_loteria['resultados'] = resultados_concursos
            resultados_loteria['concursos'] = datas_concursos
            resultados_cache[loteria] = resultados_loteria

        # TODO: this function always return True, but it's not supposed to be this way
        return True

    def ultimo_concurso_cache(self):
        loteria = str(self.name)
        resultados_cache = self._open_cache()

        if not resultados_cache:
            return False

        if resultados_cache.has_key(loteria):
            resultados_concursos = resultados_cache[loteria]['resultados']
            resultados_concursos = resultados_concursos.items()
            resultados_concursos = sorted(resultados_concursos, key=lambda concurso: int(concurso[0]))
            concurso, resultado = resultados_concursos[-1]
            # pegando a data do concurso
            datas_concursos = [list(item) for item in resultados_cache[loteria]['concursos'].items()]
            [item.reverse() for item in datas_concursos]
            data = dict(datas_concursos)[concurso]
            return concurso, resultado, data
        return False

    def limpar_cache(self):
        resultados_cache = self._open_cache()

        if not resultados_cache:
            return False

        resultados_cache[self.loteria] = {"resultados": {}, "concursos": {}}
        resultados_cache.close()

    def checa_jogo(self, sorteio, jogo):
        """ Atalho para a função global """
        return checa_jogo(sorteio, jogo)

    def abrir_arquivo(self, arquivo=None):
        if not arquivo:
            arquivo = self.arquivo
        return open(arquivo, 'r')

    def capturar_html(self, concurso):
        """ Método para captura o HTML das URL's definidas, não precisa ser sobreescrito. """
        url_alvo = self.url_ultimo
        if concurso:
            url_alvo = "%s%s" % (self.url_numerado, concurso)
        self._log("Buscando resultados do sorteio no site da %s..." % blue("CAIXA",bold=True))
        req = urllib2.Request(url_alvo, headers={'User-Agent': user_agent, 'Host': self._hostname})

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, ex:
            print "%s. Tentando novamente..." % ex
            response = urllib2.urlopen(req)

        html = response.read()
        return html

    def capturar_numero_concurso(self, html=None):
        """ Método para capturar o número do concurso que está sendo capturado, não precisa ser sobreescrito. """
        concurso = None
        if html:
            concurso = html.split('|')[0]
        return concurso

    def is_last(self, html=None):
        pepper = 'Ver pr'
        if html:
            return html.find(pepper) > -1
        return None

    def extrair_sorteio(self, html):
        sorteios = re.findall(r"(?:\d{2}\|*?){15}", html)

        if sorteios:
            # vamos pegar os números em ordem de sorteio
            numeros_sorteados = map(int, sorteios[1].split('|'))
            if (len(numeros_sorteados) == 15):
                self._log(bold("Números sorteados: ") + "%s" % numeros_sorteados)
                return numeros_sorteados

        self._log(red("ERRO:",bold=True) + red(" Sorteio não localizado!!!"))
        return  None

    def extrair_data(self, html, index=1):
        data_concurso = None
        data_match = re.findall('\d{2}/\d{2}/\d{4}', html)
        if len(data_match) > 1:
            data_concurso = data_match[index]
        elif len(data_match) == 1:
            data_concurso = data_match[0]
        self._log(bold("Data: ") + data_concurso)
        return data_concurso

    def buscar_resultado(self, concurso=None, data=None, force=False):
        """ Rotina para capturar o resultado de um dado concurso, primeiro analisando o cache e datas dos concursos """

        # checar o cache primeiro
        if concurso and not force:
            resultado = self.checa_cache(concurso)
            if resultado:
                return resultado, concurso

        if data and not force:
            resultado, concurso = self.checa_cache(data=data)
            if resultado:
                return resultado, concurso

        # Se DATA DE HOJE menos DATA DO ULTIMO CONCURSO for menor qyue intervalo médio da loteria,
            # retorna do último no cache a não ser que force esteja presente
        ultimo_concurso_cache = self.ultimo_concurso_cache()
        if ultimo_concurso_cache:
            if not concurso and ( date.today().toordinal() - ordinal_from_date(ultimo_concurso_cache[2]) ) < self.intervalo_medio and not force:
                return ultimo_concurso_cache[1], ultimo_concurso_cache[0]

        html = self.capturar_html(concurso)
        concurso = self.capturar_numero_concurso(html) or concurso

        self._log("%s: %s" % (bold("Concurso"), concurso))

        # checar se o resultado capturado é válido
        if '|N' in html and 'o existe resul' in html:
            self._log(red("ERRO:", bold=True) + red(" Sorteio não realizado/localizado!!!"))
            return None, concurso #ultimo_concurso

        numeros_sorteados = self.extrair_sorteio(html)
        data_concurso = self.extrair_data(html)

        self.atualiza_cache(concurso, numeros_sorteados, data_concurso)

        return numeros_sorteados, concurso, data_concurso

    def resultados_faltantes(self):
        """ Retorna uma lista de números de concursos que não foram encontrados no cache """
        # pegar número do último concurso
        ultimo_concurso = self.ultimo_concurso_cache()
        # Gerar um range com esse número (de 1 a concurso+1)
        range_concursos = range(1, int(ultimo_concurso[0]) + 1)
        # verificar qual Resultado dentro dessa lista não se encontra no cache
        range_resultados = sorted([int(resultado) for resultado in self.cache['resultados'].keys()])
        concursos_faltantes = list(set(range_concursos) - set(range_resultados))
        return sorted(concursos_faltantes)

    # TODO: melhorar para que confira também intervalo de concursos
    def conferir(self, concurso=None, data=None, arquivo=None, resultado=None, jogo=None):
        """ Checa o arquivo de apostas/resultado manual contra o concurso informado. Se não for informado o concurso/data, buscará o último resultado  """

        concurso_atual = concurso

        # TODO: rever esse if para considerar resultado mesmo sem concurso
        if resultado:
            jogo_sorteado = string_to_list(resultado, transform=int)
            if concurso:
                if not self.checa_cache(concurso):
                    self.atualiza_cache(concurso, jogo_sorteado, data)

        # TODO: colocar aqui um if para conferir o jogo passado manualmente (E isso ficará legal com o intervalo de jogos também

        else:
            resultados_buscados = self.buscar_resultado(concurso, data)
            jogo_sorteado = resultados_buscados[0]
            concurso_atual = int(resultados_buscados[1])

        if not jogo_sorteado:
            self._log(red("Jogo não existente:",bold=True) + red(" Ainda não foi realizado sorteio OU ocorreu um erro na busca (tente novamente)"))
            return None

        if jogo:
            # # concurso_inicial, concurso_final, [dezenas do jogo], linha_do_arquivo
            # ("Nome 1", 880, 889, [1,2,3,4,5], 45),     # Jogo com concurso inicial e final definidos
            jogos = [("Jogo não arquivado", concurso_atual, concurso_atual, string_to_list(jogo, transform=int),0)]
        else:
            jogos = self.jogos

        self._log("Conferindo Jogos, concurso %s" % (concurso_atual))
        total_premiados = 0
        linhas_premiadas = []

        self._log("================================")
        for jogo in jogos:
            if (int(concurso_atual) >= int(jogo[1]) and int(concurso_atual) <= jogo[2]) or (int(concurso_atual) == int(jogo[1])) or jogo[1] in [0, None,'']:
                resultado = self.checa_jogo(jogo_sorteado, jogo[3])
                extra_info = ""
                if (resultado >= self.min_acertos):
                    extra_info = green("*** PREMIADO *** ", bold=True)
                    total_premiados += 1
                    numero_da_linha = jogo[4]
                    linhas_premiadas.append(numero_da_linha)
                self._log("%s%s (%s a %s, Linha %s): %s acertos" % (extra_info, jogo[0], jogo[1] or 1, jogo[2] or concurso_atual, jogo[4], resultado))

        self._log("================================")
        self._log("Total de Premios: %s \nLinhas premiadas: %s" % (total_premiados, linhas_premiadas))

        return total_premiados, linhas_premiadas

    def sortear(self, jogos=1, maximo=None, quantidade=None, amostra=None, print_format=False, gerador=False):
        if gerador:
            return self.sortear_gerador(maximo, quantidade, amostra)

        if not maximo:
            maximo = self.total_dezenas
        if not amostra:
            amostra = xrange(1,maximo+1)
        if not quantidade:
            quantidade = self.max_acertos
        elif quantidade > len(amostra):
            quantidade = len(amostra)

        def gerar(amostra, quantidade):
            sorteados = random.sample(amostra, quantidade)
            sorteados.sort()
            return sorteados

        jogos_gerados = []
        counter = 0
        while counter < jogos:
            jogos_gerados.append(gerar(amostra,quantidade))
            counter += 1

        if print_format:
            return [",".join(map(str, jogo)) for jogo in jogos_gerados]
        return jogos_gerados

    def sortear_gerador(self, jogos=1, maximo=None, quantidade=None, amostra=None):
        if not maximo:
            maximo = self.total_dezenas
        if not amostra:
            amostra = xrange(1,maximo+1)
        if not quantidade:
            quantidade = self.max_acertos
        elif quantidade > len(amostra):
            quantidade = len(amostra)
        round = 0
        while round < jogos:
            sorteados = random.sample(amostra, quantidade)
            sorteados.sort()
            round += 1
            yield sorteados

    def estatisticas_numeros(self, ultimos_concursos=None, concurso=None, ordenar="+"):
        self._log("Indica quantas vezes cada número já foi sorteado no total")
        dicionario = {}
        for numero in range(1, self.total_dezenas+1):
            dicionario[str(numero)] = 0

        resultados = self.cache['resultados'].values()

        # preparando a amostra de forma ordenada
        resultados_ordenados = sorted(self.cache['resultados'].items(),  key=lambda resultado:int(resultado[0]))
        if not concurso:
            # se for passado um numero de concurso, os scores serão gerados apenas até o concurso informado.
            # se não, vamos forçar um número bem maior para que todos concursos passem no filtro
            concurso = int(self.ultimo_concurso_cache()[0]) + 100
        resultados = [item[1] for item in resultados_ordenados if int(item[0]) < concurso]

        if ultimos_concursos:
            resultados = resultados[-ultimos_concursos:]

        #if ultimos_concursos:
        #    resultados = []
        #    ultimo_concurso = int(self.ultimo_concurso_cache()[0])
        #    range_concursos = range(ultimo_concurso, ultimo_concurso-ultimos_concursos, -1)
        #    resultados_items = self.cache['resultados'].items()
        #    for concurso in range_concursos:
        #        resultados.append(self.cache['resultados'][str(concurso)])

        for resultado in resultados:
            for numero in resultado:
                numero = str(numero)
                dicionario[numero] = dicionario[numero] + 1
        dicionario = dicionario.items()

        sentido_ordenacao = True    # True = Reserved = Do maior para o menor (nosso padrao global)
        if ordenar == "-":
            sentido_ordenacao = False

        return sorted(dicionario, key=lambda numero: numero[1], reverse=sentido_ordenacao)

    def frequencia_numeros(self, lista=None, visual=None, ultimos_concursos=None, concurso=None, ordenar="score"):
        if visual:
            self._log("Mostra uma representação gráfica do comportamento de cada número quanto a ser sorteado ou não na linha do tempo")
        else:
            self._log("Indica com qual intervalor de jogos em média o número costuma sair e o Score indicando a chances de sair agora")

        if not lista:
            lista = range(1, self.total_dezenas+1)

        dicionario = {}
        dicionario_visual = {}

        # preparando a amostra de forma ordenada
        resultados_ordenados = sorted(self.cache['resultados'].items(),  key=lambda resultado:int(resultado[0]))
        if not concurso:
            # se for passado um numero de concurso, os scores serão gerados apenas até o concurso informado.
            # se não, vamos forçar um número bem maior para que todos concursos passem no filtro
            concurso = int(self.ultimo_concurso_cache()[0]) + 100
        resultados = [item[1] for item in resultados_ordenados if int(item[0]) < concurso]

        if ultimos_concursos:
            resultados = resultados[-ultimos_concursos:]

        # calculando a frequencia dos escolhidos
        target_central = 1.00
        for numero in lista:
            dicionario[str(numero)] = ""
            dicionario_visual[str(numero)] = ""
            numero_str = str(numero)
            counter_naosaiu = 0
            media_saiacada = 0
            for resultado in resultados:
                if numero in resultado:
                    media_saiacada = (media_saiacada + counter_naosaiu)/2.0
                    counter_naosaiu = 0
                    dicionario_visual[numero_str] += "1"
                else:
                    counter_naosaiu += 1
                    dicionario_visual[numero_str] += "-"
            if media_saiacada != 0:
                score_numero = (1/media_saiacada)*(counter_naosaiu+0.01) # smoothing counter_naosaiu
                diff_central = abs(score_numero - target_central)
                dicionario[numero_str] = [media_saiacada, counter_naosaiu, score_numero, diff_central]
            else:
                # score negativo para que nao atrapalhe as demais stats quando a
                # amostra for pequena. Diff_central zerada obviamente
                dicionario[numero_str] = [media_saiacada, counter_naosaiu, -1, 0]

        if visual:
            def repetitions(string, shorty=False):
                padroes = []
                r = re.compile(r"(.+)\1+")
                if shorty:
                    r = re.compile(r"(.+?)\1+")
                for match in r.finditer(string):
                    padroes.append((match.group(1), len(match.group(0))/len(match.group(1))))
                return padroes

            if len(lista) == 1:
                padroes = repetitions(dicionario_visual.values()[0])
                media_tamanho_padrao = reduce(lambda x,y:x+y, map(lambda padrao: len(padrao[0]), padroes)) / len(padroes)
                max_recorrencia = max(map(lambda padrao: padrao[1], padroes))
                padroes_filtrados = []
                for padrao in padroes:
                    if len(padrao[0]) > (media_tamanho_padrao * max_recorrencia):
                        padroes_filtrados.append(padrao)
                return sorted(padroes_filtrados, key=lambda padrao: len(padrao[0]))
            return sorted(dicionario_visual.items(), key=lambda numero: numero[0])
        else:
            self._log("Numero\t Media cada quantos Concursos sai\t  Nao sai a X Concursos\t Score")

            # trabalhando a ordenacao dos resultados
            sentido_ordenacao = True    # True = Reversed, do maior para o menor
            chave_ordenacao = 2
            ordenar = ordenar.replace("+", "")

            if ordenar == "score":
                sentido_ordenacao = True
                chave_ordenacao = 2
            elif ordenar == "-score":
                sentido_ordenacao = False
                chave_ordenacao = 2
            elif ordenar == "atraso":
                chave_ordenacao = 1
                sentido_ordenacao = True
            elif ordenar == "-atraso":
                chave_ordenacao = 1
                sentido_ordenacao = False
            elif ordenar == "media":
                chave_ordenacao = 0
                sentido_ordenacao = True
            elif ordenar == "-media":
                chave_ordenacao = 0
                sentido_ordenacao = False
            elif ordenar == "central":
                chave_ordenacao = 3
                sentido_ordenacao = False   # invertido pela lógica
            elif ordenar == "-central":
                chave_ordenacao = 3
                sentido_ordenacao = True    # invertido pela lógica

            return sorted(dicionario.items(), key=lambda numero: numero[1][chave_ordenacao], reverse=sentido_ordenacao)


    def menos_sorteados(self, quantidade=None, concurso=None, ultimos_concursos=None):
        quantidade = quantidade or self.max_acertos
        return self.estatisticas_numeros(concurso=concurso, ultimos_concursos=ultimos_concursos, ordenar="-")[:quantidade]

    def mais_sorteados(self, quantidade=None, concurso=None, ultimos_concursos=None):
        quantidade = quantidade or self.max_acertos
        return self.estatisticas_numeros(concurso=concurso, ultimos_concursos=ultimos_concursos, ordenar="+")[:quantidade]

    def menor_score(self, quantidade=None, concurso=None, ultimos_concursos=None):
        quantidade = quantidade or self.max_acertos
        return self.frequencia_numeros(concurso=concurso, ultimos_concursos=ultimos_concursos, ordenar="-score")[:quantidade]

    def maior_score(self, quantidade=None, concurso=None, ultimos_concursos=None):
        quantidade = quantidade or self.max_acertos
        return self.frequencia_numeros(concurso=concurso, ultimos_concursos=ultimos_concursos, ordenar="score")[:quantidade]

    def medio_score(self, quantidade=None, concurso=None, ultimos_concursos=None):
        """ Retorna os números com score médio baseado nos parâmetros da Loteria """
        # calculando os índices baseado nos parâmetros
        quantidade = quantidade or self.max_acertos
        inicio = (self.total_dezenas - quantidade)/2
        final = inicio + quantidade
        # filtrando dos resultados pré-ordenados
        return self.frequencia_numeros(concurso=concurso, ultimos_concursos=ultimos_concursos)[inicio:final]

    def range_score(self, min=0.85, max=1.15, concurso=None, ultimos_concursos=None):
        """ Retorna os números cujo score esteja dentro do range definido [min, max], inclusive """
        selecionados = []
        frequencias = self.frequencia_numeros(concurso=concurso, ultimos_concursos=ultimos_concursos)
        for numero in frequencias:
            if numero[1][2] >= min and numero[1][2] <= max:
                selecionados.append(numero)
        return selecionados

    def central_score(self, quantidade=None, concurso=None, ultimos_concursos=None):
        quantidade = quantidade or self.max_acertos
        return self.frequencia_numeros(concurso=concurso, ultimos_concursos=ultimos_concursos, ordenar="central")[:quantidade]

    def border_score(self, quantidade=None, concurso=None, ultimos_concursos=None):
        quantidade = quantidade or self.max_acertos
        return self.frequencia_numeros(concurso=concurso, ultimos_concursos=ultimos_concursos, ordenar="-central")[:quantidade]

    def maior_atraso(self, quantidade=None, concurso=None, ultimos_concursos=None):
        quantidade = quantidade or self.max_acertos
        return self.frequencia_numeros(concurso=concurso, ultimos_concursos=ultimos_concursos, ordenar="atraso")[:quantidade]

    def menor_atraso(self, quantidade=None, concurso=None, ultimos_concursos=None):
        quantidade = quantidade or self.max_acertos
        return self.frequencia_numeros(concurso=concurso, ultimos_concursos=ultimos_concursos, ordenar="-atraso")[:quantidade]


if (__name__ == '__main__'):
    lotofacil = LoteriaBase()
    print lotofacil.frequencia_numeros()
