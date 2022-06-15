# -*- coding: utf-8 -*-
"""
Created on Fri May 13 14:38:09 2022

@author: AARON.RAMIREZ
"""
from principal_revision import procesar
import pandas as pd
from complemento_modelos import tokenizar,clasificadorBayes
import joblib

libro = 'pregunta_prueba.xlsx'


modelo1 = joblib.load('modelo_primer_filtro.sav')

vector1 = joblib.load('vectorizador_fil.sav')

modelo2 = joblib.load('modelo_segundo_filtro.sav')

vector2 = joblib.load('vectorizador_fil2.sav')

modelos = [modelo1, vector1, modelo2, vector2]



pags = pd.ExcelFile(libro).sheet_names

saltar = [
    'Índice',
    'Presentación',
    'Informantes',
    'Participantes',
    'Glosario']

cuestionario = {}
for pag in pags:
    
    if pag not in saltar:
        data = pd.read_excel(libro,sheet_name=pag,engine='openpyxl')
        aver = procesar(data, pag,modelos)
        cuestionario[pag] = aver