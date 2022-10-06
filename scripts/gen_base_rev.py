# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 12:33:15 2022

@author: AARON.RAMIREZ
"""

import pandas as pd
import tkinter as tk


def recibir(cuestionario,libro):
    """
    

    Parameters
    ----------
    cuestionario : un diccionario con los objeto pregunta organizados por
    sección
    libro : str nombre del archivo que está siendo leído

    Returns
    -------
    None.

    """
    base = {'preguntas':[],'blanco':[],'aritmetico':[],'suma_numeral':[],
            'espeficique':[],'errores_registro':[],'salto_preguntas':[],
            'preguntas_relacionadas':[]
            }
    #primer paso es conseguir lista con nombres de preguntas
    lista_preguntas = consg_p(cuestionario)
    base['preguntas'] = lista_preguntas

    
    return

def consg_p(c):
    "c es cuesitonario"
    r = []
    for seccion in c:
        r += list(c[seccion])
    return r
    