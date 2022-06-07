# -*- coding: utf-8 -*-
"""
Created on Fri May 13 14:38:09 2022

@author: AARON.RAMIREZ
"""
from principal_revision import procesar
import pandas as pd

libro = 'CNSIPEF_2022_M2_R2_LIB_Reconsulta.xlsx'

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
        aver = procesar(data, pag)
        cuestionario[pag] = aver