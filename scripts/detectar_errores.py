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
    errores = iterar_cuestionario(cuestionario)
    print(errores)
    return


def iterar_cuestionario(cuestionario):
    "comprobar errores en cada pregunta"
    errores = {}
    for llave in cuestionario:
        for pregunta in cuestionario[llave]:
            tablas = cuestionario[llave][pregunta].tablas
            for tabla in tablas:
                df = tablas[tabla].copy()#con copia para no afectar el frame original
                ndf = quitar_sinonosabe(df)
                if cuestionario[llave][pregunta].tipo_T == 'Tabla':
                    aritmeticos = totales_fila(ndf,cuestionario[llave][pregunta].autosuma)
                    if aritmeticos:
                        errores[pregunta] = aritmeticos
                if cuestionario[llave][pregunta].tipo_T == 'NT_Desagregados':
                    aritmeticos = totales_columna(ndf)
                    if aritmeticos:
                        errores[pregunta] = aritmeticos
            #validación para todas las preguntas de si no no se sabe.
                otra_copia = tablas[tabla].copy()
                sinon = sinonosabe(otra_copia,cuestionario[llave][pregunta].autosuma)
                if sinon:
                    if pregunta in errores:
                        try:
                            errores[pregunta].append(sinon)
                        except:#si existe eror previo puede que no sea lista sin dict
                            for k in sinon:
                                if k in errores[pregunta]:
                                    errores[pregunta][k] += sinon[k]
                                if k not in errores[pregunta]:
                                    errores[pregunta][k] = sinon[k]
                    if pregunta not in errores:
                        errores[pregunta] = sinon
            #a continuacion, se buscan los errores por instrucciones de preguntas --hasta ahora solo de relaciones entre preguntas(consistencia)
            consist = consistencia(cuestionario,cuestionario[llave][pregunta]) 
            
            # instrucciones_clas = cuestionario[llave][pregunta].instruccio_clasificadas #es un diccionario. La instrucción es la llave y su valor de clasificacion es una string
            # for instruccion in instrucciones_clas:
            #     if instrucciones_clas[instruccion] == 'consistencia':
            #         comparacion = consistencia(cuestionario,instruccion,df)
    return errores

def consistencia(cuestionario,pregunta):
    """
    

    Parameters
    ----------
    cuestionario : Dict. Es el cuestionario generado luego de transofrmacion
        Se requiere todo para poder navegar entre las distintas preguntas
        para poder comparar relaciones entre ellas.
    pregunta : objeto pregunta
        La pregunta del cuestionario que será comparada con alguna otra.

    Returns
    -------
    errores. Dict. Regresa un diccionario con errores encontrados en la
        comparación de la pregunta.

    """
    #primer paso es filtrado de instrucciones clasificadas
    clasificadas = pregunta.instruccio_clasificadas
    ins_cons = [] #instrucciones de consistencia
    for instruc in clasificadas:
        if clasificadas[instruc] == 'consistencia':
            ins_cons.append(instruc)
            
    if not ins_cons:#en caos de no existir no tiene caso seguir con esta validación
        return
    #segundo paso, otro filtro de instrucciones de comparacion mayor menor o igual
    mayor = []
    menor = []
    igual = []
    for instru in ins_cons:
        rev = instru.lower()
        if 'mayor' in rev:
            mayor.append(rev)
            continue
        if 'menor' in rev:
            menor.append(rev)
            continue
        if 'igual' in rev:
            igual.append(rev)
            continue
    if mayor:
        for ins in mayor:
            mapa = mapeo(pregunta.nombre,1,ins)#mapear
            # valores = conseguir(cuestionario,mapa)#conseguir
            # comp = comparar(valores,mapa)#comparar y generar errores
    if menor:
        for ins in menor:
            mapa = mapeo(pregunta.nombre,2,ins)#mapear
            
    if igual:
        for ins in igual:
            mapa = mapeo(pregunta.nombre,3,ins)#mapear
    
        
    return

def mapeo(nombre,op,instruccion):
    """
    

    Parameters
    ----------
    nombre : str, nombre de la pregunta
    lista : list, lista de listas netgrada por lista en orden:
        mayor, menor igual

    Returns
    -------
    mapa. Dict, diccionario con nombre de la pregunta a la que se tiene
    que comparar, así como un número del 1 al 3 para saber si es mayor(1),
    menor(2) o igual(3). Finalmente el nombre de la columna o columnas
    a comparar y si es solo la parte de autosumas.

    """
    mapa = {}
    mapa['operacion'] = op
    texto = instruccion.split('igual')#divide en dos la cadena, la primera parte es sobre la pregunta actual y la segunda es para la pregunta a comparar
    #detectar a qué partes de la tabla de la pregunta van a ser comparadas
    p_actual = texto[0]
    p_comparar = texto[1]
    p_suma_a = p_actual.count('suma')
    p_suma_c = p_comparar.count('suma')
    actual = ''
    if p_suma_a > 0 and 'numeral' not in p_actual:#habrá que llenar de muchos condicionales para comprobar
        actual = 'autosuma'
    a_columna = ''
    if 'cada columna' in p_actual:
        a_columna = 'todas'
    mapa['p_act(fila,columna)'] = (actual,a_columna)
    print(mapa)
    return mapa

def sinonosabe(df,autosuma):
    """
    

    Parameters
    ----------
    df : dataframe de la pregunta

    Returns
    -------
    errores: dict. Regresa un diccionario con los errores detectados
    sobre contestar a preguntas de si no no se sabe dentro de tablas,
    así como las de no aplica (son preguntas en donde se debe dejar en
    blanco el resto de la fila o contestar puro cero o na, cualquier 
    otro valor es un error).

    """
    errores = {}
    df = df.replace({'borra':0})
    if autosuma == 'Si':#porque aquí también hay tablas con autosuma y esa fila no sirve para esta validacion
        bor = df.shape
        df = df.drop([bor[0]-1],axis=0)
    separar = []
    c = 0
    for columna in df:
        texto = columna.replace(' ','')#quitar espacios porque luego no lo escriben igual siempre
        comparar = '1.Sí/2.'
        if comparar in texto:
            separar.append(c)
        c += 1
    if not separar:#porque no se detectó columna que tenga lo que a esta validacion importa
        return
    c = 0
    for sep in separar:
        try:
            nf = df.iloc[:,sep:separar[c+1]]
        except:
            nf = df.iloc[:,sep:]#para el ultimo valor de la lista, o si solo hay uno
        lista = list(nf.iloc[:,0])
        c1 = 0
        for elemento in lista:
            fila = list(nf.iloc[c1])
            if fila[0] > 1:
                if sum(fila[1:]) > 0:
                    errores[c1] = ['Por respuesta de catálago, la suma de los desagregados no puede ser mayor que cero']
            if fila[0] == 0:
                errores[c1] = ['Faltó contestar pregunta de catálogo']
            c1 += 1
        c += 1
    return errores

def quitar_sinonosabe(df):
    """
    

    Parameters
    ----------
    df : Dataframe. Es la tabla de la pregunta a evaluar

    Returns
    -------
    df1: Dataframe. Regresa la tabla sin las columnas donde hay
    una pregunta de tipo "1. si 2. no..." Generalmente son 
    numerales 1, 2 y 9, pero aveces cambian e inclyen el 8 o el 3
    La idea es eliminarlos porque no son adecuados en una validación 
    de totales.

    """
    
    for columna in df:
        texto = columna.replace(' ','')#quitar espacios porque luego no lo escriben igual siempre
        comparar = '1.Sí/2.'
        if comparar in texto:
            del df[columna]
    return df

def totales_columna(df1):
    "leer dataframe de desagregados por columna y regresar error"
    df = df1.fillna('...')
    errores = {}
    c = 0
    for col in df:
        lista = list(df[col])
        #eliminar nan
        
        if '...' in lista:
            for element in range(len(lista)+1): #es necesario eliminar todos los '...' de la lista
                try:#esto es porque la cantidad de '...' suele variar en las listas, como pueden tener uno o pueden tener muchos
                    lista.remove('...')
                except:
                    pass
        
        #aquí el ultimo valor suele ser el total, hay que pasarlo hasta el principio para que se cumpla la utilidad de la función evaluar_suma
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

def totales_fila(df,autosuma):
    "leer dataframe de tablas normales, regresar error"
    errores = {}
    #eliminar autosumas si las hay, y también validar columnas, aunque ten teoría aquí no deberia haber errores por las fórmulas de autosuma:
    if autosuma == 'Si':
        # validar columnas:
        por_col = totales_columna(df)
        if por_col:
            errores['Columnas'] = por_col
        bor = df.shape
        df = df.drop([bor[0]-1],axis=0)
        
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