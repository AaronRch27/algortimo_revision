# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 14:24:07 2022

@author: Aaron Ramírez
"""
import openpyxl as op
from datetime import datetime




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
    formato = 'FO_2022.xlsx'#path del formato de observaciones en blanco

    libro = op.load_workbook(formato)
    
    pagina = libro['M1']
    pagina['D11'] = censo
    pagina['D14'] = datetime.now().strftime('%d/%m/%Y')
    fila = 18
    for pregunta in errores:
        
        if not errores[pregunta]:
            pass
        for inconsistencia in errores[pregunta]:
            if inconsistencia == 'Consistencia':
                desc = ' : '.join(errores[pregunta][inconsistencia])
                escribir(pregunta,'Errores de consistencia entre preguntas',
                         desc,fila,pagina)
                fila += 1
                continue
            if inconsistencia == 'catalogo':
                desc = ''.join(errores[pregunta][inconsistencia])
                escribir(pregunta,'Errores de registro (letras en lugar de números, respuestas diferentes al catálogo proporcionado, NS o NA aplicado incorrectamente)',
                         desc,fila,pagina)
                fila += 1
                continue
            if 'aritmetico' == inconsistencia or type(inconsistencia) == int:#esto tiene que ser modificado
                for erro in errores[pregunta][inconsistencia]:
                    if 'blanco' in erro:
                        escribir(pregunta,'Preguntas incompletas (con espacios en blanco)',
                                 erro,fila,pagina)
                        fila += 1
                        continue
                    if 'permitido' in erro:
                        escribir(pregunta,'Errores de registro (letras en lugar de números, respuestas diferentes al catálogo proporcionado, NS o NA aplicado incorrectamente)',
                                 erro,fila,pagina)
                        fila += 1
                        continue
                    if 'total' in erro:
                        escribir(pregunta,'Errores de congruencia aritmética',
                                 erro,fila,pagina)
                        fila += 1
                        continue
                
    
    libro.save(f'FO{nombre}')
    return

def escribir(pregunta,Ti,descripcion,fila,pagina):
    "Ti es tipo de inconsistencia"
    pagina[f'C{fila}'] = pregunta
    pagina[f'D{fila}'] = Ti
    pagina[f'E{fila}'] = descripcion
    return
