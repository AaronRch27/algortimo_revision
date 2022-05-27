# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 14:29:53 2022

@author: AARON.RAMIREZ
"""
import pandas as pd


class clase_pregunta():
    
    def __init__(self,dataframe,seccion):
        self.nombre_lit = dataframe.iat[0,0]
        borrar = '.- '
        self.nombre = ''.join(c for c in self.nombre_lit if c not in borrar) 
        self.dfraw = dataframe
        self.tabla = clase_pregunta.tabla(dataframe)
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
    
    def tabla(df):
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
        na = pd.isna(df)
        columnas = []
        c = 0
        for i in na:
            if False in na[i].values:
                columnas.append(c)
            c += 1
        mayor = max(columnas)
        nuevo_df = clase_pregunta.borrar_col(df)
        #Aqui debe ir iteracion para más de una tabla 
        
        if mayor > 15: #Se trata de una tabla
            colyfil = clase_pregunta.imagen(nuevo_df)
            espacios = clase_pregunta.distancia(colyfil['fila'],1) #forzozamente debe arrojar al menos dos numeros dentro de la lista
            inf =  [i for i in range(0,colyfil['fila'][espacios[0]+1])]
            sup = [i for i in range(colyfil['fila'][espacios[1]]+1,len(nuevo_df['Unnamed: 2'].values))]
            nuevo_df = nuevo_df.drop(inf + sup, axis=0)
            nuevo_df = nuevo_df.drop(['Unnamed: 0','Unnamed: 1'],axis=1)
            nuevo_df = clase_pregunta.borrar_col(nuevo_df)
            # print(colyfil,espacios,inf,sup)
            
            #Encontrar numeral para determinar si es tabla con varias filas o de fila única y perfilar los nombres de columnas
            bus = ['1.', '1. ', '01.', '01. ']
            comprobador = []
            val = {}
            print(nuevo_df.head())
            try:
                for uno in bus:    
                    if uno in nuevo_df['Unnamed: 2'].values:
                        comprobador.append(1)
                        c = 0
                        index = 0
                        for fila in nuevo_df['Unnamed: 2'].values:
                            if uno in str(fila):
                                index = c
                                break
                            c += 1
                        
                        for col in nuevo_df:
                            ap = list(nuevo_df[col])
                            val[ap[index-1]] = ap[index:]
                        
                        nuevo_df = pd.DataFrame(val)
                if not comprobador: #tabla de filas unicas
                    for col in nuevo_df:
                        ap = list(nuevo_df[col])
                        val[ap[-2]] = [ap[-1]]
                    
                    nuevo_df = pd.DataFrame(val)
            except:
                print('algun error con el unnamed 2')
                    
        return nuevo_df
    
    @staticmethod
    def borrar_col(df):
        df = df.reset_index(drop=True)
        na = pd.isna(df)
        ncolum = []
        for i in na:
            if False in na[i].values:
                ncolum.append(i)
        borrar_col = [nombre for nombre in list(df.columns) if nombre not in ncolum]
        nuevo_df = df.drop(borrar_col, axis=1)
        # nuevo_df = nuevo_df.drop([1], axis=0)
        nuevo_df = nuevo_df.reset_index(drop=True)
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


