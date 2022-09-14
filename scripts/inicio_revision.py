# -*- coding: utf-8 -*-
"""
Created on Fri May 13 14:38:09 2022

@author: AARON.RAMIREZ
"""
from principal_revision import procesar
from detectar_errores import errores
import pandas as pd
from complemento_modelos import tokenizar,clasificadorBayes
import joblib

#No olvidar marcar los complementos con el inicio de su pregunta y un ## donde termina


# libro = 'CNPJF_2022_M2_R3.xlsx'
libro = 'pregunta_prueba.xlsx'

#Estos modelos solo funcionan si se cargan desde el main, es decir, este script kjunto con tokenizar,clasificadorBayes 
modelo1 = joblib.load('modelo_primer_filtro.sav')

vector1 = joblib.load('vectorizador_fil.sav')

# modelo2 = joblib.load('modelo_segundo_filtro.sav')

# vector2 = joblib.load('vectorizador_fil2.sav')

modelos = [modelo1, vector1]



pags = pd.ExcelFile(libro).sheet_names

saltar = [
    'Índice',
    'Presentación',
    'Informantes',
    'Participantes',
    'Glosario']

if 'Glosario' in pags:#si tiene glosario es un cuestionario. Aveces incluyen hojas ocultas por alguna razón pero esas no deben ser validadas con este método ya que no forman parte como tal del cuestionario
    saltar += [f'Hoja{i}' for i in range(1,6)]

cuestionario = {}
for pag in pags:
    
    if pag not in saltar:
        data = pd.read_excel(libro,sheet_name=pag,engine='openpyxl',
                             na_values=[''], keep_default_na=False)
        seccion = procesar(data, pag,modelos)
        cuestionario[pag] = seccion

list_erro = errores(cuestionario,libro)