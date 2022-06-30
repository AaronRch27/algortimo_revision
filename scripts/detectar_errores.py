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
    print(aritme)
    return


def aritmeticos(cuestionario):
    "comprobar errores aritmeticos en cada tabla"
    errores = {}
    for llave in cuestionario:
        for pregunta in cuestionario[llave]:
            if cuestionario[llave][pregunta].tipo_T == 'Tabla':
                tablas = cuestionario[llave][pregunta].tablas
                for tabla in tablas:
                    er = totales_fila(tablas[tabla])
                    if er:
                        errores[pregunta] = er
            if cuestionario[llave][pregunta].tipo_T == 'NT_Desagregados':
                tablas = cuestionario[llave][pregunta].tablas
                for tabla in tablas:
                    er = totales_columna(tablas[tabla])
                    if er:
                        errores[pregunta] = er
    
    return errores

def totales_columna(df1):
    "leer dataframe de desagregados por columna y regresar error"
    df = df1.fillna('...')
    errores = {}
    c = 0
    for col in df:
        lista = list(df[col])
        #eliminar nan
        if '...' in lista:
            lista.remove('...')
        #aquí el primer valor suele ser el total, hay que pasarlo hasta el último para que se cumpla la utilidad de la función evaluar_suma
        if len(lista) > 2: #porque algunas columnas solo tendrán un valor, a esas no se les hace este proceso
            ins = lista[-1] #es el total
            lista.insert(0, ins)
            lista.pop(-1)
            aritme = evaluador_suma(lista)
            if aritme:
                if col in errores:
                    errores[col].append(aritme)
                else:
                    errores[col] = aritme
        c += 1
    return errores

def totales_fila(df):
    "leer dataframe de tablas normales, regresar error"

    total = []
    subtotal = []
    c = 0
    for colum in df:
        if 'Total' in colum:
            total.append(c)
        if 'Subtotal' in colum:
            subtotal.append(c)
        c += 1
    # print(total,subtotal)
    errores = {}
    if total and not subtotal:
        c = 0
        for tot in total:
            c1 = 0
            
            for fila in list(df.iloc[:,0]):
                
                try:
                    lista = list(df.iloc[c1, tot:total[c+1]])
                except:
                    lista = list(df.iloc[c1, tot:])
                aritmetic = evaluador_suma(lista)
                if aritmetic:
                    errores[c1] = evaluador_suma(lista)
                
                c1 += 1
            c += 1
    
    if total and subtotal:
        desagre_totales = [] #lista de los totales de desagregados
        limites = []
        for tota in total:

            for sub in subtotal:
                if sub > tota:
                    limites.append(sub) #límites tendrá un numero por cada elemento mayor a cada total detectado
                    break
        c = 0
        for limite in limites:#generar listas con columnas intermedias entre un total y su primer subtotal
            if limite-total[c]>0:
                lista_columnas =[i for i in range(total[c]+1,limite)]#el mas uno es porque necesitamos saber la columna a partir del total
            else:
                lista_columnas =[i for i in range(total[c],limite)]
            desagre_totales.append(lista_columnas)
            c += 1
        #hacer listas de cada total desagregado con sus respectivos desagregados
        for desa in desagre_totales:
            ref = len(desa)
            comp = []
            c = 0
            for sub in subtotal:
                if c > 0:
                    resta = sub - subtotal[c-1] - 1 #menos uno para quitar la columna del subtotal y que solo queden las de los desagregados
                    comp.append(resta)
                c += 1
            cant_col = df.shape
            resta = cant_col[1]-subtotal[-1] - 1
            comp.append(resta) #porque en la iteración falta el último subtotal contra la cantidad de columnas
            # print(ref,comp,desagre_totales)
            #hacer las listas y enviar a la funcion evaluadora por los totales/desagregados en los subtotales
            c2 = 1 #tiene que iniciar desde 1 porque no deseamos almacenar el valor del subtotal sino del que sigue
            for des in desa:
                
                c = 0
                for fila in list(df.iloc[:,0]):#primero se itera por fila del df
                    lista_fila = list(df.iloc[c,:])#se saca la lista de los valores de la fila
                    lista = [lista_fila[des]] #esta es la lista que eventualmente pasará a ser evaluda. Inicia con el total del desagregado y se complementa con los desagregados de cada subtotal
                    c1 = 0
                    for sub in subtotal:
                        if sub > des: #para no trabajar con subtotales de otro total
                            if comp[c1] == ref:
                                agregar =  lista_fila[sub+c2]
                                lista.append(agregar)
                            if comp[c1] > ref:
                                div = comp[c1]//ref
                                for i in range(div):
                                    aumento = ref*i
                                    agregar = lista_fila[sub+c2+aumento]
                                    lista.append(agregar)
                            
                        c1 += 1
                    aritmetic = evaluador_suma(lista)
                    if aritmetic:
                        errores[c] = evaluador_suma(lista)
                    c += 1
                c2 += 1
            #en el ciclo for que conluye, se revisan únicamente los desagregados del total
        # a continuación se revisa el total con sus subtotales
        c = 0
        for fila in list(df.iloc[:,0]):
            lista_fila = list(df.iloc[c,:])
            for tot in total:
                lista = [lista_fila[tot]]
                for sub in subtotal:
                    if sub > tot:
                        lista.append(lista_fila[sub])
                
                aritmetic = evaluador_suma(lista)
                if aritmetic:
                    
                    errores[c] = evaluador_suma(lista)
            c += 1
        # ahora se revisan los subtotales con sus desagregados
        rsubtotal = subtotal+[]#un respaldo de subtotal por si se necesita después
        subtotal += total #se juntan para validar todo de una vez, cada uno por separado con sus desagregados
        subtotal.sort()
        
        c = 0
        for fila in list(df.iloc[:,0]):
            lista_fila = list(df.iloc[c,:])
            for sub in subtotal:
                try:
                    lista = [lista_fila[sub:subtotal[c+1]]]
                except:#para cuando llegue a la ultima columna de subtotales
                    lista = [lista_fila[sub:]]
                aritmetic = evaluador_suma(lista)
                if aritmetic:
                    errores[c] = evaluador_suma(lista)
            c += 1
        

                    
                    
    return errores

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
    if len(lista) < 3:#posteriormente entará otra comprobación aquí
        return 
    else:
        errores = []
        total = lista[0]
        convertir = ['NS','NA','na','ns','Na','Ns','nA','nS']
        na = 'No'
        ns = 'No'
        blanco = 0
        comprobar = 'No'
        desagregados = lista[1:]
        c = 0
        for valor in desagregados:
            if valor == 'borra':
                blanco += 1
            if valor in convertir:
                if valor.lower() == 'na':
                    na = 'Si'
                if valor.lower() == 'ns':
                    ns = 'Si'
                comprobar = 'Si'
                desagregados[c] = 0
            if type(valor) == str and valor not in convertir:
                desagregados[c] = 0
                if valor != 'borra':
                    errores.append('Error: valor no permitido')
            c += 1
        suma = sum(desagregados)
        if blanco > 0:
            if total == 'borra':
                blanco += 1
                if len(lista) == blanco:
                    return
                else:
                    errores.append('Hay espacios en blanco')
                    return errores
            if total != 'borra':
                errores.append('Hay espacios en blanco')
                return errores
        if total in convertir and suma > 0:
            errores.append('Error: Suma de desagregados no puede ser mayor a cero si total es NS o NA')
            return errores
        if total in convertir and suma == 0:
            if total.lower() == 'na' and ns == 'Si':
                errores.append('Error: Si el total es NA ninguno de sus desagregados puede ser NS')
        if type(total) == str and total not in convertir:
            errores.append('Error: el total es un valor no permitido como respuesta')
            return errores
        if type(total) != str:
            if total != suma:
                if total >= 0 and comprobar == 'No' and suma > 0:
                    errores.append('Error: Suma de desagregados no coincide con el total')
                if total == 0 and ns == 'Si':
                    errores.append('Si el total es cero, ningún desagregado puede ser NS')
            
        return errores
    
    return