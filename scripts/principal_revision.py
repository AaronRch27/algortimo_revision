# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 14:05:03 2022
@author: AARON.RAMIREZ
"""
import numpy as np
import pandas as pd
from clase_preguntas import clase_pregunta


def preguntas(hopan):
    """
    
    Parameters
    ----------
    hopan : es un dataframe de pandas.
    Returns
    -------
    ind : (list).
    Regresa una lista con el número de fila en la que detectó cada pregunta.
    Aquí se incluye lo de los número romanos
    """
    
    c=0
    ind=[]
    for i in hopan['Unnamed: 0']:
        a = pd.isna(hopan['Unnamed: 0'][c])
        if a == False:
            ind.append(c)
        c+=1
    
    return ind


def espacio(hopan,preguntas):
    """
    
    Parameters
    ----------
    hopan : dataframe de pandas.
    preguntas : (list). Corresponde a la lista que genera la 
    función preguntas
    Returns
    -------
    di : (dict). Regresa diccionario con el numero de la fila 
    donde hay pregunta como llave, y su valor es el espacio que abarca 
    (es una lista de dos valores)
    """
    
    a = preguntas
    di = {}
    con = 0
    b = len(hopan)
    for i in a:
        try:
            di[con]=[a[con],a[con+1]]
        except:
            di[con]=[a[con],b]
        con+=1
    
    return di


def imagen(cor,hopan,preguntas,seccion,modelos):
    """
    
    Parameters
    ----------
    cor : tupla, creo, con el tamaño de pregunta inicio y término
    hopan : Dataframe de pandas.
    preguntas : (list). Lista de preguntas
    contenedor: dic Diccionario donde se almacenarán las preguntas
    Returns
    -------
    ente : (dict).genera un diccionario con filas y columnas en los que se 
    registra un valor de la pregunta
    """
        
    a = cor[0]
    b = cor[1]
    if 'Sec' in seccion:
        mdf = hopan.iloc[a:b,0:31]
    else:
        mdf = hopan.iloc[a:b]
    mdf = mdf.reset_index(drop=True)
    objeto = clase_pregunta(mdf, seccion,modelos)
    
    return objeto


def procesar(hopan,seccion,modelos):
    """
    
    Parameters
    ----------
    hopan : Dataframe pandas con todo el cuestionario
        
    seccion : str
        string con nombre de la seccion.
    Returns
    -------
    None.
    """
    lista_preguntas = preguntas(hopan)
    tam_preguntas = espacio(hopan, lista_preguntas)
    # print(lista_preguntas,tam_preguntas)
    contador = 0
    cuestionario = {}#aqui se van a almacenar las preguntas como objetos
    for preg in lista_preguntas:
        objeto = imagen(tam_preguntas[contador], hopan, preg, seccion,modelos)
        cuestionario[objeto.nombre] = objeto
        print('pregunta creada con nombre ', objeto.nombre)
        contador += 1
        
    return cuestionario
        