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
            if inconsistencia == 'registro':
                desc = 'En tabla de delitos para tipos de víctima, no se puede registar datos distintos a cero en numerales indicados por columna a continuación'+str(errores[pregunta][inconsistencia])
                escribir(pregunta,'Errores de registro (letras en lugar de números, respuestas diferentes al catálogo proporcionado, NS o NA aplicado incorrectamente)',
                         desc,fila,pagina)
                fila += 1
                continue 
            if inconsistencia == 'catalogo':
                desc = ' : '.join(errores[pregunta][inconsistencia])
                escribir(pregunta,'Errores de registro (letras en lugar de números, respuestas diferentes al catálogo proporcionado, NS o NA aplicado incorrectamente)',
                         desc,fila,pagina)
                fila += 1
                continue
            if inconsistencia == 'numerales y columnas  donde otros delitos son mayores a 25%':
                desc = ' , '.join(errores[pregunta][inconsistencia])
                desc = 'Numerales y columnas donde otro tipo de delito supera el 25% de su bien jurídico: '+ desc
                escribir(pregunta,'Falta de comentario explicativo sobre diferencia de la información reportada con respecto al cumplimiento de la instrucción o validaciión establecida ',
                         desc,fila,pagina)
                fila += 1
                continue
            if 'aritmetico' == inconsistencia or type(inconsistencia) == int:#esto tiene que ser modificado
                clas_er = {'bl':[],'per':[],'tot':[]}
                for erro in errores[pregunta][inconsistencia]:
                    if 'blanco' in erro:
                        clas_er['bl'].append(erro)
                        continue
                    if 'permitido' in erro:
                        clas_er['per'].append(erro)
                        continue
                    if 'total' in erro:
                        clas_er['tot'].append(erro)
                        continue
                    
                if clas_er['bl']:
                    desc = ' : '.join(clas_er['bl'])
                    escribir(pregunta,'Preguntas incompletas (con espacios en blanco)',
                              desc,fila,pagina)
                    fila += 1
                if clas_er['per']:
                    desc = ' : '.join(clas_er['per'])
                    escribir(pregunta,'Errores de registro (letras en lugar de números, respuestas diferentes al catálogo proporcionado, NS o NA aplicado incorrectamente)',
                              desc,fila,pagina)
                    fila += 1
                if clas_er['tot']:
                    desc = ' : '.join(clas_er['tot'])
                    escribir(pregunta,'Errores de congruencia aritmética',
                              desc,fila,pagina)
                    fila += 1
    
    libro.save(f'FO{nombre}')
    return

def orden_error(lista):
    lista_listas = []
    return lista_listas

def escribir(pregunta,Ti,descripcion,fila,pagina):
    "Ti es tipo de inconsistencia"
    pagina[f'C{fila}'] = pregunta
    pagina[f'D{fila}'] = Ti
    pagina[f'E{fila}'] = descripcion
    return
