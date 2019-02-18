#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#       lotofacil.py - Script para conferir resultados da Lotofácil (Loteria Brasileira)
#
#       Copyright 2011 Thomas Jefferson Pereira Lopes <thomas@thlopes.com>
#       Parte integrante do projeto PyLottery (https://bitbucket.org/THLopes/pylottery)
#
#       Uso: python lotofacil.py [ARQUIVO] [CONCURSO] [RESULTADO]
#         CONCURSO = número do concurso a conferir, por exemplo, 1245
#         ARQUIVO = nome do arquivo com os jogos, na seguinte sintaxe:
#           [nomedojogador1,670,674]
#           1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
#           1,3,5,7,9,10,12,14,16,18,19,20,21,23,25
#
#           [nomedojogador2,673,681]
#           2,3,6,7,9,11,13,15,17,18,19,20,22,24,25
#
#           [nomedojogador3]
#           3,6,7,9,11,13,15,17,18,19,20,21,22,23,24
#           ...
#         RESULTADO = Coloque o resultado manual caso queira conferir algum
#            sorteio que ainda nao foi publicado no site da caixa, com os numeros
#            separados por virgula, sem espacos. Ex.: 1,7,22,31,40,58
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

import sys
from base import LoteriaBase


class Lotofacil(LoteriaBase):
    """ Classe para processar a Lotofácil, herdada de LoteriaBase, que foi inspirada nessa """
    def __init__(self, mensagens=True, cache=True):
        super(Lotofacil, self).__init__(name="lotofacil",
                              total_dezenas=25,
                              min_acertos= 11,
                              max_acertos = 15,
                              arquivo="lotofacil.txt",
                              url_base="http://www1.caixa.gov.br/loterias/loterias/lotofacil/lotofacil_pesquisa_new.asp",
                              intervalo_medio=2,
                              mensagens=mensagens,
                              cache=cache)

    # A classe não implementa os métodos que deveriam ser sobrescritos pois
    #   LoteriaBase já foi criada baseada na Lotofácil.


def main():
    concurso = None
    resultado_manual = None

    if (len(sys.argv) > 1):
        concurso = int(sys.argv[1])
    if (len(sys.argv) > 2):
        resultado_manual = sys.argv[2]

    lotofacil = Lotofacil()
    total_premios = 0
    linhas_premiadas = []

    total_premios, linhas_premiadas = lotofacil.conferir(concurso, resultado=resultado_manual)

if (__name__ == '__main__'):
    main()
