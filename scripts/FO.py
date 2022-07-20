# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 14:24:07 2022

@author: Aaron Ramírez
"""
import openpyxl as op

formato = 'FO_2022.xlsx'#path del formato de observaciones en blanco

libro = op.load_workbook(formato)

pagina = libro['M1']


def generar_formato(errores,censo,nombre):
    """
    

    Parameters
    ----------
    errores : dict
        diccionario: llaves son nombres de pregunta con errores, cada
        pregunta contiene otro diccionario con sus tipos de error.
    censo : str
        Nombre del censo
    nombre : str
        Nombre del cuestionario

    Returns
    -------
    None.

    """
    fila = 18
    for pregunta in errores:
        
        if not errores[pregunta]:
            pass
        for inconsistencia in errores[pregunta]:
            if inconsistencia == 'Consistencia':
                pagina[f'E{fila}'] = ''.join(errores[pregunta][inconsistencia])
                fila += 1
    
    libro.save(f'FO{nombre}')
    return