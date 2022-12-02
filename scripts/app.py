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
    if os.path.exists(camino+'veamos.csv'):
        indicaciones = pd.read_csv(camino+'veamos.csv')
        #en caso de que ya exista se corre directamente la comprobación
        list_erro = errores(cuestionario,libro,indicaciones)
        ventana.destroy()
    else:
        abrir = libro.split('/')
        abrir = abrir[-1]
        os.system(f"start EXCEL.EXE {abrir}")
        ventana.destroy()
        crear_base = recibir(cuestionario,libro)
        
boton1 = tk.Button(ventana, text ="Iniciar", command = ruta)
boton1.pack()
ventana.mainloop()

