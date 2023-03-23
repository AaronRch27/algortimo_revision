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


libro = '02_CNSIPEF_2023_M2_.xlsx'
# libro = 'pregunta_prueba.xlsx'

#Estos modelos solo funcionan si se cargan desde el main, es decir, este script kjunto con tokenizar,clasificadorBayes 
modelo1 = joblib.load('Recursos/modelo_primer_filtro.sav')

vector1 = joblib.load('Recursos/vectorizador_fil.sav')

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
#identificar censo, módulo y si fuese el caso, sección:
nombre = libro #nombre del cuestionario con punto xlsx
censos = ['CNIJF','CNDHF','CNSPF','CNSIPEF','CNGF','CNPJF']  
identificador = {'censo':'','modulo':'','seccion':''}
for censo in censos:
    if censo in nombre:
        identificador['censo'] = censo
        break
c = 0
for letra in nombre:
    if letra == 'M':
        try:
            if nombre[c+1].isdigit():
                identificador['modulo'] = nombre[c+1]
        except:
            pass
    if letra == 'S':
        try:
            if nombre[c+1].isdigit():
                identificador['seccion'] = nombre[c+1]
        except:
            pass
    c += 1

nombre_compuesto = f"validaciones_{identificador['censo']}_M{identificador['modulo']}_S{identificador['seccion']}"
if identificador['censo'] == '':
    nombre_compuesto = 'veamos' #porque es de pruebas ya que no pertenece a cuestionario
        
#identificar si ya existe base de datos con validaciones a ejecutar
if os.path.exists(f"Recursos/{nombre_compuesto}.csv"):
    indicaciones = pd.read_csv(f"Recursos/{nombre_compuesto}.csv")
    #en caso de que ya exista se corre directamente la comprobación
    list_erro = errores(cuestionario,libro,indicaciones)
    
else:
    os.system(f"start EXCEL.EXE {libro}")
    crear_base = recibir(cuestionario,nombre_compuesto)
#aquí tendrá que haber una division para revision o para crear archivo de revision
# list_erro = errores(cuestionario,libro)

#desactivar el proceso de generacion de base debido a que da muchos errores en spyder (no errores de codigo sino con el kernel, se traba o algo)
# crear_base = recibir(cuestionario,libro)