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
from gen_base_rev import recibir
import os

#No olvidar marcar los complementos con el inicio de su pregunta y un ## donde termina


# libro = 'CNDHF_2022_M1_R3.xlsx'
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
        
#identificar si ya existe base de datos con validaciones a ejecutar
if os.path.exists('veamos.csv'):
    indicaciones = pd.read_csv('veamos.csv')
    #en caso de que ya exista se corre directamente la comprobación
    list_erro = errores(cuestionario,libro,indicaciones)
    
else:
    crear_base = recibir(cuestionario,libro)
#aquí tendrá que haber una division para revision o para crear archivo de revision
# list_erro = errores(cuestionario,libro)

#desactivar el proceso de generacion de base debido a que da muchos errores en spyder (no errores de codigo sino con el kernel, se traba o algo)
# crear_base = recibir(cuestionario,libro)