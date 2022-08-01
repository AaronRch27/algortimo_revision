# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 14:27:15 2022

@author: AARON.RAMIREZ
"""
from FO import generar_formato

def errores(cuestionario,nombre):
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
    errores, censo = iterar_cuestionario(cuestionario)
    #depurar
    errores = depurar(errores)

    generar_formato(errores, censo, nombre)
    print(errores)
    return errores


def depurar(errores):
    "borrar algunos errores de acuerdo a instrucciones de validacion"
    for pregunta in errores:
        
        if 'borraAr' in errores[pregunta]:
            
            del errores[pregunta]['borraAr']
            for k in errores[pregunta]:
                if type(k) == int:
                    c = 0
                    for error in errores[pregunta][k]:
                        if error == 'Error: Suma de desagregados no coincide con el total':
                            c += 1
                    if c > 0:
                        for vez in range(c):
                            errores[pregunta][k].remove('Error: Suma de desagregados no coincide con el total')
            borrar=[]
            for k in errores[pregunta]: 
                if not errores[pregunta][k]:
                    borrar.append(k)
            for ele in borrar:
                del errores[pregunta][ele]
    
    return errores

def iterar_cuestionario(cuestionario):
    "comprobar errores en cada pregunta"
    errores = {}
    censo = ''
    for llave in cuestionario:
        for pregunta in cuestionario[llave]:
            print('comienzo de errores ', pregunta)
            tablas = cuestionario[llave][pregunta].tablas
            if censo == '':
                conseguir_censo = cuestionario[llave][pregunta].dfraw
                nombres = list(conseguir_censo.columns)
                rem_le = ['0','1','2','3','4','5','6','7','8','9','\n']
                censo = ''.join(cut for cut in nombres[1] if cut not in rem_le)
                if 'Unnamed' in censo:
                    censo = 'Hoja de pruebas'
            for tabla in tablas:
                if type(tablas[tabla]) == str:
                    continue
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
            # print('hasta aquie vba bien ',pregunta)
            try:
                consist = consistencia(cuestionario,cuestionario[llave][pregunta]) 
            except:
                consist = {'Consistencia':['Las instrucciones de consistencia escapan a la capacidad actual de validación']}
            if consist:
                
                if pregunta in errores:
                    try:
                        errores[pregunta].append(consist)
                    except:#si existe eror previo puede que no sea lista sin dict
                        for k in consist:
                            if k in errores[pregunta]:
                                errores[pregunta][k] += consist[k]
                            if k not in errores[pregunta]:
                                errores[pregunta][k] = consist[k]
                if pregunta not in errores:
                    errores[pregunta] = consist
            
    return errores, censo

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
    errores = {}
    #primer paso es filtrado de instrucciones clasificadas
    clasificadas = pregunta.instruccio_clasificadas
    ins_cons = [] #instrucciones de consistencia
    for instruc in clasificadas:
        if clasificadas[instruc] == 'consistencia':
            ins_cons.append(instruc)
            
    if not ins_cons:#en caos de no existir no tiene caso seguir con esta validación
        return
    #segundo paso, otro filtro de instrucciones de comparacion mayor menor o igual

    for instru in ins_cons:
        # print(instru)
        op = 0
        rev = instru.lower()
        if 'igual' in rev:
            op = 1

        if 'menor' in rev:
            op = 2

        if 'mayor' in rev:
            op = 3
  
        if op == 0:
            # errores['Consistencia'] = [f'Instrucción "{instru[:35]}..." no se pudo validar,revisar ']
            pass
        
        if op > 0: 
            comparar = pregunta_comparar(pregunta.nombre,instru)#string con el nombre de la pregunta que se va a comparar

            if comparar == 'misma':#La validacion es con la misma pregunta
                tablas = pregunta.tablas
                for tabla in tablas:
                    relmisma = relaciones_mis(tablas[tabla])
                    if relmisma:
                        if 'Consistencia' in errores:
                            errores['Consistencia'] += relmisma['Consistencia']
                        if 'Consistencia' in errores:
                            errores['Consistencia'] = relmisma['Consistencia']
                        errores['borraAr'] = 1
                        return errores
                    if not relmisma:
                        errores['borraAr'] = 1
                        return errores
        #aquí entonces se van a tomar las tablas de ambas preguntas y se hará un análisis de qué se puede comparar de acuerdo a nombres de columnas y de fila index de pregunta
            pregunta_c = buscar_pregunta(cuestionario,comparar) #objeto pregunta
            if pregunta_c == 'No':#agregar advertencia para errores
                
                if 'Consistencia' in errores:
                    errores['Consistencia'].append('No se pudo comparar con pregunta '+comparar)
                else:
                    errores['Consistencia'] = ['No se pudo comparar con pregunta '+comparar]
            else:#analizar las tablas de cada pregunta 
                #comprobar que solo tienen una tabla
                if len(pregunta_c.tablas) == 1 and len(pregunta.tablas) == 1:
                    tablaA = pregunta.tablas[1]#la numeracion de tablas inicia desde 1
                    tablaC = pregunta_c.tablas[1]
                    compatible = analizarT(tablaA,tablaC)
                    if not compatible:
                        #qui va llamado a funcion para interpretar el texto en el sentido de ver nombres de columnas o numerales según la instrucción
                        compatible = analizar_tex_instr(tablaA,tablaC,instru)
                        if not compatible:
                            if 'Consistencia' in errores:
                                errores['Consistencia'].append('No se pudo comparar con pregunta '+comparar+' por incompatibilidad en tablas')
                                continue
                            else:
                                errores['Consistencia'] = ['No se pudo comparar con pregunta '+comparar+' por incompatibilidad en tablas']
                                continue
                    #de llegar aquí, entonces sí hay compatibilidad
                    # print(compatible)
                    #conseguir los valores de la tabla en pregunta actual
                    valor_conseguir_p_actual = compatible['rel'][0]
                    instruc_ambas = rev.split('igual') #general lista con dos elementos, el priemro refiere a la instruccion de la pregunta actual y el segundo a lo que se busca en la pregunta a comparar   
                    tipo_val_pa = analizarIns(instruc_ambas[0])
                    if pregunta.T_tip == 'index' and 0 in compatible['p_act']:
                        compatible['p_act'].remove(0)
                        
                    pa_val = lista_valores(tablaA,
                                           pregunta.autosuma,
                                           tipo_val_pa,compatible['p_act'],
                                           valor_conseguir_p_actual)
        
                    #para conseguir valores de pregunta a comparar    
                    valor_conseguir_p_comp = compatible['rel'][1]
                    tipo_val_pc = analizarIns(instruc_ambas[1])
                    if pregunta_c.T_tip == 'index' and 0 in compatible['p_comp']:
                        compatible['p_comp'].remove(0)
                    pc_val = lista_valores(tablaC,
                                           pregunta_c.autosuma,
                                           tipo_val_pc,compatible['p_comp'],
                                           valor_conseguir_p_comp)
                    #comparar ambas listas según su operación
                    err = comparacion_consistencia(op,pa_val,pc_val,comparar)
                    if err:
                        if 'Consistencia' in errores:
                            errores['Consistencia'] += err['Consistencia']
                            continue
                        else:
                            errores = err
                            continue
                    
                    #hacer la comparacion entre ambas listas, quiza iterar por cada valor a comparar. La idea es que sean la misma cantidad de ellos. Usar función de NS pero dentro de una nueva función de comparación
                
                #algo distinto para más de una tabla
        
    return errores

def analizar_tex_instr(t1,t2,tx):
    "t1 y 2 son dataframes, tx es string instruccion. Regresa dict con filas o columnas compatibles(su indice)"    
    res = {}
    tx = tx.lower()
    textos = tx.split('igual')
    res['rel'] = [] #forma final ['columna','columna']
    res['p_act'] =[]   #list [0,1,2...] indices de lo que se va a comparar
    res['p_comp'] = [] # list [0,1,2...]
    #textos genera una lista de dos elementos, el primero es referente a pregunta actual y el segundo es referente a la pregunta de comparación
    if 'columna' in textos[0]:
        res['rel'].append('columna')
    st = encontrar_comillas(textos[0])
    #comparar palabra obtenida entre comillas con lista de nombres de columnas pregunta actual
    col = list(t1.columns)
    c = 0
    for co in col: #encontrar la coincidencia con los nombres de columnas
        co = co.lower()
        if st in co:
            res['p_act'].append(c)
            break
        c += 1
    #ahora hacer lo mismo pero para pregunta de comparación
    if not 'columna' in textos[1] and not 'numeral' in textos[1]:
        res['rel'].append('columna')
    st = encontrar_comillas(textos[1])
    col = list(t2.columns)
    c = 0
    for co in col: #encontrar la coincidencia con los nombres de columnas
        co = co.lower()
        if st in co:
            res['p_comp'].append(c)
            break
        c += 1
    
    return res

def encontrar_comillas(texto):
    st = ''
    c = 0
    for letra in texto:
        if letra == '"':
            for le in texto[c+1:]:
                
                if le != '"':
                    st += le
                else:
                    break
            break
        c += 1
    return st

def relaciones_mis(tabla):
    """
    

    Parameters
    ----------
    tabla : dataframe de la tabla.

    Returns
    -------
    errores. dict. Con los errores detectados. Estas relaciones entre
        la misma pregunta siempre son de solo una forma. La suma de los
        desagregados no necesariamente debe ser igual al total, más bien
        ningún desagregado debe ser mayor al total. Eso es lo que
        importa en esta validacion.

    """
    tablac = tabla.copy()
    tablac = tablac.replace({'borra':0})
    errores = {}
    #identificar total
    col = tablac.columns
    ind = 0
    for c in col:
        if c == 'Total':
            break
        ind += 1
    if ind == 0:
        errores['Consistencia'] = ['No se pudo comprar internamente porque no hay columna de Total']
        return errores
    filas = tablac.shape
    for fila in range(filas[0]):
        lista = tablac.iloc[fila-1,ind:]
        total = lista[0]
        for val in lista[1:]:
            if val > total:
                if 'consistencia' in errores:
                    errores['Consistencia'].append(f'Fila {fila}:valores de desagregados no pueden ser mayores que el valor del total')
                if 'consistencia' not in errores:
                    errores['Consistencia'] = [f'Fila {fila}:valores de desagregados no pueden ser mayores que el valor del total']
    return errores

def comparacion_consistencia(operacion,comparador,referente,nombre_ref):
    """
    

    Parameters
    ----------
    operacion : int = 1 igual, 2 menor o igual, 3 mayor o igual
        
    comparador : list. lista de los comparadores
        
    referente : list lista de valores referentes para comparar
    
    nombre_ref : str. nombre de la pregunta con la que se va a comparar 
        la pregunta actual
        

    Returns
    -------
    errores : dict. diccionario con los errores encontrados en la 
        comparacion

    """
    errores = {}
    #primer error comparar que ambas listas sean del mismo tamaño
    if len(comparador) != len(referente):
        errores['Consistencia'] = ['No es posible comparar por error de lectura en tabla']
        return errores
    c = -1
    for comp in comparador:
        c +=1
        ref = referente[c]
        if type(comp) == str or type(ref) == str: #si hay NS o NA
            nsa = NS(comp,ref)
            #convertir a cero para poder hacer comparaciones posteriores
            if type(comp) == str:
                comp = 0
            if type(ref) == str:
                ref = 0
                
            if nsa == 1:
                if 'Consistencia' in errores:
                    errores['Consistencia'].append(f'Inconsistencia detectada con el uso de NA/NS en pregunta {nombre_ref}')
                else:
                    errores['Consistencia'] = [f'Inconsistencia detectada con el uso de NA/NS en pregunta {nombre_ref}']
                    continue
                # return errores
            if nsa  == 0:#quiere decir que es correcto el registro
                continue
        #cualquier comparación se basa en que sean iguales, por eso es lo primero
        if operacion == 1:
            if comp == ref:
                continue
            else:
                if 'Consistencia' in errores:
                    errores['Consistencia'].append(f'El valor {comp} no es igual que pregunta {nombre_ref}')
                else:
                    errores['Consistencia'] = [f'El valor {comp} no es igual que pregunta {nombre_ref}']
                # return errores
        #sino son iguales entonces se hacen las operaciones
        if operacion == 2:
            if comp <= ref:
                continue
            else:
                if 'Consistencia' in errores:
                    errores['Consistencia'].append(f'El valor {comp} no es menor o igual que pregunta {nombre_ref}')
                else:
                    errores['Consistencia'] = [f'El valor {comp} no es menor o igual que pregunta {nombre_ref}']
                # return errores
        if operacion == 3:
            if comp >= ref:
                continue
            else:
                if 'Consistencia' in errores:
                    errores['Consistencia'].append(f'El valor {comp} no es mayor o igual que pregunta {nombre_ref}')
                else:
                    errores['Consistencia'] = [f'El valor {comp} no es mayor o igual que pregunta {nombre_ref}']
                # return errores
        
        
    return errores

def NS(comparador,referente):
    """
    

    Parameters
    ----------
    comparador : str--es el valor de pregunta actual
        el valor detectado en excel, y que tiene dentro ns o na.
    referente : str-- es el valor de pregunta a comparar
        el valor detectado en excel, y que tiene dentro ns o na.

    Returns
    -------
    int
        regresa 1 si es error, 0 si todo en orden.
    
    Nota: No alterar el orden de los condicionales, ya que eso puede 
    generar errores

    """
    n = ['NS','ns']
    a = ['NA','na']
    br = ['borra']
    
    if referente == comparador:
        return 0
    if referente in br and comparador in br:
        return 0
    if referente in a and comparador in a:
        return 0
    if referente in a and comparador not in a:
        return 1
    if referente not in a and comparador in a:
        return 1 #Error discutido con Paulina sobre NA´s 
    if referente in n and comparador in n:
        return 0
    if referente == 0 and comparador in n:
        return 1
    if referente in n and comparador >= 0:
        return 1
    if referente > 0 and comparador in n:
        return 0

def lista_valores(tabla,autosuma,tipo_val,indices,valor_conseguir):
    """
    

    Parameters
    ----------
    tabla: dataframe de la tabla
    autousma: str. Puede ser Si o No, para saber si la tabla tiene autosuma 
        al final de sus columnas.
    valor_conseguir : string. puede ser columna o fila
    indices : lista. Contiene los indices para extraer los valores,
        se toma en cuenta el primero y el último para generar 
        la lista. 
    tipo_val: str. para saber si se busca una autosuma o suma de 
        numeral. 

    Returns
    -------
    lista. list. Lista con los valores que serán comparados

    """
    #nota: siguene pendientes condicionales para otro tipo de busquedas, como las de fila
    if valor_conseguir == 'columna':
                        
        if autosuma == 'Si' and tipo_val == 'autosuma':
            pa_val = list(tabla.iloc[-1,:])
    
        if autosuma == 'No' and tipo_val == 'autosuma':
            pa_val = []
            for col in tabla:
                lista = list(tabla[col])
                nlis = [x for x in lista if type(x) != str] #para quitar registros que no son numeros
                suma = sum(nlis)
                pa_val.append(suma)
        if tipo_val == 'unifila':
            pa_val = list(tabla.iloc[0,:])
        
        if type(tipo_val) == int:
            pa_val = list(tabla.iloc[tipo_val-1,:])
        
        
    
    # if valor_conseguir == 'fila':
        

    if not indices:
        if 'Total' in list(tabla.columns):
            pa_val = list(tabla['Total'])
            return pa_val
        else:
            pa_val = list(tabla.iloc[:,1])  
            return pa_val
    pa_val = pa_val[indices[0]:indices[-1]+1]
    return pa_val
    

def analizarIns(texto):
    "analiza el texto de la instrucción, regresa string de autosuma o int de numeral para hacer la comparación"
    
    if 'numeral' in texto:
        #obtener el numeral o numerales a sumar en la tabla
        if not 'suma' in texto:
            nt = texto.split('numeral')
            nt1 = nt[1].split()
            numeral = int(nt1[0])
        # if 'suma'
        return numeral
    if 'suma' in texto or 'recuadro' in texto:
        
        return'autosuma'    
    
    if 'suma' not in texto and 'numeral' not in texto:
        return 'unifila'

def analizarT(t1,t2):
    "t1 y 2 son dataframes. Regresa dict con filas o columnas compatibles(su indice)"
    filasa = list(t1.iloc[:,0])
    filasc = list(t2.iloc[:,0])
    col_a = list(t1.columns)
    col_c = list(t2.columns)
    #pasarlos a minuscula, quitar saltos de linea y espacios
    borr = ['\n',' ']
    filasa = [''.join(car for car in str(fila) if car not in borr).lower() for fila in filasa]
    filasc = [''.join(car for car in str(fila) if car not in borr).lower() for fila in filasc]
    col_a = [''.join(car for car in str(fila) if car not in borr).lower() for fila in col_a]
    col_c = [''.join(car for car in str(fila) if car not in borr).lower() for fila in col_c]
    # print(filasa,filasc,col_a,col_c)
    medidor = [0,0,0,0] #cada cero pertenece a cada iteracion, el máximo señala cuál es la mejor manera de comparar tablas(filaxfila,filaxcolumna,columnaxfila.columnaxcolumna)
    indices = [[],[],[],[]] #indices de la pregunta a comprarar
    ind_a = [[],[],[],[]] #indices de la pregunta actual
    respuesta = [['fila','fila'],['fila','columna'],['columna','fila'],['columna','columna']]
    c1 = 0     
    for elm in filasc:
        # if elm in filasa:
        #     medidor[0] += 1
        #     indices[0].append(c1)
        #     ind_a[0].append(filasa.index(elm))
        if elm in col_a:
            medidor[2] += 1
            indices[2].append(c1)
            ind_a[2].append(col_a.index(elm))
        c1 += 1
    c1 = 0
    for elm in col_c:
        if elm in filasa:
            medidor[1] += 1
            indices[1].append(c1)
            ind_a[1].append(filasa.index(elm))
        if elm in col_a:
            medidor[3] += 1
            indices[3].append(c1)
            ind_a[3].append(col_a.index(elm))
        c1 += 1

    res = {}
    
    r = max(medidor)
    if r == 0: #por si nada es comparable
        return []
    c = 0 
    for val in medidor:
        if val == r:
            break
        c += 1
    res['rel'] = respuesta[c]
    res['p_act'] = ind_a[c]
    res['p_comp'] = indices[c]
    
    return res

def buscar_pregunta(cuestionario,nombre):
    "Busca la prgeunta por nombre(str) en el cuestionario(dict), regrea objeto pregunta"
    for seccion in cuestionario:
        for pregunta in cuestionario[seccion]:
            if pregunta == nombre:
                return cuestionario[seccion][pregunta]
    return 'No'

def pregunta_comparar(nombre,instruccion):
    """
    

    Parameters
    ----------
    nombre : str, nombre de la pregunta

    Returns
    -------
    str con el nombre de la pregunta a la que se tiene 
    que hacer la comparacion

    """
    borrar = [',', ' ']
    # print(instruccion)
    if 'la pregunta' not in instruccion:#preguntas cuya suma no debe ser necesariamente igual a sus desagregados, sino simplemente el valor decada desgregado no debe ser mayor al del total
        return 'misma' 
    tx = instruccion.split('la pregunta')
    tx1 = tx[1]
    interes = tx1.split()
    pregunta_c = interes[0]
    if 'anterior' in pregunta_c:
        nnn = nombre.split('.')
        resta = int(nnn[1]) - 1
        return f'{nnn[0]}.{resta}'
    else:
        pregunta_c = ''.join(c for c in pregunta_c if c not in borrar)
        return pregunta_c


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
    indices = list(df.iloc[:,0])
    df = df.replace({'borra':0,'NS':0,'NA':0})
    if autosuma == 'Si':#porque aquí también hay tablas con autosuma y esa fila no sirve para esta validacion
        bor = df.shape
        df = df.drop([bor[0]-1],axis=0)
    separar = []
    c = 0
    for columna in df:
        texto = str(columna).replace(' ','')#quitar espacios porque luego no lo escriben igual siempre
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
            #comporbar si hay strings
            for val in fila:
                if type(val) == str:
                    string = 1
                    break
                else:
                    string = 0
      
            if string == 0:#porque aveces solo son filas con texto, normalmente en preguntas unifila
                if fila[0] > 1:
                    if sum(fila[1:]) > 0:
                        if 'catalogo' in errores:
                            errores['catalogo'].append(f'Por respuesta de catálago, la suma de los desagregados no puede ser mayor que cero en fila {c1+1}')
                        if 'catalogo' not in errores:
                            errores['catalogo'] = [f'Por respuesta de catálago, la suma de los desagregados no puede ser mayor que cero en fila {c1+1}']
                if fila[0] == 0 and 'borra' not in indices[c1]:
                    if 'catalogo' in errores:
                        errores['catalogo'].append(f'Faltó contestar pregunta de catálogo en fila {c1+1}')
                    if 'catalogo' not in errores:
                        errores['catalogo'] = [f'Faltó contestar pregunta de catálogo en fila {c1+1}']
                if fila[0] == 1:
                    if fila[1:]:#porque si la fila esta vacia no es un error ya que es la ultima columna y no hay nada con que corroborar
                        if sum(fila[1:]) == 0:
                            if 'catalogo' in errores:
                                errores['catalogo'].append(f'Por respuesta de catálago, se debe reportar algo en los desagregados de fila {c1+1}')
                            if 'catalogo' not in errores:
                                errores['catalogo'] = [f'Por respuesta de catálago, se debe reportar algo en los desagregados de fila {c1+1}']
            if string == 1:
                if fila[0] > 1:
                    if fila[1:]:
                        if 'catalogo' in errores:
                            errores['catalogo'].appenf(f'Por respuesta de catálago, no puede registrar nada en el resto de la fila {c1+1}')
                        if 'catalogo' not in errores:
                            errores['catalogo'] = [f'Por respuesta de catálago, no puede registrar nada en el resto de la fila {c1+1}']
                if fila[0] == 0 and 'borra' not in indices[c1]:
                    if 'catalogo' in errores:
                        errores['catalogo'].append(f'Faltó contestar pregunta de catálogo en fila {c1+1}')
                    if 'catalogo' not in errores:
                        errores['catalogo'] = [f'Faltó contestar pregunta de catálogo en fila {c1+1}']
                    if fila[0] == 1:
                        if not fila[1:]: #porque sino hay más fila, entonces es la última columna y no hay error
                            
                            if 'catalogo' in errores:
                                errores['catalogo'].append(f'Por respuesta de catálago, se debe reportar algo en los desagregados de fila {c1+1}')
                            if 'catalogo' not in errores:
                                errores['catalogo'] = [f'Por respuesta de catálago, se debe reportar algo en los desagregados de fila {c1+1}']
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
        texto = str(columna).replace(' ','')#quitar espacios porque luego no lo escriben igual siempre
        comparar = '1.Sí/2.'
        if comparar in texto:
            del df[columna]
    return df

def totales_columna(df1):
    "leer dataframe de desagregados por columna y regresar error"
    df = df1.fillna('...')
    #quitar columnas que no necesitan esta validacion
    rev = ['ver catálogo', 'ID']
    S = []
    for s in rev:
        for col in list(df.columns):
            if s in col:
                S.append(col)
    for sacar in S:
        del df[sacar]
            
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
            aritme = evaluador_suma(lista,f'columna {col}')
            if aritme:
                if 'aritmetico' in errores:
                    errores['aritmetico'] += aritme
                else:
                    errores['aritmetico'] = aritme
        c += 1
    
    return errores

def totales_fila(df,autosuma):
    "leer dataframe de tablas normales, regresar error"
    errores = {}
    #eliminar autosumas si las hay, y también validar columnas, aunque ten teoría aquí no deberia haber errores por las fórmulas de autosuma:
    if autosuma == 'Si':
        # validar columnas:
        por_col = totales_columna(df.iloc[:,1:])
        if por_col:
            borrar_error = []
            c = 0
            
            for er in por_col['aritmetico']:
                if 'Hay espacios en blanco' in er:#aqui no tiene sentido validar errores de blancos
                    borrar_error.append(c)
                c += 1
            for br in list(reversed(borrar_error)):#borrar los errores de blanco
                por_col['aritmetico'].pop(br)
            if por_col['aritmetico']:
                errores['aritmetico'] = por_col['aritmetico']
                
        bor = df.shape
        df = df.drop([bor[0]-1],axis=0)
        
    total = []
    subtotal = []
    c = 0
    for colum in df:
        if 'Total' in str(colum):
            total.append(c)
        if 'Subtotal' in str(colum):
            subtotal.append(c)
        c += 1
    # print(total,subtotal)
    
    if total and not subtotal:
        c = 0
        for tot in total:
            c1 = 0
            
            for fila in list(df.iloc[:,0]):
                
                try:
                    lista = list(df.iloc[c1, tot:total[c+1]])
                except:
                    lista = list(df.iloc[c1, tot:])
                aritmetic = evaluador_suma(lista,f'fila{c1+1}')
                if aritmetic:
                    if 'aritmetico' in errores:
                        errores['aritmetico']+=aritmetic
                    if 'aritmetico' not in errores:
                        errores['aritmetico'] = aritmetic
                
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
                    aritmetic = evaluador_suma(lista,f'fila{c+1}')
                    
                    if aritmetic:
                        if 'aritmetico' in errores:
                            errores['aritmetico']+=aritmetic
                        if 'aritmetico' not in errores:
                            errores['aritmetico'] = aritmetic
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
                
                aritmetic = evaluador_suma(lista,f'fila{c+1}')
                if aritmetic:
                   
                    if 'aritmetico' in errores:
                        errores['aritmetico']+=aritmetic
                    if 'aritmetico' not in errores:
                        errores['aritmetico'] = aritmetic
            c += 1
        # ahora se revisan los subtotales con sus desagregados
        rsubtotal = subtotal+[]#un respaldo de subtotal por si se necesita después
        subtotal += total #se juntan para validar todo de una vez, cada uno por separado con sus desagregados
        subtotal.sort()
        # print(subtotal)
        c = 0
        for fila in list(df.iloc[:,0]):
            lista_fila = list(df.iloc[c,:])
            c1 = 0
            for sub in subtotal:
                try:
                    lista = lista_fila[sub:subtotal[c1+1]]
                except:#para cuando llegue a la ultima columna de subtotales
                    lista = lista_fila[sub:]
                # print(lista)
                aritmetic = evaluador_suma(lista,f'fila{c+1}')
                if aritmetic:
                    
                    if 'aritmetico' in errores:
                        errores['aritmetico']+=aritmetic
                    if 'aritmetico' not in errores:
                        errores['aritmetico'] = aritmetic
                c1 += 1
            c += 1
        

                    
                    
    return errores

def evaluador_suma(lista,indi):
    """
    

    Parameters
    ----------
    lista : list
        el primer valor de la lista debe ser el total y los demás
        sus desagregados, los cuales deben ser al menos dos, de 
        ser menos no hará la comprobación.
    indi : str or int
        es la fila o columna que se anda comparando
    Returns
    -------
     lista de errores

    """
    if len(lista) < 3:#posteriormente entará otra comprobación aquí
        return 
    else:
        errores = []
        total = lista[0]
        convertir = ['NS','NA','na','ns','Na','Ns','nA','nS','X','x']
        na = 'No'
        ns = 'No'
        x = 'No'
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
                if valor.lower() == 'x':
                    x = 'Si'
                comprobar = 'Si'
                desagregados[c] = 0
            if type(valor) == str and valor not in convertir:
                # print(valor)
                desagregados[c] = 0
                if valor != 'borra':
                    errores.append(f'Error: valor no permitido en {indi}')
            c += 1
        suma = sum(desagregados)
        if blanco > 0:
            if total == 'borra':
                blanco += 1
                if len(lista) == blanco:
                    
                    return
                else:
                    errores.append(f'{indi} Hay espacios en blanco')
                    return errores
            if total != 'borra':
                errores.append(f'{indi} Hay espacios en blanco')
                return errores
        if total == 0:
            if ns == 'Si':
                errores.append(f'{indi} Si el total es cero, valores de desagregados no pueden ser NS o mayores a cero')
                return errores
        if total in convertir and suma > 0:
            errores.append(f'Error: Suma de desagregados no puede ser mayor a cero si total es NS o NA en {indi}')
            return errores
        if total in convertir and suma == 0:
            if total.lower() == 'na' and ns == 'Si':
                errores.append(f'Error: Si el total es NA ninguno de sus desagregados puede ser NS para {indi}')
        if type(total) == str and total not in convertir:
            errores.append(f'Error: el total es un valor no permitido como respuesta en {indi}')
            return errores
        if type(total) != str:
            if total != suma:
                if total >= 0 and comprobar == 'No' and suma > 0:
                    print(total,suma,'okssksks')
                    errores.append(f'Error: Suma de desagregados no coincide con el total en {indi}')
                if total == 0 and ns == 'Si':
                    errores.append(f'Si el total es cero, ningún desagregado puede ser NS en {indi}')
            
        return errores
    
    return