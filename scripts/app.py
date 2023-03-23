# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 08:56:58 2022

@author: AARON.RAMIREZ
"""

from principal_revision import procesar
from detectar_errores import errores
import pandas as pd
from complemento_modelos import tokenizar,clasificadorBayes
import joblib
from gen_base_rev import recibir
import os
import tkinter as tk


ventana = tk.Tk()
ventana.title('Prueba')
ventana.geometry('300x100')
tk.Label(ventana, 
         text="Hola, para iniciar presiona el botón y selecciona un cuestionario",
         wraplength=150).pack() 


def ruta():
    archivo = tk.filedialog.askopenfile(mode='r')
    libro = archivo.name
    camino = libro.split('/')
    cam = ''
    for ca in camino[:-1]:
        cam += ca+'/'
    camino = cam #toda la ruta del archivo pero sin el nombre del archivo
    # libro = libro.split('/')
    # libro = libro[-1]
    modelo1 = joblib.load('Recursos/modelo_primer_filtro.sav')

    vector1 = joblib.load('Recursos/vectorizador_fil.sav')

    # modelo2 = joblib.load('modelo_segundo_filtro.sav')

    # vector2 = joblib.load('vectorizador_fil2.sav')

    modelos = [modelo1, vector1]


    guide = pd.ExcelFile(libro)
    pags = guide.sheet_names

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
    abrir = libro.split('/')
    abrir = abrir[-1]
    nombre = abrir #nombre del cuestionario con punto xlsx
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
    if os.path.exists(f"Recursos/{nombre_compuesto}.csv"):#quita la ruta de variable camino porque no se necesita ya que es en el mismo directorio donde se ejecuta
        indicaciones = pd.read_csv(f"Recursos/{nombre_compuesto}.csv")
        #en caso de que ya exista se corre directamente la comprobación
        list_erro = errores(cuestionario,libro,indicaciones)
        ventana.destroy()
    else:
        os.system(f"start EXCEL.EXE {abrir}")
        ventana.destroy()
        crear_base = recibir(cuestionario,nombre_compuesto)
    guide.close()
        
boton1 = tk.Button(ventana, text ="Iniciar", command = ruta)
boton1.pack()
ventana.mainloop()

