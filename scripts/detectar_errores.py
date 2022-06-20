# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 14:27:15 2022

@author: AARON.RAMIREZ
"""

def errores(cuestionario):
    """
    

    Parameters
    ----------
    cuestionario : Dic
        Cuestionario es lo que se genera luego de convertir todo el 
        documento de excel a dataframes y sus propiedades. Contiene 
        entonces llaves para cada pestaña del documento con preguntas
        validables, y en cada llave hay otras llaves, una por pregunta.

    Returns
    -------
    Regresa una lista con los errores detectados en tres áreas: 
        errores aritméticos, errores de omision de especifique y
        erores de relaciones entre preguntas; unicamente comparaciones
        de menores, mayores o iguales.
        
    Eventualmente, regresará el formato de observaciones con una fila por
    error detectado

    """
    aritme = aritmeticos(cuestionario)
    return


def aritmeticos(cuestionario):
    "comprobar errores aritmeticos en cada tabla"
    errores = []
    for llave in cuestionario:
        for pregunta in cuestionario[llave]:
            if cuestionario[llave][pregunta].tipo_T == 'Tabla':
                tablas = cuestionario[llave][pregunta].tablas
                for tabla in tablas:
                    er = totales(tablas[tabla])
                    if er:
                        errores.append(er)
    
    return errores

def totales(df):
    "leer dataframe, regresar error"

    total = []
    subtotal = []
    c = 0
    for colum in df:
        if 'Total' in colum:
            total.append(c)
        if 'Subtotal' in colum:
            subtotal.append(c)
        c += 1
    print(total,subtotal)
    if total and not subtotal:
        c = 0
        for tot in total:
            c1 = 0
            
            for fila in list(df.iloc[:,0]):
                
                try:
                    lista = list(df.iloc[c1, tot:total[c+1]])
                except:
                    lista = list(df.iloc[c1, tot:])
                print(lista)
                c1 += 1
            c += 1
            
            
    return

def evaluador_suma(lista):
    """
    

    Parameters
    ----------
    lista : list
        el primer valor de la lista debe ser el total y los demás
        sus desagregados, los cuales deben ser al menos dos, de 
        ser menos no hará la comprobación.

    Returns
    -------
     str. bien o mal dependiendo cómo se evalue la suma

    """
    if len(lista) > 3:
        return 'No se puede evaluar'
    
    
    return