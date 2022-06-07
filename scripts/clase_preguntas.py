# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 14:29:53 2022

@author: AARON.RAMIREZ
"""
import pandas as pd
import numpy as np

class clase_pregunta():
   
    def __init__(self,dataframe,seccion):
        self.nombre_lit = dataframe.iat[0,0]
        borrar = '.- '
        self.nombre = ''.join(c for c in self.nombre_lit if c not in borrar)
        self.dfraw = dataframe
        self.tablas = clase_pregunta.tablas(self,dataframe)
        # self.metadata = metadata
        # self.instr = clase_pregunta.clas_instru(instrucciones)
        # self.tipo_pregunta = clase_pregunta.clas_tipo() #inserte funcion con modelo de clasificacion de tipos de pregunta
        # self.seccion = seccion
       
    def clas_instru(instrucciones):
        #Aquí irá el modelo de clasifiacion
        dic = {'texto':instrucciones,'clas':[]}
        return dic
   
    def clas_tipo(df):
        #aqui modelo de clasificación de pregunta tipo analizarcoor
        return 'desconocido'
    
    def tablas(self,df):
        "hacer varios dataframes por cada tabla de la pregunta"
        nombres_iniciales = list(df.columns)
        bs = ['I)','II)','III)','IV)','V)','VI)','VII)','VIII)']
        cortar = []
        fila = 0
        self.rawercut = {}
        for valor in df[nombres_iniciales[2]]: #equivalente a unnamed 2 
            
            for v in bs:
                try:
                    if v in valor:
                        cortar.append(fila)
                except: #excepcion por valores nan
                    pass
            fila += 1
        
        if not cortar:
            tablas = {1:clase_pregunta.tabla(self,df)}
            return tablas
        
        if cortar:
            cortar = list(set(cortar))
            cortar.sort()
            
            tablas = {}
            c = 0
            for ind in cortar:
                if ind != cortar[-1]:
                    nf = df.iloc[ind:cortar[c+1]+1]   
                else:
                    nf = df.iloc[ind:]
                self.rawercut[c] = nf
                tablas[c] = clase_pregunta.tabla(self,nf)
                c += 1
                    
        return tablas
    
    def tabla(self,df):
        """
       

        Parameters
        ----------
        df : DataFrame pandas.

        Returns
        -------
        nuevo_df : DataFrame pandas. Genera un nuevo dataframe solo
                    con la tabla o tablas que contenga la pregunta.
                    En caso de contener varias tablas, genera un
                    diccionario con df para cada tabla.

        """
        #comienza con proceso de detectar tabla por partes para juntarlo todo en una sola

        
        df = df.reset_index(drop=True)
        df = clase_pregunta.borrar_S(df)
        
        # nombres_iniciales = list(df.columns)
        df = clase_pregunta.tabla_partes(df)
        self.rawer = df
        na = pd.isna(df)
        columnas = []
        c = 0
        for i in na:
            if False in na[i].values:
                columnas.append(c)
            c += 1
        mayor = max(columnas)
        nuevo_df = clase_pregunta.borrar_col(df)
        
       
       
        if mayor > 15: #Se trata de una tabla
            nuevo_df = clase_pregunta.transformar_tabla(nuevo_df)
        else: #para los que no son tablas
            nuevo_df = clase_pregunta.transformar_notab(nuevo_df)

        return nuevo_df
   
    @staticmethod
    def transformar_notab(df):
        print(df.columns,df.head())
        #primer paso distinguir de cual de las dos se trata. Las de medio tablas inician en el 6 y la otras en el 2. Un buen indicador también son los saltos de lineas
        return df
    
    @staticmethod
    def transformar_tabla(nuevo_df):
        # nombres_iniciales = list(nuevo_df.columns)
        # print(nombres_iniciales)
        colyfil = clase_pregunta.imagen(nuevo_df)
        espacios = clase_pregunta.distancia(colyfil['fila'],1) #forzozamente debe arrojar al menos dos numeros dentro de la lista
        if not espacios or len(espacios)==1:
            espacios = [colyfil['fila'][0],colyfil['fila'][-1]]
        
        inf =  [i for i in range(0,colyfil['fila'][espacios[0]+1])]
        sup = [i for i in range(colyfil['fila'][espacios[1]]+1,len(nuevo_df['Unnamed: 2'].values))]
        nuevo_df = nuevo_df.drop(inf + sup, axis=0)
       
        try:
            nuevo_df = nuevo_df.drop(['Unnamed: 0','Unnamed: 1'],axis=1)
        except:#excepcion por si las columnas unnamed 0 y 1 ya fueron borradas. Eso pasa con las preguntas que tienen varias tablas
            pass
        nuevo_df = clase_pregunta.borrar_col(nuevo_df)

        #Encontrar numeral para determinar si es tabla con varias filas o de fila única y perfilar los nombres de columnas
        bus = ['1.', '1. ', '01.', '01. ']
        comprobador = []
        val = {}
        
        # print('por encontrar', nuevo_df['Unnamed: 2'].values)
        for uno in bus:
            if comprobador: #no tiene caso que se siga iterando si ya lo encontró
                break
            # print(nuevo_df.columns)
            if uno in nuevo_df['Unnamed: 2'].values: #nombres iniciales [2] es una referencia a la columna unnamed 2, pero ésta aveces cambia de nombre porque se borra cuando hay una mala lectura de la tabla
                
                comprobador.append(1)
                c = 0
                index = 0
                for fila in nuevo_df['Unnamed: 2'].values:
                    if uno in str(fila):
                        index = c
                        break
                    c += 1
                nuevo_df = nuevo_df.fillna('borra')
                nombres = []
                for col in nuevo_df:
                    #aqui se mete el proceso para los nombres de columnas
                    ap = list(nuevo_df[col])
                    nnn = []
                    condicion = 0
                    # print(ap[0])
                    
                    intermedios = []
                    for valor in ap[0:index-1]: #comprobar si hay algún valor en tabla de encabezado
                        if valor != 'borra':
                            intermedios.append(valor)
                            
                    if ap[0] != 'borra' or intermedios:
                        if ap[0] != 'borra' and intermedios:
                            # if intermedios[0] != ap[0]:
                            nnn = intermedios + [ap[0]]
                            # else: #condicionales para evitar la copia de nombre en columna Total
                            #     nnn = intermedios
                        else:
                            for filaN in ap[0:index]:
                                if filaN != 'borra':
                                    nnn.append(filaN)
                    if nnn:
                        # print(nnn, intermedios)
                        nombres = nnn
                    if not nombres:
                        nombre = str(ap[index-1])
                   
                    if nombres:
                        if len(nombres) > 1:
                            if ap[index-1] == 'borra' and not intermedios:
                                
                                nombre = [str(n) for n in nombres[0:-1]]
                                condicion = 'juntar'
                            if ap[index-1] == 'borra' and intermedios:
                                nombre = [str(n) for n in nombres]
                            else:
                                nombre = [str(n) for n in nombres[0:-1]]+[ap[index-1]]
                        else:
                            nombre = str(nombres[0])
                        
                        nombre = [str(n) for n in nombre]
                        nombre = ' '.join(nombre)
                    # print(nombre,nombres)
                    if nombre in val or condicion == 'juntar': #si el nombre generado ya está en el diccionario, hay que unir ambas columnas
                        # if nombre in val:
                        #     print('por nombre repetido')
                        # if condicion == 'juntar':
                        #     print('por condicion')
                        # if nombre in val and condicion == 'juntar':
                        #     print('por nombre y condicion')
                        ind = 0
                        nl = []
                        for key in val:
                            nombre = key #con esta iteracion se asegura tener el útimo nombre registrado de columna para juntarla
                        for elem in val[nombre]:
                            nl.append(str(elem) + ' '+ str(ap[index:][ind]))
                            ind += 1
                        val[nombre] = nl
                    if nombre not in val:
                       
                        val[nombre] = ap[index:] #por los nan, se sobre escriben algunas columnas
                    
                nuevo_df = pd.DataFrame(val)
                
        if not comprobador: #tabla de filas unicas
            nuevo_df = nuevo_df.fillna('borra')
            nombres = []
            for col in nuevo_df:
                ap = list(nuevo_df[col])
                nnn = []
                condicion = 0
                # print(ap[0])
                if ap[0] != 'borra':
                    for filaN in ap[0:-1]:
                        if filaN != 'borra':
                            nnn.append(filaN)
                if nnn:
                    
                    nombres = nnn
                if not nombres:
                    try:
                        nombre = str(ap[-2])
                    except:
                        nombre = str(ap[-1])
               
                if nombres:
                    if len(nombres) > 1:
                        if ap[-1] == 'borra':
                            nombre = [str(n) for n in nombres[0:-1]]
                            condicion = 'juntar'
                        else:
                            nombre = [str(n) for n in nombres[0:-1]]+[ap[-2]]
                    else:
                        nombre = str(nombres[0])
                    
                    nombre = [str(n) for n in nombre]
                    nombre = ' '.join(nombre)
                # print(nombre,nombres)
                # if nombre in val or condicion == 'juntar': #si el nombre generado ya está en el diccionario, hay que unir ambas columnas
                #     ind = 0
                #     nl = []
                #     for elem in val[nombre]:
                #         nl.append(str(elem) + ' '+ str(ap[index:][ind]))
                #         ind += 1
                #     val[nombre] = nl
                if nombre not in val:
                    val[nombre] = [ap[-1]]
           
            nuevo_df = pd.DataFrame(val)    
        return nuevo_df
    
    @staticmethod
    def borrar_S(df):
        "Borrar la letra S de autosumas en columnas y la palabra Complemento"
        S = clase_pregunta.busqueda_exacta(df, 'S')
        complemento = clase_pregunta.buscarpalabra('Complemento', df)
        if not S and not complemento:
            return df
        if S:
            loc = S[0]
            # fila = loc[0]
            columna = loc[1]
            c = 0
            for col in df:
                
                if c == columna:
                    
                    df.loc[df[col]=='S',col] = np.nan #hayq ue especificar el col para que no cambie toda la fila
                    
                c += 1
        if complemento:
            
            loc = complemento[-1]
            # fila = loc[0]
            columna = loc[1]
            c = 0
            for col in df:
                
                if c == columna:
                    A = 'Complemento'
                    if df.isin([A]).any().any():
                        df.loc[df[col]==A,col] = np.nan #hayq ue especificar el col para que no cambie toda la fila
                        break
                    A = 'Complemento '
                    if df.isin([A]).any().any():
                        df.loc[df[col]==A,col] = np.nan #hayq ue especificar el col para que no cambie toda la fila
                        break
                    for i in range(0,20):
                        A =  f'Complemento {i}'
                        if df.isin([A]).any().any():
                            df.loc[df[col]==A,col] = np.nan #hayq ue especificar el col para que no cambie toda la fila
                            break
                c += 1
            
        return df
    
    @staticmethod
    def borrar_col(df):
        
        df = df.reset_index(drop=True)
        na = pd.isna(df)
        ncolum = []
        for i in na:
            if False in na[i].values:
                ncolum.append(i)
        # print(na['Unnamed: 2'].values)
        borrar_col = [nombre for nombre in list(df.columns) if nombre not in ncolum]
        nuevo_df = df.drop(borrar_col, axis=1)
        # nuevo_df = nuevo_df.drop([1], axis=0)
        nuevo_df = nuevo_df.reset_index(drop=True)
        # print('de la funcion ',ncolum)
        return nuevo_df
    
    @staticmethod
    def tabla_partes(df):
        partes = clase_pregunta.buscarpalabra('(1 de', df)
        if not partes:
            return df
        colyfil = clase_pregunta.imagen(df)
        espacios = clase_pregunta.distancia(colyfil['fila'],1)
        #Espacios tendrá más de dos elementos, y se cuenta a partir del segundo, ya que las tablas siguen esa distribución de una fila vacía por salto de parte de tabla
        cant_tablas = df.iat[partes[0][0],partes[0][1]]
        can = cant_tablas[-3:-1]
        can = int(can) #siempre tiene que ser 2 o más
        filas_inicio = [np.nan for i in range(colyfil['fila'][espacios[0]+1])]#[espacios[0]+1]+1)
        # filas_fin = [np.nan for i in range(colyfil['fila'][espacios[1]+1]+1)] #este sirve para cuando estén vacias las columnas en el contenido
        # filas_fin = [np.nan for i in range(colyfil['fila'][espacios[1]+1]+1,colyfil['fila'][-1]+1)]
        # print(len(filas_fin),colyfil['fila'][espacios[1]+1]+1,colyfil['fila'][-1]+1)
        #contruir lista de columnas para el dataframe
        nuevas_columnas = {}
        longitud_tabla = colyfil['fila'][-1]+1-colyfil['fila'][espacios[1]+1]#+1 #la cantidad de filas que tiene la tabla
        llenado = [np.nan for i in range(longitud_tabla)]
        for tabla in range(1,can):
            filaS = colyfil['fila'][espacios[tabla]]+2 #la fila donde empieza la tabla
            
            c = 0
            for columna in df:
                ap = list(df[columna])
                nuevas_columnas[str(tabla)+str(c)] = filas_inicio + ap[filaS:filaS+colyfil['fila'][espacios[1]+1]]+llenado
                
                c += 1
        
        add = pd.DataFrame(nuevas_columnas)
        nuevo_df = pd.concat([df,add],axis=1)
        nuevo_df = nuevo_df.drop([partes[0][0]],axis=0)
        return nuevo_df
    
    @staticmethod
    def distancia(lista,nfilas):
        """
       
   
        Parameters
        ----------
        lista : list. Lista con numeros
        nfilas : int. La distancia o diferencia a medir
   
        Returns
        -------
        li : list. Regresa una lista con los indices de la lista de entrada en donde se cumple la diferencia señalada
   
        """
       
        li = []
        con = 0
        for i in lista:
            try:
                a = lista[con+1]-lista[con]
            except:
                a = 0
            if a > nfilas:
                li.append(con)
            con+=1
        return li
   
    @staticmethod
    def imagen(df):
        """
       
   
        Parameters
        ----------
        df : DataFrame
   
        Returns
        -------
        ente : (dict).genera un diccionario con filas y columnas en los que se
        registra un valor de la pregunta
   
        """
     
        sa = pd.isna(df)
        listas = sa.to_numpy().tolist()
        cont = 0
        entot = {'fila':[],'columna':[]}
        for lista in listas:
            vo = 0
            for elm in lista:
                if False == elm:
                    entot['fila'].append(cont)
                    entot['columna'].append(vo)          
                else:
                    pass
                vo+=1
            cont+=1
       
        return entot  
    
    @staticmethod
    def buscarpalabra(palabra,hopan):
        """
        
    
        Parameters
        ----------
        palabra : (str). La palabra o frase que se va a 
        buscar (no es búsqueda exacta!, solo que esté en el texto).
        hopan : Dataframe de pandas.
    
        Returns
        -------
        entot : (list). Regresa una lista de tuplas con las coordenadas de 
        la palabra
    
        """
        
        sa = hopan.fillna('')
        listas = sa.to_numpy().tolist()
        cont = 0
        entot = []
        for lista in listas:
            vo = 0
            try:
                for elm in lista:
                    if palabra in elm:
                        sad = (cont,vo)
                        entot.append(sad)
                    else:
                        pass
                    vo+=1
                cont+=1
            except:
                pass
        return entot
  
    @staticmethod
    def busqueda_exacta(dataframe,vaal):
        """
        
    
        Parameters
        ----------
        dataframe : TYPE
            DESCRIPTION.
        vaal : (str). Palabra a buscar
    
        Returns
        -------
        res : (list). genera lista de tuplas con coordenadas del vaal asignado;
        Es coincidencia exacta
    
        """
        
        sa = dataframe.isin([vaal])
        listas = sa.to_numpy().tolist()
        cont = 0
        entot = {'fila':[],'columna':[]}
        res = []
        for lista in listas:
            vo = 0
            for elm in lista:
                if True == elm:
                    entot['fila'].append(cont)
                    entot['columna'].append(vo)
                    res.append((cont,vo))
                else:
                    pass
                vo+=1
            cont+=1
        
        return res  


