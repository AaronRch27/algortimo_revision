# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 14:27:15 2022

@author: AARON.RAMIREZ
"""
from FO import generar_formato
import pandas as pd

def errores(cuestionario,nombre,indica):
    """
    

    Parameters
    ----------
    cuestionario : Dic
        Cuestionario es lo que se genera luego de convertir todo el 
        documento de excel a dataframes y sus propiedades. Contiene 
        entonces llaves para cada pestaña del documento con preguntas
        validables, y en cada llave hay otras llaves, una por pregunta.
    indica : dataframe generado con las validaciones que se van a
        aplicar a todas las preguntas del cuestionario
    Returns
    -------
    Regresa una lista con los errores detectados en tres áreas: 
        errores aritméticos, errores de omision de especifique y
        erores de relaciones entre preguntas; unicamente comparaciones
        de menores, mayores o iguales.
        
    Eventualmente, regresará el formato de observaciones con una fila por
    error detectado

    """
    errores, censo = iterar_cuestionario(cuestionario, indica)
    #dado que se harán validaciones respecto a indica, no hace falta depurar errores
    #depurar
    # errores = depurar(errores)
    nombre = nombre.split('/')
    nombre = nombre[-1]
    generar_formato(errores, censo, nombre)
    # print(errores)
    return errores


def depurar(errores):
    "borrar algunos errores de acuerdo a instrucciones de validacion"
    for pregunta in errores:
        
        if 'borraAr' in errores[pregunta]:
            
            del errores[pregunta]['borraAr']
            for k in errores[pregunta]:
                if type(k) == int or k == 'aritmetico':
                    
                    er = []
                    c = 0
                    for error in errores[pregunta][k]:
                        if 'Error: Suma de desagregados no coincide con el total' in error:
                            er.append(c)
                        c += 1
                    if er:
                        
                        for vez in reversed(er):
                            errores[pregunta][k].pop(vez)
            borrar=[]
            for k in errores[pregunta]: 
                if not errores[pregunta][k]:
                    borrar.append(k)
            for ele in borrar:
                del errores[pregunta][ele]
    
    return errores

def iterar_cuestionario(cuestionario,base):
    "comprobar errores en cada pregunta"
    p = [l[:-2] for l in list(base['preguntas'])]
    base['preguntas'] = p
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
            fila_indicador = 0
            for indic in p:
                if indic == pregunta:
                    break
                fila_indicador += 1 
            validaciones = base.loc[fila_indicador,:]#para multiples tablas seguramente se hará dentro de la iteracion por tabla
            
            for tabla in tablas:
                if type(tablas[tabla]) == str:
                    continue
                #Lo primero es ver si la tabla debe ser saltada, por alguna relación con preguntas anteriores
                # if validaciones['salto_preguntas']:
                #     #aun pendiente por cóom ejecutar esta validación
                #     print('debe saltar')#solo un indicador, borrar después
                    
                    #aquí alguna funcion para verificar esos saltos de preguntas  y comprobación en blanco
            #     #comprobar si la tabla está toda en blanco
            #     t1 = tabla_vacia(tablas[tabla])
            #     if not t1:#si está vacía la salta
            #         continue
                if validaciones['aritmetico']=='1' or validaciones['aritmetico']==1:  
                    
                    df = tablas[tabla].copy()#con copia para no afectar el frame original
                    ndf = quitar_sinonosabe(df)
                    #aunque ya se indicó, se hace evaluacion adicional para validar totales de forma aritmética
                    aritme1, ntab = exam_aritme(ndf,cuestionario[llave][pregunta]) #corroborar si vale el esfuezro hacer validacion aritmetica--regresa sí o no como priemra vcariable y si es sí, segunda es el DF ya recortado con puntos de interés, sino solo es una variable vacía que no se usará
                    aritme1 = 'Si' #no hay forma de que sea no, si se ha indicado que se requiere esta validación
                    if aritme1 == 'Si':
                        if cuestionario[llave][pregunta].tipo_T == 'Tabla':
                            aritmeticos = totales_fila(ntab,cuestionario[llave][pregunta].autosuma)
                            if aritmeticos:
                                errores[pregunta] = aritmeticos
                        if cuestionario[llave][pregunta].tipo_T == 'NT_Desagregados':
                            aritmeticos = totales_columna(ndf)#queda ndf porque ntab es solo para las tablas normales
                            if aritmeticos:
                                errores[pregunta] = aritmeticos
                        if cuestionario[llave][pregunta].tipo_T == 'Tabla_delitos':
                            aritmeticos = val_delitos(ntab,cuestionario[llave][pregunta],tabla)
                            if aritmeticos:
                                errores[pregunta] = aritmeticos
                if validaciones['blanco']=='1' or validaciones['blanco']==1:
                #ver si hay espacios en blanco y tomar en cuenta excepciones sinonosabe, Usos de X en no aplica etc
                #validación para todas las preguntas de si no no se sabe.
                #hacer una para blancos exclusivamente
                #integrar validacion de No aplica con X--- se supne que ya---probar
                    otra_copia = tablas[tabla].copy()
                    sinon = sinonosabe(otra_copia,
                                       cuestionario[llave][pregunta].autosuma,
                                       cuestionario[llave][pregunta].tipo_T)
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
                        
                #resto de validaciones pendientes:
                if validaciones['suma_numeral']=='1' or validaciones['suma_numeral']==1:
                    
                    sumas = suma_numeral(tablas[tabla],validaciones['s_num_lis'])
                    if sumas:
                        if pregunta in errores:
                            if 'aritmetico' in errores[pregunta]:
                                for error in sumas:
                                    errores[pregunta]['aritmetico']+=sumas[error]
                            if 'aritmetico' not in errores[pregunta]:
                                errores[pregunta] = sumas
                        if pregunta not in errores:
                            errores[pregunta] = sumas
                    # print(errores,sumas)
                # if validaciones['espeficique']:
                #     espec = especifique(cuestionario[llave][pregunta])
                    
                # if validaciones['errores_registro']:#esta validacion no se desarrollará ya que existe en aritmético, y esto es más eficiente así ya que hay columnas fuera de validaciones aritmética que aceptan otro valores y en ellas no conviene esto.
                    
                if validaciones['preguntas_relacionadas']=='1' or validaciones['preguntas_relacionadas']==1:
                    #a continuacion, se buscan los errores por instrucciones de preguntas --hasta ahora solo de relaciones entre preguntas(consistencia)
                    datos = eval(validaciones['preg_rel'])#arreglar un poco/pasar a formato de diccionario porque está en string todo
                    consist = consistencia(cuestionario,
                                           cuestionario[llave][pregunta],
                                           datos)  
                    # print(consist)
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
   
def suma_numeral(tabla,listadlistas):
    "Validacion de sumas por columna para numerales de tabla,con lista de listas de los que deben ser sumados"
    
    listadlistas = eval(listadlistas)
    errores = {}
    for lista in listadlistas:
        #cada lista tendrá valor de inicio y de término nada más, es decir, dos elementos. 
        #la comprobación de longitudes de tabla y elementos de lista debe hacerse en generar base
        indices = [ lista[0]+x-1 for x in range(1,lista[1])]
        indices.append(lista[0]-1)#para que primer valor sea el ultimo y se tome como autosuma
        to_val = tabla.iloc[indices,1:]#del uno para la derecha con el fin de evitar columna de indices de tabla
        ercol = totales_columna(to_val) 
        # print(ercol)
        if ercol:
            if 'aritmetico' in errores:
                errores['aritmetico']+=ercol['aritmetico']
            if 'aritmetico' not in errores:
                errores['aritmetico'] = ercol['aritmetico']
       
    return errores
    


def val_delitos(df,context,ntabla):
    """
    

    Parameters
    ----------
    df : dataframe de la pregunta ya sin los catálogos sinonosabe y
        también con el filtro de si hay algo más en la prgeunta que
        no deba ser validado con el total
    context : objeto pregunta para tener en cuenta el
        contexto de la tabla
    ntabla: index de la tabla para buscarla en el context

    Returns
    -------
    errores: dict. Diccionario con errores detectados

    """
    errores = {}
    #validar fila por fila#######################
    total = []
    subtotal = []
    c = 0
    for colum in df:
        if 'Total' in str(colum):
            total.append(c)
        if 'Subtotal' in str(colum):
            subtotal.append(c)
        c += 1
    # print(total,subtotal,df.shape)
    
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
        c = 0
        for tota in total:
            try: #esto es para cuando hay más de un total y alguno de ellos u otro tiene desagregados
                if subtotal[0] > total[c+1]:
                    limites.append(total[c+1])
                    c += 1
                    continue
            except:
                pass
            for sub in subtotal:
                if sub > tota:
                    limites.append(sub) #límites tendrá un numero por cada elemento mayor a cada total detectado
                    break
            c += 1
                
        c = 0
        for limite in limites:#generar listas con columnas intermedias entre un total y su primer subtotal
            if limite-total[c]>0:
                lista_columnas =[i for i in range(total[c]+1,limite)]#el mas uno es porque necesitamos saber la columna a partir del total
            else:
                lista_columnas =[i for i in range(total[c],limite)]
            desagre_totales.append(lista_columnas)
            c += 1
        # print(limites,desagre_totales,total, subtotal)
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
            c1 = 0
            for tot in total:
                lista = [lista_fila[tot]]
                for sub in subtotal:
                    try: #para atender casos donde hay varios totales pero algunos no tienen subtotales
                        if sub > tot and sub < total[c1+1]:
                            lista.append(lista_fila[sub])
                    except:
                        if sub > tot:
                            lista.append(lista_fila[sub])
                # print(lista)
                aritmetic = evaluador_suma(lista,f'fila{c+1}')
                if aritmetic:
                   
                    if 'aritmetico' in errores:
                        errores['aritmetico']+=aritmetic
                    if 'aritmetico' not in errores:
                        errores['aritmetico'] = aritmetic
                c1 += 1
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
    #validar columna por columna##############
    
    co_des = [] #codigos de desagregados, esos hay que sacarlos antes de enviar a la funcion
    for k in context.tablas: #solo paradar el valor a k, que es cero o uno dependiendo las tablas que tenga, interesa la primera tabla unicamente para linea siguiente
        break
    lista = list(context.tablas[k]['Código']) #Toda tabla de delitos tiene columna llamada así
    c = 0
    for cod in lista:
        if len(cod) > 5:
            co_des.append(c)
        c += 1
    ndf = df.copy()
    ndf = ndf.drop(co_des)
    nombres = list(df.columns)
    borrar = ['Bien jurídico',
              'Código',
              'Tipo de delito']
    for bor in borrar:
        for nombre in nombres:
            if bor in nombre:
                ndf = ndf.drop([nombre],axis=1)
    ndf = ndf.reset_index(drop=True)
    # print(nombres,borrar)
    ercol = totales_columna(ndf)
    if ercol:
        if 'aritmetico' in errores:
            errores['aritmetico']+=ercol['aritmetico']
        if 'aritmetico' not in errores:
            errores['aritmetico'] = ercol['aritmetico']
        # print(errores)
    #validar desagregado por desagregado(columa por columna)#####
    ldelistas_co = {}#diccionario que contiene llaves codigo y contenido de cada llave es una lista con el indice de los codigos desagregados
    c = 0
    for codigo in lista:#variable lista definida en proceso anterior que contiene los codigos de la tabla
        app = []
        if codigo != lista[-1]:#condicional para no generar errores al llegar al último codigo de la lista
            d = 1
            for cod in lista[c+1:]:
                if codigo in cod:
                    app.append(c+d)
                if codigo not in cod:
                    break
                d += 1
        if app:
            ldelistas_co[codigo] = app #genera llave con lista de indices que le perrtenecen al código
        c += 1
    
    for codigo in ldelistas_co:
        #por cada llave con desagregados se hará un dataframe para enviarlo a validar por columna
        ndf = df.iloc[ldelistas_co[codigo]+[ldelistas_co[codigo][0]-1],:]
        nombres = list(df.columns)
        borrar = ['Bien jurídico',
                  'Código',
                  'Tipo de delito']
        for bor in borrar:
            for nombre in nombres:
                if bor in nombre:
                    ndf = ndf.drop([nombre],axis=1)
        ndf = ndf.reset_index(drop=True)#el último valor de ndf es el total del codigo sin desagregados, simulado como si éste fuera una autosuma, para enviarlo a la funcion de validar columnas
        ercol = totales_columna(ndf)
        # print(ercol)
        if ercol:
            R = []
            for err in ercol['aritmetico']:#esto para agregar el codigo donde se encontró el error
                R.append(codigo+':'+err)
            if 'aritmetico' in errores:
                errores['aritmetico']+=R
            if 'aritmetico' not in errores:
                errores['aritmetico'] = R    
        
        ##revisar el tema del 25% de los delitos registrados en otro tipo
        detc = []
        for col in ndf:
            lista = list(ndf[col])
            to = lista[-1]
            com = lista[-3]#este siempre es el indicedel valor otros delitos
            if type(to) == str or type(com) == str:
                div = 0
            else:
                try:#por division entre cero
                    div = com/to
                except:
                    div = 0
            if div >= 0.25:
                detc.append(codigo+' : ' +col)
        if detc:
            if 'numerales y columnas  donde otros delitos son mayores a 25%' in errores:
                errores['numerales y columnas  donde otros delitos son mayores a 25%']+=detc
            if 'numerales y columnas  donde otros delitos son mayores a 25%' not in errores:
                errores['numerales y columnas  donde otros delitos son mayores a 25%'] = detc
    # print(errores)
    #como último paso, corroborar si es una tabla de tipo de víctimas, para hacer comprobación de escritura de valores en donde no deben ir
    nombres = ['Hombres',
     'Mujeres',
     'No identificada',
     'Sector público',
     'Sector privado',
     'No identificada',
     'Sociedad',
     'Estado',
     'Otro',
     'No identificada']
    n_tabl = list(df.columns)
    contador = 0
    for nombre in nombres:
        for tn in n_tabl:
            if nombre in tn: #doble iteración para tener mayor precisión al comparar
                contador += 1
                break
    if contador > 5:#es porque se trata de la tabla buscada
        referente = pd.read_csv('Recursos/tipo_victima.csv')
        nfr = context.tablas[ntabla].copy()
        nfr_n = list(nfr.columns)
        borr = ['Bien jurídico', 'Tipo de delito', 'Total']
        for bo in borr:#para borrar esos nombres de la lista y posteriormente usarla para filtrar el dataframe
            for val in nfr_n:
                if bo in val:
                    nfr_n.remove(val)
        nfr = nfr[nfr_n]
        nlre = list(referente.columns)
        er_col = {}
        c = 1
        for col in list(nfr.columns)[1:]:
            fila = 0
            er_nc = []
            for val in nfr[col]:
                if fila == 164:
                    break
                if referente[nlre[c]][fila] == 1:
                    if type(val) == int:
                        if val < 0:
                          
                            er_nc.append(referente['codigo'][fila])
                    if type(val) == str:
                        if val != 'NS':
                            
                            er_nc.append(referente['codigo'][fila])
                if referente[nlre[c]][fila] == 0:
                    if type(val) == int:
                        if val > 0:
                            
                            er_nc.append(referente['codigo'][fila])
                    if type(val) ==str:
                        if val !='0': #aquí se agregaría el NA si aplica
                            
                            er_nc.append(referente['codigo'][fila])
                fila += 1
            if er_nc:
                er_col[col] = er_nc
            c += 1
        if er_col:
            errores['registro'] = er_col
        
    return errores

def exam_aritme(df,context):
    """
    

    Parameters
    ----------
    df : dataframe de la pregunta ya sin los catálogos sinonosabe
    context : objeto pregunta para tener en cuenta el
        contexto de la tabla

    Returns
    -------
    es : bool Si o No para ver si se hace la validacion aritmetica
    dff : dataframe con lo que debe entrar a esa comparación
        manteniendo una columna de index si fuera el caso de 
        tablas de más de una fila.
        dff también puede regresar un cero si variable "es" 
        vale No.

    """
    # print(df.shape,'exa in')
    es = 'No'
    ddf = 0 #valores predefinidos para ambas variables. Con ello al retornar así, no se hará validacion aritmética
    columnas = list(df.columns)
    if 'Total' not in columnas:
        return es , ddf
    es = 'Si'
    try:#porque aveces no tiene esta característica 
        enc = context.encabezado_tabla#es un dataframe
    except:
        return es, df #no le hace nada al df
    #en caso de que sí hay encabezado, revisar porque hay tablas que no se puede validar el total con todas las columnas, ya que meten otras al final que no son parte de la suma
    cole = []#lista con los primeros valores por columna de encabezados de tabla
    for col in enc:
        for fil in reversed(list(enc[col])):
            if fil != 'borra':
                cole.append(fil)
                break
           
    conteo_rep = dict(zip(cole,map(lambda x: cole.count(x),cole)))#diccionario con conteo de los nombres repetidos
    valores_col = []
    for col in enc:
        lista = list(enc[col])
        if len(lista)==1:#si solo tiene una fila de encabezado no tiene caso
            return es, df
        v_col = 1
        v_col1= 0
        for valor in lista:
            if valor != 'borra':
                v_col1 = v_col
            v_col += 1
        valores_col.append(v_col1)
    # print('####',valores_col)
    #el primer valor de valores_col será el del index de la tabla
    c = 1
    ddf = df.copy()
    # print('aqui',len(columnas),len(cole))
    for ref in valores_col[1:]:
        if ref == 0:
            continue#son columnas vacias, eesas deben ser ignorads
        if ref == 1:

            if conteo_rep[cole[c]] == 1:#esta confirmación es para evitar borrar columnas de tablas por partes que son unidas, donde se repite el nombre del índice   
                try:    
                    ddf = ddf.drop([cole[c]],axis=1)
                except:#porque aveces hay columnas de sinonosabe que ya se removieron
                    pass
            if conteo_rep[cole[c]] > 1:#borrar duplicados de index que no deberían estar por error de lectura de tabla
                columnas = list(ddf.columns)
                if cole[c] in columnas:
                    f = '1'#este uno es porque al transformar la tabla, a columnas repetidas se les va agregando el uno para que no se sobrescriban pudiendo quedar por ejemplo "Subtotal111"
                    lf = []
                    for v in range(6):
                        lf.append(f)
                        f += '1'
                    ch = [str(cole[c])+x for x in lf]
                    borr = [x for x in columnas if x in ch]
                    for val in borr:
                        ddf = ddf.drop([val],axis=1)
                        
                    
        c += 1
    # print(ddf.shape,'exaout')
    return es , ddf

def tabla_vacia(df):
    med = df.shape
    cols = list(df.columns)
    if med[0]>1000:
        cortado = df.iloc[:-1,1:]
    if med[0]<1000:
        cortado = df.iloc[:,1:]
    if 'Tipo de delito' in cols:
        cortado = df.iloc[:-1,3:]
    vacios = cortado.isin(['borra','borra borra'])
    falsos = vacios.isin([False]).any().any()
    if falsos:
        return 'no vacio'
    else:
        print('pregunta con tabla vacia')
        return
    
def consistencia(cuestionario,pregunta,datos):
    """
    

    Parameters
    ----------
    cuestionario : Dict. Es el cuestionario generado luego de transofrmacion
        Se requiere todo para poder navegar entre las distintas preguntas
        para poder comparar relaciones entre ellas.
    pregunta : objeto pregunta
        La pregunta del cuestionario que será comparada con alguna otra.
    datos : list. Es una lista que contiene un diccionario por comparación
        ya sean instrucciones u comparaciones manuales. Los diccionarios
        contienen todas las variables necesarias para hacer la extracción
        de los datos en tablas, y compararlos directamente.El o los
        diccionarios están integrados de la siguiente manera:
            {'pregunta_ref': '1.5.-', 'operacion': 2, 'filas_act': ['2'], 'columnas_act': ['1,2,3'], 'suma_numeral_act': [], 'filas_ref': ['4,5'], 'columnas_ref': ['2,3,4'], 'suma_numeral_ref': ['4', '5']}
            Los datos que contiene cada llave solo son para ejemplificar
    Returns
    -------
    errores. Dict. Regresa un diccionario con errores encontrados en la
        comparación de la pregunta.

    """
    errores = {}
    #iterar por cada comparacion(diccionario en datos)
    for comparacion in datos:
        # if comparacion['pregunta_ref'][0].isdigit():
        #     comparacion['pregunta_ref'] += '.-'
        # print(comparacion)  #excelente para el debug
        for k in comparacion:
            if type(comparacion[k])==list:
                
                if comparacion[k]:
                    sep = comparacion[k][0].split(',')
                    if sep[0] != 'todas' and sep[0] != 'C':
                        comparacion[k]=[int(x) for x in sep]

        if comparacion['pregunta_ref'] == 'misma':#La validacion es con la misma pregunta
            tablas = pregunta.tablas
            
            for tabla in tablas:
                relmisma = relaciones_mis(tablas[tabla])
                if relmisma:
                    if 'Consistencia' in errores:
                        errores['Consistencia'] += relmisma['Consistencia']
                    if 'Consistencia' in errores:
                        errores['Consistencia'] = relmisma['Consistencia']
                    errores['borraAr'] = 1
                    
                if not relmisma:
                    
                    errores['borraAr'] = 1
            continue                    
    #aquí entonces se van a tomar las tablas de ambas preguntas y se hará un análisis de qué se puede comparar de acuerdo a nombres de columnas y de fila index de pregunta
        pregunta_c = buscar_pregunta(cuestionario,comparacion['pregunta_ref']) #objeto pregunta
        
        if pregunta_c == 'No':#agregar advertencia para errores

            if 'Consistencia' in errores:
                errores['Consistencia'].append('No se pudo comparar con pregunta '+comparacion['pregunta_ref'])
            else:
                errores['Consistencia'] = ['No se pudo comparar con pregunta '+comparacion['pregunta_ref']]
        else:#analizar las tablas de cada pregunta 
            
            tablaA = pregunta.tablas[1]#la numeracion de tablas inicia desde 1
            tablaC = pregunta_c.tablas[1]
            #conseguir los valores de la tabla en pregunta actual
            #pa val y pc val son listas de listas
            pa_val = extraer_lista(tablaA,
                                   comparacion['filas_act'],
                                   comparacion['columnas_act'],
                                   comparacion['suma_numeral_act'],
                                   pregunta.tipo_T)

            #para conseguir valores de pregunta a comparar    

            pc_val = extraer_lista(tablaC,
                                   comparacion['filas_ref'],
                                   comparacion['columnas_ref'],
                                   comparacion['suma_numeral_ref'],
                                   pregunta_c.tipo_T)
            #comparar ambas listas según su operación
            # print(pa_val,pc_val)
            c = 0
            for lista in pa_val:
                
                err = comparacion_consistencia(comparacion['operacion'],
                                               lista,
                                               pc_val[c],
                                               comparacion['pregunta_ref'])
                if err:
                    if 'Consistencia' in errores:
                        errores['Consistencia'] += err['Consistencia']
                    else:
                        errores = err
                c += 1
 
        
    return errores

def extraer_lista(tabla,filas,columnas,suma,tipotabla):
    "funcion que extrae una lista de una tabla de acuerdo a las filas y columnas especificadas, así como si hay que sumar algunas filas"
    lista = []
    #filas, columnas y suma son listas y hacen referencia a index pero hay que restarles 1 debido a que su numeración por instrucciones inicia en 1 y no de cero como es el conteo en python
    if type(filas[0]) != str:#para descartar que sean todas las filas de una o unas columas
        filasN = [x-1 for x in filas]
    if type(filas[0])==str:
        if filas[0].lower()=='todas':
            filasN = 'todas'
    
    if type(columnas[0]) != str:#para descartar que sean todas las filas de una o unas columas
        columnasN = [x-1 for x in columnas]
    if type(columnas[0])==str:
        if columnas[0].lower()=='todas':
            columnasN = [x for x in range(tabla.shape[1])]

    #si es no tabla no hay sumas y necesita tratamiento especial
    if tipotabla == 'NT_Desagregados':
        lista = []
        if type(filasN)==str:
            for colum in columnasN:#dificlmente se usaráel else de esta condicional
                l = list(tabla.iloc[:,colum])
                l = [l[-1]]+l#pasar el último al principio
                l.pop()
                lista.append(l)
        else:
            for fila in filasN:
                lista.append(list(tabla.iloc[fila,columnasN]))
        
        return lista
    #comprobar si hay algo que se deba sumar
    if suma:
        
        if suma[0] != 'C': #se trata de sumas de filas
            inicio = suma[0]-1
            fin = suma[1] #a este no se le quita uno porque como se va a un range, en realidad se toma el penultimo valor entonces ahí se hace la resta automáticamente. Ejemplo, si es 8, llegaría hasta el 7 la iteracion
            ldl = []
            res_s = []
            for i in range(inicio,fin):
                lis = list(tabla.iloc[i,columnasN])
                ldl.append(lis)
            c = 0
            for val in ldl[0]:#por valor en la primera lista
                agregar = val
                na = 0
                ns = 0
                if type(val) == str:#por si son na o ns
                    vv = val.lower()
                    if vv=='na':
                        na = 1
                    if vv=='ns':
                        ns = 1
                    agregar = 0
                for lis in ldl[1:]:#iterar resto de listas para sacar sus valores respectivos y sumarlos
                    if type(lis[c])==str:
                        vv = lis.lower()
                        if vv=='na':
                            na = 1
                        if vv=='ns':
                            ns = 1 
                    else:#es int o float
                        agregar += lis[c]
                if agregar == 0 and na > 0:
                    res_s.append('NA')
                if agregar == 0 and ns > 0:
                    res_s.append('NS')
                if agregar >= 0 and na == 0 and ns == 0:
                    res_s.append(agregar)
                c += 1
            lista.append(res_s)
            # print(lista,ldl)
            
        else:#para sumas de columnas
            res_s = []
            if type(filasN) == str:
                filasN = [x for x in range(tabla.shape[0])]
            for fila in filasN:
                lis = list(tabla.iloc[fila,columnasN])
                try:#si son ppuros numeros es sum directa
                    agregar = sum(lis)
                    res_s.append(agregar)
                except:# si hay string hay que comprobar ns y na
                    agregar = 0
                    for val in lis:
                        na = 0
                        ns = 0
                        if type(val) == str:#por si son na o ns
                            vv = val.lower()
                            if vv=='na':
                                na = 1
                            if vv=='ns':
                                ns = 1
                        else:
                            agregar += val
                            
                    if agregar == 0 and na > 0:
                        res_s.append('NA')
                    if agregar == 0 and ns > 0:
                        res_s.append('NS')
                    if agregar >= 0 and na==0 and ns==0:
                        res_s.append(agregar)

                lista.append(res_s)
    
    else:
        if type(filasN)==str:
            for colum in columnasN:
                lista.append(list(tabla.iloc[:,colum]))
        else:
            for fila in filasN:
                lista.append(list(tabla.iloc[fila,columnasN]))
           
    return lista

def analizar_tex_instr(t1,t2,tx,encabezadoA,encabezadoC):
    "t1 y 2 son dataframes, tx es string instruccion. Regresa dict con filas o columnas compatibles(su indice)"    
    res = {}
    tx = tx.lower()
    textos = tx.split('igual')
    res['rel'] = ['columna','columna'] #forma final ['columna','columna']
    res['p_act'] =[]   #list [0,1,2...] indices de lo que se va a comparar
    res['p_comp'] = [] # list [0,1,2...]
    #textos genera una lista de dos elementos, el primero es referente a pregunta actual y el segundo es referente a la pregunta de comparación
    # if 'columna' in textos[0]: # se comenta esta parte porque se dará como predeterminado columna para pregunta actual
    #     res['rel'].append('columna')
    if 'numeral' in textos[0] and not 'columna' in textos[0]:
        res['rel'][0] = 'fila'
    if 'numeral' in textos[1] and not 'columna' in textos[1]:
        res['rel'][1] = 'fila'
        
    st, v = encontrar_comillas(textos[0])
    # print(st,v)
    if v:
        c = 0
        for col in encabezadoA:
            encabezadoA = encabezadoA.fillna('borra')
            lista = list(encabezadoA[col])
            borras = []
            for val in lista:
                if v in val.lower():
                    res['p_act'].append(c)
                if val == 'borra':
                    borras.append(1)
            if len(borras) == len(lista):
                c -= 1 #esa columna no cuenta, y para no borrarla, solo se le resta uno al contador
            c += 1

    #comparar palabra obtenida entre comillas con lista de nombres de columnas pregunta actual
    if not v:
        col = list(t1.columns)
        c = 0
        for co in col: #encontrar la coincidencia con los nombres de columnas
            co = co.lower()
            if st in co:
                res['p_act'].append(c)
                break
            c += 1
    #ahora hacer lo mismo pero para pregunta de comparación
    # print(tx)
    if 'numeral' in textos[1]:
        rt = textos[1].split('numeral')
        numeral = rt[1][:3]
        numeral = ''.join(c for c in numeral if c != ' ')
        # res['rel'].append('fila')
        if len(list(t2.iloc[:,0])) == 1: #tablas de fila unica que son derivadas de preguntas que no son tablas
            #comprobar en columnas
            cols = list(t2.columns)
            # res['rel'].append('columna')
            c = 0
            for val in cols:
                if numeral in val:
                    res['p_comp'].append(c)
                c += 1
            return res
        
    # if not 'numeral' in textos[1]:
        # res['rel'].append('columna')
    st, v = encontrar_comillas(textos[1])
    # print(st,v)
    if v:
        # print('aja',v)
        c = 0
        for col in encabezadoC:
            encabezadoC = encabezadoC.fillna('borra')
            lista = list(encabezadoC[col])
            borras = []
            # print(lista,v)
            for val in lista:
                
                if v in val.lower():
                    res['p_comp'].append(c)
                if val == 'borra':
                    borras.append(1)
            if len(borras) == len(lista):
                c -= 1 #esa columna no cuenta, y para no borrarla, solo se le resta uno al contador
            c += 1
    if not v:
        col = list(t2.columns)
        c = 0
        for co in col: #encontrar la coincidencia con los nombres de columnas
            co = co.lower()
            if st in co:
                res['p_comp'].append(c)
                break
            c += 1
    #comprobar si hay desagregados para añadirlos a los indices
    if 'su desagregación' in tx:
        aver = analizarT(t1, t2,encabezadoA,encabezadoC)
        if not aver:
            return res
        
        if res['p_act']:
            partida = res['p_act'][0]
            for val in aver['p_act']:
                if val > partida:
                    res['p_act'].append(val)
        if res['p_comp']:
            partida = res['p_comp'][0]
            for val in aver['p_comp']:
                if val > partida:
                    res['p_comp'].append(val)
    return res

def encontrar_comillas(texto):

    st = ''
    stl = ''
    c = 0
    for letra in texto:
        if letra == '"':
            for le in texto[c+1:]:
                
                if le != '"':
                    st += le
                    c += 1
                else:
                    break
            break
        c += 1
    # print(texto[c+2:])
    for letra in texto[c+2:]:
        
        if letra == '"':
            for le in texto[c+3:]:
                
                if le != '"':
                    stl += le
                else:
                    break
            break
        c += 1
    
    return st, stl

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
    errores = {}
    if tablac.shape[0] > 1: #para tablas que no son unifila
        tablac = tablac.replace({'borra':0,'NA':0,'NS':0})
        #identificar total
        col = tablac.columns
        ind = 0
        for c in col:
            
            if c == 'Total':
                break
            if c == 'Computadoras': #se agrega esta para tablas con  comparacion en computadoras
                break
            ind += 1
        if ind == 0:
            errores['Consistencia'] = ['No se pudo comprar internamente porque no hay columna de Total']
            return errores
        
        filas = tablac.shape
        for fila in range(filas[0]):
            lista = list(tablac.iloc[fila-1,ind:])
            total = lista[0]
            for val in lista[1:]:
                if val > total:
                    if 'consistencia' in errores:
                        errores['Consistencia'].append(f'Fila {fila}:valores de desagregados no pueden ser mayores que el valor del total')
                    if 'consistencia' not in errores:
                        errores['Consistencia'] = [f'Fila {fila}:valores de desagregados no pueden ser mayores que el valor del total']
    if tablac.shape[0] == 1: #suelen ser tablas NT  sin desagregados
        primero = list(tablac.iloc[:,0])
        for col in tablac.iloc[:,1:]:
            if tablac[col][0] > primero[0]:
                if 'consistencia' in errores:
                    errores['Consistencia'].append(f'{col}:valores no pueden ser mayores que el valor de {tablac.columns[0]}')
                if 'consistencia' not in errores:
                    errores['Consistencia'] = [f'{col}:valores  no pueden ser mayores que el valor de {tablac.columns[0]}']                
        
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
    # print(comparador,referente)
    #primer error comparar que ambas listas sean del mismo tamaño
    if len(comparador) != len(referente):
        if len(comparador) > len(referente):
            ncomp = []
            c = -1 #para tomar los últimosvalores de la lista que generalmente son los totales
            for va in referente:
                ncomp.append(comparador[c])
                c -= 1
            comparador = ncomp
        if len(comparador) < len(referente):
            nref = []
            c = -1 #para tomar los últimosvalores de la lista que generalmente son los totales
            for va in comparador:
                nref.append(referente[c])
                c -= 1
            referente = nref
        # errores['Consistencia'] = ['No es posible comparar por error de lectura en tabla']
        # return errores
    c = -1
    for comp in comparador:
        c +=1
        ref = referente[c]
        if type(comp) == str or type(ref) == str: #si hay NS o NA
            nsa = NS(comp,ref)
            if nsa == 1:
                if 'Consistencia' in errores:
                    errores['Consistencia'].append(f'Inconsistencia detectada con el uso de NA/NS en pregunta {nombre_ref}, con los valores {comp} y {ref}')
                else:
                    errores['Consistencia'] = [f'Inconsistencia detectada con el uso de NA/NS en pregunta {nombre_ref}, con los valores {comp} y {ref}']
                    continue
                # return errores
            #convertir a cero para poder hacer comparaciones posteriores
            if type(comp) == str:

                comp = 0
            if type(ref) == str:
                ref = 0

            if nsa  == 0:#quiere decir que es correcto el registro

                continue
        #cualquier comparación se basa en que sean iguales, por eso es lo primero
        if operacion == 1:
            if comp == ref:
                continue
            else:
                if 'Consistencia' in errores:
                    errores['Consistencia'].append(f'El valor {comp} no es igual que {ref} de pregunta {nombre_ref}')
                else:
                    errores['Consistencia'] = [f'El valor {comp} no es igual que {ref} de pregunta {nombre_ref}']
                # return errores
        #sino son iguales entonces se hacen las operaciones
        if operacion == 2:
            
            if comp <= ref:
                continue
            else:
                if 'Consistencia' in errores:
                    errores['Consistencia'].append(f'El valor {comp} no es menor o igual que {ref} de pregunta {nombre_ref}')
                else:
                    errores['Consistencia'] = [f'El valor {comp} no es menor o igual que {ref} de pregunta {nombre_ref}']
                # return errores
        if operacion == 3:
            if comp >= ref:
                continue
            else:
                if 'Consistencia' in errores:
                    errores['Consistencia'].append(f'El valor {comp} no es mayor o igual que {ref} de pregunta {nombre_ref}')
                else:
                    errores['Consistencia'] = [f'El valor {comp} no es mayor o igual que {ref} de pregunta {nombre_ref}']
                # return errores
        
        
    return errores

def NS(p_actual,p_comp):
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
    comparador = p_actual
    referente = p_comp
    n = ['NS','ns']
    a = ['NA','na']
    br = ['borra']
    # print(referente,comparador) #borra y cero respectivamete 1.63
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
    if referente in br and comparador == 0: #error más nuevo donde pregunta referente no tienen nada por instruccion y en pregunta actual tiene cero, seguramente por instrucción debe ir en blanco
        return 1
    if referente > 0 and comparador in n:
        return 0

def lista_valores(tabla1,autosuma,tipo_val,indices,valor_conseguir):
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
    # print(autosuma,tipo_val,indices,valor_conseguir)
    tabla = tabla1.fillna(0)#en este punto está bien cambiar los Nan por cero ya que no se busca comprobación de blancos
    #nota: siguene pendientes condicionales para otro tipo de busquedas, como las de fila
    if valor_conseguir == 'columna':
                        
        if autosuma == 'Si' and tipo_val == 'autosuma':
            
            pa_val = list(tabla.iloc[-1,:])
        
        if autosuma == 'Si' and tipo_val == 'Toda la columna':
            if len(indices)>1:
                pa_val = list(tabla.iloc[-1,indices])
                return pa_val
            
            pa_val = list(tabla.iloc[:,indices[0]])
            return pa_val
        
        if autosuma == 'Si' and tipo_val == 'NT_allc':
            
            if indices:
                pa_val = list(tabla.iloc[:,indices[0]]) #tal vez genere un error después por los indices (no hay)
            if not indices:
                pa_val = list(tabla.iloc[:,1])
                return pa_val
            #como es pregunta de NT_desagregados hay que hacer una correccion en el orden de los datos
            pa_val = [pa_val[-1]] + pa_val[:-1]
            
            return pa_val
            
        if autosuma == 'No' and tipo_val == 'autosuma':
            pa_val = []
            for col in tabla:
                lista = list(tabla[col])
                nlis = [x for x in lista if type(x) != str] #para quitar registros que no son numeros
                suma = sum(nlis)
                pa_val.append(suma)
        if tipo_val == 'unifila':
            pa_val = list(tabla.iloc[0,:])
        if autosuma == 'No' and tipo_val == 'suma todo':
            #seguro es de unifila pero hay que sumar toda la fila
            pa_val = sumar_fila(list(tabla.iloc[0,:]))
        if autosuma == 'Si' and tipo_val == 'suma todo':
            pa_val = list(tabla.iloc[:,1])
            # print('esto deberia ser',pa_val)
            return [pa_val[-1]] #regresa solo un valor que pertenece a la autosuma y se pone en lista para no romper ese formate 
        if type(tipo_val) == int:
            pa_val = list(tabla.iloc[tipo_val-1,:])
            
    # if valor_conseguir == 'fila':
    if 'numeral_fila' in tipo_val:#esta condicional aplica para los que son numerales pero no deben ser sumados
        divi = tipo_val.split()
        if '.' in divi[1]:
            numeral = divi[1].split('.')
        if not '.' in divi[1]:
            numeral = [divi[1],'1'] #simular que es numeral .1, porque de igual forma se buscará el primer valor del numeral, así que no hay problema
        prim = numeral[0]
        index_tab = list(tabla.iloc[:,0])#conseguir la columna donde vienen los numerales de la tabla
        posibles = []
        c = 0

        if len(index_tab) == 1:
            pa_val = list(tabla.iloc[0,:]) #unifilas
            return pa_val
        if tabla1.isna().any().any():#tablas NT desagregados
            for col in tabla:
                if col.startswith(prim):
                    posibles.append(c)
                c += 1
            sec = int(numeral[1])-1
            pa_val = list(tabla.iloc[:,posibles[sec]])
            return pa_val
        
        for indice in index_tab:

            if indice.startswith(prim):
                posibles.append(c)
            c += 1
        sec = int(numeral[1])-1 #para buscar la segunda parte del numeral, si fuese 3.1, aquí se buscaría el 1, menos uno para obtener el índice de la lista posibles
        # print(sec,posibles,type(prim),index_tab)
        pa_val = list(tabla.iloc[posibles[sec],1:])
        
        return pa_val #aqui retorna toda la fila del numeral
    if 'numeral_suma' in tipo_val:#numeral que tiene que ser sumado
        divi = tipo_val.split()
        numeral = divi[1]
        filas_asumar = []
        c = 0
        for fila in list(tabla.iloc[:,0]):
            if numeral in fila:
                filas_asumar.append(c)
            if filas_asumar:
                if c - filas_asumar[-1] > 2: #esto es por si hay numeral 1 y la tabla tiene hasta numeral 10, no se busca sumar ese numeral también
                    break
            c += 1
        #hacer la suma de las filas
        dfinteres = tabla.iloc[filas_asumar,1:]
        pa_val = []
        for col in dfinteres:
            suma = sumar_fila(list(dfinteres[col]))
            pa_val.append(suma[0])
        return pa_val
        
    if not indices:
        if 'Total' in list(tabla.columns):
            pa_val = list(tabla['Total'])
            return pa_val
        else:
            pa_val = list(tabla.iloc[:,1])  
            return pa_val
    pa_val = pa_val[indices[0]:indices[-1]+1]
    
    return pa_val

def sumar_fila(lista):
    "funcion para sumar lista y retornar el valor total, es necesario por ns"
    NA = 0
    NS = 0
    res = 0
    for valor in lista:
        if type(valor) == str:
            n = valor.lower()
            if n == 'na':
                NA = 1
            if n == 'ns':
                NS = 1
        else:
            res += valor
    if res == 0:
        if NA > 0 and NS > 0:
            res = 'NS'
        if NS > 0 and NA == 0:
            res  = 'NS'
        if NA > 0 and NS == 0:
            res = 'NA'
    return [res]

def analizarIns(texto,instr):
    "analiza el texto de la instrucción, regresa string de autosuma o int de numeral para hacer la comparación"
    # print(texto)
    if 'numeral' in texto:
        #obtener el numeral o numerales a sumar en la tabla
        if not 'suma' in texto:
            nt = texto.split('numeral')
            nt1 = nt[1].split()
            # try:
            #     numeral = int(nt1[0])
            #     numeral = 'autosuma' #para caso especifico de pregunta que no es tabala y genera una de filas unicas
            # except:
            numeral = 'numeral_fila '+ nt1[0]
        if 'suma' in texto:
            nt = texto.split('numeral')
            nt1 = nt[1].split()
            numeral = 'numeral_suma '+ nt1[0]
            
        return numeral
    if 'suma' in texto or 'recuadro' in texto:
        if 'suma de las cantidades registradas' in texto and not 'columna' in texto and not 'numeral' in texto:
            return 'suma todo'
        if 'columna' in texto:
            # if 'desagregación' in instr:
            #     return 'fila autosuma'
            return 'autosuma'
        if 'desagregación' in instr:
            return 'NT_allc' #porque aqui necesitamos toda la columna, se trata de una tabla NT_desagregados
        return'autosuma'    
    if 'ara cada' in texto:#aqui llega porque no hay numeral ni palabra suma en el texto pero sí hay para cada elemento, es decir, comparar toda la columna
        return'Toda la columna'
    
    if 'suma' not in texto and 'numeral' not in texto:
        return 'unifila'

def analizarT(t1,t2,en1,en2):
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
    #evaluar encabezados de ambas tablas
    if type(en1) == list:
        if not en1:
            return res
    if type(en2) == list:
        if not en2:
            return res
    
    ene1 = []#esto es para sacar las prtes de arriba del encabezado y comparar lo que dicen con la de la otra tabla
    ene2 = []
    for col in en1:
        lista = list(en1[col])
        for val in lista:
            if val != 'borra':
                ene1.append(val)
                break
    for col in en2:
        lista = list(en2[col])
        for val in lista:
            if val != 'borra':
                ene2.append(val)
                break
    #hacer la comparación pero desde la columna uno, ya que la cero suele ser del index
    posibles1 = []
    posibles2 = []
    c = 1
    for val in ene1[1:]:
        if val in ene2:
            posibles1.append(c)
        c += 1
    c = 1
    for val in ene2[1:]:
        if val in ene1:
            posibles2.append(c)
        c += 1
    #de esos posibles solo nos importa tener los que tienen continuidad
    c = 0 
    for val in posibles1[1:]:
        if val - posibles1[c] > 1:
            break
        c += 1
    definitivo1 = posibles1[:c+1]
    
    c = 0 
    for val in posibles2[1:]:
        if val - posibles2[c] > 1:
            break
        c += 1
    definitivo2 = posibles2[:c+1]
    
    res['p_act'] = definitivo1
    res['p_comp'] = definitivo2
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
        if pregunta_c.endswith('.'):
            pregunta_c = pregunta_c[:-1]
        return pregunta_c


def sinonosabe(df1,autosuma,tipo):
    """
    

    Parameters
    ----------
    df : dataframe de la pregunta
    autosuma: str si hay autosuma en la tabla o no
    tipo : str el tipo de la tabla(tabla,nt_desagregados o de delitos)

    Returns
    -------
    errores: dict. Regresa un diccionario con los errores detectados
    sobre contestar a preguntas de si no no se sabe dentro de tablas,
    así como las de no aplica (son preguntas en donde se debe dejar en
    blanco el resto de la fila o contestar puro cero o na, cualquier 
    otro valor es un error). También da errores de blanco

    """
    df = df1.copy()
    errores = {}
    if tipo == "NT_Desagregados":
        #aqui solo se va a buscar espacios en blanco porque son preguntas con datos en un formato no de tabla
        v = df1.isin(['BO']).any().any()
        if v:
            if 'blanco' in errores:
                errores['blanco'].append('Hay espacios en blanco')
            if 'blanco' not in errores:
                errores['blanco'] = ['Hay espacios en blanco']
        return errores
    
    if tipo != "NT_Desagregados":
        indices = list(df.iloc[:,0])
        df = df.replace({'borra':0,'NS':0,'NA':0})
        if autosuma == 'Si':#porque aquí también hay tablas con autosuma y esa fila no sirve para esta validacion
            bor = df.shape
            df = df.drop([bor[0]-1],axis=0)
        separar = []
        no_aplica = []
        c = 0
        for columna in df:
            if 'No aplica' in str(columna) or 'No se realizaron acciones formativas' in str(columna):
                no_aplica.append(c)
            texto = str(columna).replace(' ','')#quitar espacios porque luego no lo escriben igual siempre
            comparar = '1.Sí/'
            if comparar in texto:
                separar.append(c)
            c += 1
        if not separar:#porque no se detectó columna que tenga lo que a esta validacion importa
            #se hace detcción de blancos
            if not no_aplica:
                nf = 0
                for fila in indices:
                    if fila != 'borra':
                        #comprobacion adiiconal para filas que no tienen contenido
                        filan1 = str(fila)
                        filan1 = filan1.split(' ')
                        no_vacio = 0
                        for elem in filan1[1:]: #itera del elemento uno en adelante porque usualmente el elemento cero es un numero, en cuyo caso y aunque fuese borra, ese no interesa para descartar
                            if elem != 'borra':
                                no_vacio += 1
                        if no_vacio:
                            fila_comp = list(df1.iloc[nf,1:]) #con esto ya se tiene la fila sin el index
                            
                            if 'borra' in fila_comp:
                                if 'blanco' in errores:
                                    errores['blanco'].append(f'Fila {nf+1} tiene espacios en blanco')
                                if 'blanco' not in errores:
                                    errores['blanco'] = [f'Fila {nf+1} tiene espacios en blanco']
                    nf +=1 
            return errores
        
        if no_aplica:
            no_a = list(df.iloc[:,no_aplica[0]]) #es la columna de no aplica
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
                    if fila[0] == 0 and 'borra' not in indices[c1] and c == 0:
                        # print(indices[c1],'11111111111')
                        if no_aplica:
                            if no_a[c1] != 'X':
                                if 'catalogo' in errores:
                                    errores['catalogo'].append(f'Faltó contestar pregunta de catálogo en fila {c1+1}')
                                if 'catalogo' not in errores:
                                    errores['catalogo'] = [f'Faltó contestar pregunta de catálogo en fila {c1+1}']
                        if not no_aplica:
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
                                errores['catalogo'].append(f'Por respuesta de catálago, no puede registrar nada en el resto de la fila {c1+1}')
                            if 'catalogo' not in errores:
                                errores['catalogo'] = [f'Por respuesta de catálago, no puede registrar nada en el resto de la fila {c1+1}']
                    if fila[0] == 0 and 'borra' not in indices[c1] and c == 0:
                        # print(indices[c1],'11111111111')
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
    # print(df.shape,'totales_fila in')
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
    c = 0
    for colum in df:
        if 'Total' in str(colum):
            total.append(c)
        c += 1
    if len(total)>1:
        c = 0
        for to in total:
            try:
                ndf = df.iloc[:,to:total[c+1]]
            except:
                ndf = df.iloc[:,to:]
            aritmetic = vts(ndf)
            if aritmetic:
                
                if 'aritmetico' in errores:
                    errores['aritmetico']+=aritmetic['aritmetico']
                if 'aritmetico' not in errores:
                    errores['aritmetico'] = aritmetic['aritmetico']
    else:
        aritmetic = vts(df)
        if aritmetic:
            
            if 'aritmetico' in errores:
                errores['aritmetico']+=aritmetic['aritmetico']
            if 'aritmetico' not in errores:
                errores['aritmetico'] = aritmetic['aritmetico']
               
    return errores
    
def vts(df):
    "esta funcion se desprendio de totales_fila derivado de la necesidad de iterar el dataframe en el caso de que hubiesen varios totales dentro de la tabla"
    # print(df.shape,'vts in')
    errores = {}      
    total = []
    subtotal = []
    c = 0
    for colum in df:
        if 'Total' in str(colum):
            total.append(c)
        if 'Subtotal' in str(colum):
            subtotal.append(c)
        c += 1
    # print(total,subtotal,df.shape)
            
    
    if total and not subtotal:
        
        c = 0
        for tot in total:
            c1 = 0
            
            for fila in list(df.iloc[:,0]):
                
                try:
                    lista = list(df.iloc[c1, tot:total[c+1]])
                except:
                    lista = list(df.iloc[c1, tot:])
                # if c1 < 3:
                #     print(len(lista))
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
        c = 0
        for tota in total:
            try: #esto es para cuando hay más de un total y alguno de ellos u otro tiene desagregados
                if subtotal[0] > total[c+1]:
                    limites.append(total[c+1])
                    c += 1
                    continue
            except:
                pass
            for sub in subtotal:
                if sub > tota:
                    limites.append(sub) #límites tendrá un numero por cada elemento mayor a cada total detectado
                    break
            c += 1
                
        c = 0
        for limite in limites:#generar listas con columnas intermedias entre un total y su primer subtotal
            if limite-total[c]>0:
                lista_columnas =[i for i in range(total[c]+1,limite)]#el mas uno es porque necesitamos saber la columna a partir del total
            else:
                lista_columnas =[i for i in range(total[c],limite)]
            desagre_totales.append(lista_columnas)
            c += 1
        # print(limites,desagre_totales,total, subtotal)
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
                CN = list(df.columns)
                DE = CN[des]
                IC =[]
                c1 = 0
                for nombr in CN:
                    if DE in nombr:
                        IC.append(c1)
                    c1 += 1
                # print(IC)
                c = 0
                for fila in list(df.iloc[:,0]):#primero se itera por fila del df
                    lista_fila = list(df.iloc[c,:])#se saca la lista de los valores de la fila
                    # lista = [lista_fila[des]] #esta es la lista que eventualmente pasará a ser evaluda. Inicia con el total del desagregado y se complementa con los desagregados de cada subtotal
                    # c1 = 0
                    # for sub in subtotal:
                    #     if sub > des: #para no trabajar con subtotales de otro total
                    #         if comp[c1] == ref:
                    #             agregar =  lista_fila[sub+c2]
                    #             lista.append(agregar)
                    #         if comp[c1] > ref:
                    #             div = comp[c1]//ref
                    #             for i in range(div):
                    #                 aumento = ref*i
                    #                 agregar = lista_fila[sub+c2+aumento]
                    #                 lista.append(agregar)
                            
                    #     c1 += 1
                    lista = [lista_fila[i] for i in IC]
                    # print(lista)
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
            c1 = 0
            for tot in total:
                lista = [lista_fila[tot]]
                for sub in subtotal:
                    try: #para atender casos donde hay varios totales pero algunos no tienen subtotales
                        if sub > tot and sub < total[c1+1]:
                            lista.append(lista_fila[sub])
                    except:
                        if sub > tot:
                            lista.append(lista_fila[sub])
                # print(lista)
                aritmetic = evaluador_suma(lista,f'fila{c+1}')
                if aritmetic:
                   
                    if 'aritmetico' in errores:
                        errores['aritmetico']+=aritmetic
                    if 'aritmetico' not in errores:
                        errores['aritmetico'] = aritmetic
                c1 += 1
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
        columnas_ex = ['Nombre',
                       'Clave',
                       'No aplica',
                       'Tipo de delito'
                       'Código',
                       'Código ',
                       'Centro penitenciario',
                       'Tipo de hecho presuntamente violatorio de derechos humanos'
                       ]#nombres de columnas donde van valores de string y que deben ser excluidas
        errores = []
        no_err = []
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
            if valor == 'borra' or valor == 'BO':
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
                brrr = ['borra','BO']
                if valor not in brrr:
                    
                    for val in columnas_ex:
                        if val in indi:
                            no_err.append(1)
                    if not no_err:
                        errores.append(f'Error: el valor {valor} no es permitido en {indi}')
            c += 1
        suma = sum(desagregados)
        # print('llega1',total,suma,desagregados,lista)
        if blanco > 0:
            if total == 'borra' or total == 'BO':
                blanco += 1
                if len(lista) == blanco:
                    
                    return
            #     else:
            #         errores.append(f'{indi} Hay espacios en blanco')
            #         return errores
            # if total != 'borra':
            #     errores.append(f'{indi} Hay espacios en blanco')
            #     return errores
        if total == 0:
            if ns == 'Si':
                errores.append(f'{indi} Si el total es cero, valores de desagregados no pueden ser NS o mayores a cero')
                return errores
            if suma > 0:
                errores.append(f'{indi} Si el total es cero, valores de desagregados no pueden ser mayores a cero')
                return errores
        if total in convertir and suma > 0:
            errores.append(f'Error: Suma de desagregados no puede ser mayor a cero si total es NS o NA en {indi}')
            return errores
        if total in convertir and suma == 0:
            if total.lower() == 'na' and ns == 'Si':
                errores.append(f'Error: Si el total es NA ninguno de sus desagregados puede ser NS para {indi}')
        if type(total) == str and total not in convertir and not no_err:
            if total == 'borra':
                errores.append(f'Error: el total es un espacio vacío y sus desagregados contienen algo distinto a un espacio vacío como respuesta en {indi}')
                return errores
            errores.append(f'Error: el total es un valor no permitido como respuesta en {indi}')
            return errores
        if type(total) != str:
            # print('llega',total,suma)
            if total != suma:
                if total != 0 and suma >= 0 and ns == 'No':
                    
                    errores.append(f'Error: Suma de desagregados no coincide con el total en {indi}(Total = {total}vs Suma de desagregados = {suma})')
                if total == 0 and ns == 'Si':
                    errores.append(f'Si el total es cero, ningún desagregado puede ser NS en {indi}')
                    
        return errores
    
    return