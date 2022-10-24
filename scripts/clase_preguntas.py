# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 14:29:53 2022

@author: AARON.RAMIREZ
"""
import pandas as pd
import numpy as np
import joblib
import traceback
#Los modelos se deben cargar desde el main
# modelo1 = joblib.load('modelo_primer_filtro.sav')

# vector1 = joblib.load('vectorizador_fil.sav')

# modelo2 = joblib.load('modelo_segundo_filtro.sav')

# vector2 = joblib.load('vectorizador_fil2.sav')

class clase_pregunta():
   
    def __init__(self,dataframe,seccion,modelos):
        self.nombre_lit = dataframe.iat[0,0]
        self.pregunta = dataframe.iat[0,1]
        borrar = '- ' #solia remover el punto también pero entocnes hay preguntas con el mismo nombre como 1.11 y 11.1
        bnom = ''.join(c for c in self.nombre_lit if c not in borrar)
        self.nombre = bnom[:-1] #para quitar el ultimo punto nada más
        self.dfraw = dataframe
        self.tablas = clase_pregunta.tablas(self,dataframe)
        self.metadata = clase_pregunta.meta(self,dataframe,modelos)
        # self.tipo_T = 'Desconocido'
        # self.instr = clase_pregunta.clas_instru(instrucciones)
        # self.tipo_pregunta = clase_pregunta.clas_tipo() #inserte funcion con modelo de clasificacion de tipos de pregunta
        self.seccion = seccion
       
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
        self.tipo_T = 'Desconocido'
        for valor in df[nombres_iniciales[2]]: #equivalente a unnamed 2 
            
            for v in bs:
                try:
                    if v in valor:
                        cortar.append(fila)
                except: #excepcion por valores nan
                    pass
            fila += 1
           
        if not cortar: #comprobación adicional por si lollegaron a escribir en la columna B
            fila = 0
            for valor in df[nombres_iniciales[1]]: #equivalente a unnamed 1 
                
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
            comentario = 0
            fila = 0
            for val in df[nombres_iniciales[2]]:#busqueda para depurar los que puedan estar en el comentario del informante
                try:#no se puede comparar con nan
                    if 'En caso de tener algún' in val:
                        comentario = fila
                        break
                except:
                    pass
                fila += 1
            cortar = [corta for corta in cortar if corta < comentario]    
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
    
    def meta(self,df,M):
        """
        M es modelos
        Esta función es para generar los metadatos de la pregunta:
            instrucciones
            instrucciones clasificadas por el modelo
            comentarios de la pregunta (hechos por el informante)
            datos de especifique (si es que los hay)
            
        Regresa un diccionario con esos metadatos, aunque define en el
        proceso las propuedades del objeto pregunta con los mismos datos

        """
        ndf  = df.fillna('blanco')
        nombres = list(df.columns)
        texto = list(ndf[nombres[2]])
        res = {}
        c = 0
        for val in texto:
            if 'En caso de tener algún comentario' in str(val):
                try:
                    self.comentario = texto[c+1]
                    if texto[c+1] == 'blanco':
                        self.comentario = 'Sin comentario'
                except:
                    self.comentario = 'Sin comentario'
                res['comentario'] = self.comentario
            c += 1
        
        instrucciones = []    
        c = 0    
        for val in texto:
            if c > 0:
                if val == 'blanco':
                    break
                else:
                    instrucciones.append(val)
            c += 1
        self.instrucciones = instrucciones
        res['instrucciones'] = instrucciones
        inss = {}
        #clasificar instrucciones
        matriz = M[1].transform(instrucciones)
        data = pd.DataFrame(matriz.toarray(),index=instrucciones)
        primer = M[0].predict(data)
        seginstr = []
        c = 0 
        
        for i in primer:#filtrar las instrucciones evaludas de a cuerdo a especifique o a consistencia
            if i != 'nada':
                seginstr.append(instrucciones[c])
                inss[instrucciones[c]] = i
                # if i in inss:
                #     inss[i].append(instrucciones[c])
                # else:
                #     inss[i] = instrucciones[c]
            c+=1
        
        # matriz1 = M[3].transform(seginstr)
        # data = pd.DataFrame(matriz1.toarray(),index=seginstr)
        # segundo = M[2].predict(data)
        
        # c = 0
        # for i in segundo:
        #     inss[i] = seginstr[c]
        #     c += 1
        self.instruccio_clasificadas = inss
        res['instruc_clasificadas'] = self.instruccio_clasificadas
        
        #buscar los especifuque
        candidatos = []
        c = 0
        for val in texto:
            if '(especifique' in str(val):
                candidatos.append(c)
                
            c +=1 
        espe = 'No hay elementos a especificar'
        
        if candidatos:
            espe = {}
        for candidato in candidatos:
            fila = list(ndf.iloc[candidato])
            
            for fi in fila[3:]:#para iniciar después de la columna unnamed 2
                if fi != 'blanco':
                    espe[fila[2]] = fi
                    break
        self.especifique = espe
        res['especifique'] = espe           
        
        # print(texto,instrucciones)
        return res
        
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
        df = clase_pregunta.borrar_S(self,df)
        try:
            self.autosuma
        except:#esta excepcion es porque aveces no se genera el atributo autosuma en borrarS
            self.autosuma = 'No'
        self.encabezado_tabla = []
        medidas = df.shape
        # print(medidas)
        if medidas[0] < 25: #identificar preguntas si no no se sabe tomando en cuenta que suelen ser pequeñas en cantidad de filas <10
            probar = clase_pregunta.sino(df)  
            
            if probar:
                return probar
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
            nuevo_df = clase_pregunta.transformar_tabla(nuevo_df,self)
            self.tipo_T = 'Tabla'
            #comoprobar si es tabla de delitos
            columns = list(nuevo_df.columns)
            nc = []

            saca = [' ','\n']
            for val in columns:
                nc.append(''.join(v for v in str(val) if v not in saca))#quitar espacios
                
            if 'Tipodedelito' in nc and 'Código' in nc:
                self.tipo_T = 'Tabla_delitos'
        else: #para los que no son tablas
            nuevo_df = clase_pregunta.transformar_notab(nuevo_df,mayor,self)
                
        return nuevo_df
   
    @staticmethod
    def sino(df1):
        "identificar preguntas de si, no, no se sabe"
        #buscar los tres terminos en el frame
        df = df1.fillna(' ')
        b = 0
        palabras = ['Sí','No', 'No se'] #identificadores
        contador_columna = 0
        for palabra in palabras:
            c = 0 + contador_columna #variable para control de columna en la que se va iterando, ya que no se busca repetir la iteracion desde la primer columna luego de encontrar alguna palabra
            for col in df.iloc[:,contador_columna:]: #iterar columnas desde donde se encontró la última palabra o desde cero
                
                a = 0 #variable solo para poner el break si pasa lo de abajo
                for valor in df[col].values:
                    
                    if palabra in str(valor):
                        contador_columna = c + 1 #Mas uno para iniciar desde siguiente columna
                        a = 1
                        b += 1
                        
                        break
                if a == 1:
                    
                    break
                c += 1
        if b != 3:
            return [] #regresa lista vacía para que se pueda terminar el ciclo con un condicional en la funcion tabla
        
        if b == 3: #se trata de la pregunta que se está buscando
            b1 = 0
            cord = 0
            palabras = ['X','x'] #identificadores
            for palabra in palabras:
                c = 0
                for col in df:
                    fila = 0
                    for valor in df[col].values:
                        try: #por nan se hace esta excepcion, no se puede comparar string con nan
                            if palabra == valor:
                                cord = (fila,c)
                                b1 += 1        
                        except:
                            pass
                        fila += 1
                    c += 1
                    
            # respuesta = 0 #no debería ser necesario definirla previamente, si surge error aquí es por algo con b1
            
            if b1 == 0:
                respuesta = 'No se respondió la pregunta'
            if b1 > 1:
                respuesta = 'Error, se respondió más de una opción'
            if b1 == 1:
                #se extrae el valor de la respuesta donde se escribió X
                nom = list(df.columns)
                
                respuesta = df[nom[cord[1]+1]][cord[0]]
            
            return respuesta
        
    @staticmethod
    def transformar_notab(df,mayor,self):
        previo_comentario = clase_pregunta.buscarpalabra('En caso de tener algún comentario', df)#fila previa al comentario de la pregunta si es que lo tiene o no, más bien es el lugar donde va el comentario
        especifique = clase_pregunta.buscarpalabra('especifique', df) 
        # ndf = df.iloc[:previo_comentario[0][0],:]
        
        if especifique:
            previo_comentario = [especifique[-1]]+previo_comentario
        
        colyfil = clase_pregunta.imagen(df)
        espacios = clase_pregunta.distancia(colyfil['fila'],1)
        c_espacios = espacios + [] #crear una copia para modificarla
        # print(ndf,espacios,previo_comentario)
        # print(espacios,df)
        for espacio in espacios:#sacar los espacios que no sirven, aunque 
            if espacio > previo_comentario[0][0]:
                c_espacios.remove(espacio)
          
        inf =  [i for i in range(0,colyfil['fila'][c_espacios[0]]+2)]
        sup = [i for i in range(colyfil['fila'][c_espacios[-1]]+1,len(df['Unnamed: 2'].values))]
        nuevo_df = df.drop(inf+sup, axis=0)
        nuevo_df = clase_pregunta.borrar_col(nuevo_df)
        forma = nuevo_df.shape
        #porque se pasa el frame en preguntas donde hay glosarios de nuevas subsecciones o apartados de especifique
        
        # previo_comentario = clase_pregunta.buscarpalabra('En caso de tener algún comentario', nuevo_df)
        # if previo_comentario:
        #     nuevo_df = nuevo_df.iloc[:previo_comentario[0][0],:]
        # especifique = clase_pregunta.buscarpalabra('especifique', nuevo_df)    
        # print(especifique,previo_comentario,nuevo_df)
        # if especifique:
        #     especifique = [especifique[-1]]
        #     print('si',especifique, nuevo_df.shape)
        #     nuevo_df = nuevo_df.iloc[:especifique[0][0]-1,:]
        #     print(nuevo_df)
        # desde la linea anterior hasta el inicio de esta función, lo que se hace es un recorte de la pregunta, dejando fuera la parte de los comentarios, instrucciones, y numero de pregunta, con tal de quedarse con solo los datos que ella contiene
        #Para comenzar con la reestructuración de la prgeunta, un conteo de niveles de desagregados
        self.tipo_T = 'No Tabla'
        if forma[1] > 2 and len(c_espacios) > 2: #Esto solo aplicará para las preguntas que tienen desagregados
            self.tipo_T = 'NT_Desagregados'
            self.T_tip = 'desagregados'
            nuevo_df = nuevo_df.fillna('    ')#cuatro espacios
            #rellenar espacios en blanco
            #para ello borrar columnas y filas que tienen nada
            borrar = []
            for col in nuevo_df:
                check = list(nuevo_df[col])
                unicos = list(set(check))
                # print(unicos)
                if len(unicos) == 1:
                    borrar.append(col)
            if borrar:
                nuevo_df = nuevo_df.drop(borrar, axis=1, inplace=True)
            #ahora lo mismo pero por filas
            
            borrar = []
            for fila in range(nuevo_df.shape[0]):
                ff = list(nuevo_df.iloc[fila,:])
                unicos = list(set(ff))

                if len(unicos) == 1:
                    borrar.append(fila)
            
            nuevo_df = nuevo_df.drop(borrar, axis=0)
            nuevo_df = nuevo_df.reset_index(drop=True)
            
            fila = 0
            for f in list(nuevo_df.iloc[:,0]):
                filal = list(nuevo_df.iloc[fila,:])
                #por fila se hará la comprobación. 

                columna = 0
                for v in filal:
                    print(len(filal),filal)
                    if v != '    ':
                        romper = False
                        if len(filal[:columna]) > 2:#para que no haga cosas en las primeras columnas ya que ahí van los valores en blanco
                        
                            for m in filal[:columna]:
                                if m != '    ':#si un valor no e sen blanco romper
                                    romper = True
                                    

                                    
                        if not romper and columna > 1:
                            r = columna - 2
                            
                            if nuevo_df.iloc[fila,r] == '    ':#ultima rectificación de que no se va alterar un valor que no es blanco
                                # print('romper',nuevo_df.iloc[fila,r],filal,columna)
                                nuevo_df.iloc[fila,r] = 'BO'
                             
                        # if columna-3 >= 0:
                        #     if filal[columna - 3] == '    ':
                                
                        #         nuevo_df.iloc[fila,columna-3] = 999999999 #bo va a ser el valor de espacios vacios en este tipo de preguntas
                               
                    columna += 1

                fila += 1
             
            
            nfram = {}
            nombres_c = list(nuevo_df.columns)
            col = 0
            for columna in nombres_c:
                c = 0
                for valor in nuevo_df[columna]:
                    if type(valor) == int or type(valor) == float:
                        nfram[nuevo_df[nombres_c[col+2]][c]] = [valor]
                        try:
                            lista = list(nuevo_df[nombres_c[col+2+1]][c+1:])
                            lista2 = list(nuevo_df[nombres_c[col+2]][c+1:])
                            
                            c1 = 0
                            for i in lista2:
                                if type(i) == str and len(i) > 4:
                                    break
                                c1 += 1
                            lista = lista[0:c1]
                            anexar = []
                            c2 = 1
                            for otrov in lista:
                                if otrov != '    ':
                                    anexar.append(nuevo_df[nombres_c[col+1]][c+c2])
                                    # nfram[nuevo_df[nombres_c[col+2]][c]].insert(0, nuevo_df[nombres_c[col+1]][c+c2])
                                c2 += 1
                            nfram[nuevo_df[nombres_c[col+2]][c]] = anexar + nfram[nuevo_df[nombres_c[col+2]][c]] #esto es para dejar el total hasta abajo de la columna
                        except:
                            pass
                        
                    if type(valor) == str and len(valor) < 3: #por esta condicion se necesitan los 4 espacios. Esto es para no dejar fuera los NA o NS
                        nfram[nuevo_df[nombres_c[col+2]][c]] = [valor]
                        try:
                            lista = list(nuevo_df[nombres_c[col+2+1]][c+1:])
                            lista2 = list(nuevo_df[nombres_c[col+2]][c+1:])
                            
                            c1 = 0
                            for i in lista2:
                                if type(i) == str and len(i) > 4:
                                    break
                                c1 += 1
                            lista = lista[0:c1]
                            anexar = []
                            c2 = 1
                            for otrov in lista:
                                if otrov != '    ':
                                    anexar.append(nuevo_df[nombres_c[col+1]][c+c2])
                                c2 += 1
                            nfram[nuevo_df[nombres_c[col+2]][c]] = anexar + nfram[nuevo_df[nombres_c[col+2]][c]] #esto es para dejar el total hasta abajo de la columna
                        except:
                            pass
                    else:
                        pass
                    c += 1
                col += 1
            #Lo que se hace a continuación es rellenar las listas del diccionario con nan para poder crear un dataframe
            ext = [len(nfram[key]) for key in nfram]
            parana = max(ext)
            if parana > 2:
                self.autosuma = 'Si'
            for key in nfram:
                numerona = parana - len(nfram[key])
                for i in range(numerona):
                    nfram[key].append(np.nan)
            nuevo_df = pd.DataFrame(nfram)
            return nuevo_df
        if forma[1] == 2 and len(c_espacios) > 1: #para pregutas con solo una columna de desagregados
            self.tipo_T = 'NT_Desagregados'
            self.T_tip = 'desagregados'
            nuevo_df = nuevo_df.fillna('    ')
            nuevo_df = nuevo_df.reset_index(drop=True)
            borrar = []
            c = 0
            for fila in nuevo_df.iloc[:,0]:
                lis = list(nuevo_df.iloc[c,:])
                vac = []
                for val in lis:
                    if val == '    ':
                        vac.append(val)
                if len(vac) == len(lis):
                    borrar.append(c)
                c += 1
            if borrar:
                nuevo_df = nuevo_df.drop(borrar,axis=0)
                nuevo_df = nuevo_df.reset_index(drop=True)
            #convertir a nombres de columnas los que están en columa 1 y pasar columna cero a fila
            ncols = {}
            c = 0
            for val in nuevo_df.iloc[:,1]:
                ncols[val] = nuevo_df.iloc[c,0]
                c += 1
            nuevo_df = pd.DataFrame(ncols,index=[0])
            
        return nuevo_df
    
    @staticmethod
    def transformar_tabla(nuevo_df,self):
        # nombres_iniciales = list(nuevo_df.columns)
        # print(nombres_iniciales)
        medida = nuevo_df.shape
        if medida[0] > 2000: #para borrar fila de total que está debajo de los encabezados de la tabla, porque eso genera errores de lectura
            c = 0
            nuevo_df = nuevo_df.reset_index(drop=True)
            for fila in list(nuevo_df.iloc[:,2]):#iterar columna C
                if 'Total' == fila:
                    nuevo_df = nuevo_df.drop([c])
                    # print('borró fila ',c)
                    nuevo_df = nuevo_df.reset_index(drop=True)
                    break
                c += 1
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
        # nombres_iniciales = list(nuevo_df.columns)
        # print(nombres_iniciales)
        
        nuevo_df = clase_pregunta.borrar_col(nuevo_df)
        # nombres_iniciales = list(nuevo_df.columns)
        # print(nombres_iniciales)
        #Encontrar numeral para determinar si es tabla con varias filas o de fila única y perfilar los nombres de columnas
        bus = ['1.', '1. ', '01.', '01. ','1','01.01']
        comprobador = []
        val = {}
        # print('por encontrar', list(nuevo_df['Unnamed: 2']))
        for uno in bus:
            
            if comprobador: #no tiene caso que se siga iterando si ya lo encontró
                break
            # print(nuevo_df.columns)
            Revisar = 0
            for val11 in list(nuevo_df['Unnamed: 2']):
                if type(val11) == str:
                    if val11.startswith(uno):
                        Revisar = 1
            # print(Revisar)
            if uno in list(nuevo_df['Unnamed: 2']) or Revisar == 1: #nombres iniciales [2] es una referencia a la columna unnamed 2, pero ésta aveces cambia de nombre porque se borra cuando hay una mala lectura de la tabla
                self.T_tip = 'index'
                comprobador.append(1)
                c = 0
                index = 0
                for fila in nuevo_df['Unnamed: 2'].values:
                    if str(uno) in str(fila):
                        index = c
                        break
                    c += 1
                nuevo_df = nuevo_df.fillna('borra')
                nombres = []
                cn = 0
                self.encabezado_tabla = nuevo_df.iloc[0:index,:]
                for col in nuevo_df:
                    #aqui se mete el proceso para los nombres de columnas
                    ap = list(nuevo_df[col])
                    nombres = ap[:index]
                    if 'borra' in nombres:
                        veces = nombres.count('borra')
                        for vez in range(veces):
                            nombres.remove('borra')
                    if nombres:
                        nombre = str(nombres[-1])
                    if nombre in val:
                        while True:
                            if nombre in val:
                                nombre += '1'
                            if nombre not in val:
                                break
                    if not nombres: #si el nombre generado ya está en el diccionario, hay que unir ambas columnas
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
                    cn += 1
                if 'Código1' in val:
                    val.pop('Código1') #borrar porque esta columna es un error
                nuevo_df = pd.DataFrame(val)
        # print(comprobador,'com')        
        if not comprobador: #tabla de filas unicas
            # print('hastaqui bien')
            self.T_tip = 'unifila'
            nuevo_df = nuevo_df.fillna('borra')
            self.encabezado_tabla = nuevo_df.iloc[:-1,:]
            nombres = []
            fila_resp = list(nuevo_df.iloc[-1,:])
            vacia = True #comprobador de si la tabla está vacia
            for vl in fila_resp:
                if type(vl) == str:
                    comp = ['NS','NA','X']
                    vv = vl.upper()
                    if vv in comp:
                        vacia = False
                if type(vl) == int or type(vl) == float:
                    vacia = False
            for col in nuevo_df:
                ap = list(nuevo_df[col])
                
                if len(ap) == 1:#para tablas vacias
                    ap.append('borra')
                nombres = ap[:-1]
                if 'borra' in nombres:
                    veces = nombres.count('borra')
                    for vez in range(veces):
                        nombres.remove('borra')
                if nombres:
                    nombre = str(nombres[-1])
                if not nombres:
                    nombre = ap[0]
                if nombre in val:
                    while True:
                        if nombre in val:
                            nombre += '1'
                        if nombre not in val:
                            break
                # print(nombre,nombres)
                # if nombre in val or condicion == 'juntar': #si el nombre generado ya está en el diccionario, hay que unir ambas columnas
                #     ind = 0
                #     nl = []
                #     for elem in val[nombre]:
                #         nl.append(str(elem) + ' '+ str(ap[index:][ind]))
                #         ind += 1
                #     val[nombre] = nl
                if nombre not in val:
                    if not vacia:
                        val[nombre] = [ap[-1]]
                    if vacia:
                        val[nombre] = ['borra']
            if 'Código1' in val:
                val.pop('Código1') #borrar porque esta columna es un error
            nuevo_df = pd.DataFrame(val)    
        return nuevo_df
    
    @staticmethod
    def borrar_S(self,df):
        "Borrar la letra S de autosumas en columnas y la palabra Complemento"
        S = clase_pregunta.busqueda_exacta(df, 'S')
        complemento = clase_pregunta.buscarpalabra('Complemento', df)
        if not S and not complemento:
            self.autosuma = 'No'
            return df
        if S:
            self.autosuma = 'Si'
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
        df = df.reset_index(drop=True)
        partes = clase_pregunta.buscarpalabra('(1 de ', df)
        
        if not partes:
            return df
        colyfil = clase_pregunta.imagen(df)
        espacios = clase_pregunta.distancia(colyfil['fila'],1)
        #Espacios tendrá más de dos elementos, y se cuenta a partir del segundo, ya que las tablas siguen esa distribución de una fila vacía por salto de parte de tabla
        partes1 = partes[0]
        if len(colyfil['fila'])>500:
            chek = colyfil['fila'][espacios[1]]
            if chek in range(partes1[0],partes1[0]+4):
                espacios.pop(1)
        filas = [colyfil['fila'][s] for s in espacios]
        des_esp_ini = [i for i in filas if i > partes1[0]] #espacios despues del espacio inicial, para detetctar saltos en encabezado de tabla
        for fil in des_esp_ini:
            if fil < partes1[0]+3:#una diferencia de tres debido a que no hay tablas que solo tengan 3 filas de longitud y sean tablas por partes
                ind = 0
                for i in filas:
                    if i == fil:
                        break
                    ind += 1
                espacios.pop(ind) #borrar esos espacios extras debido a maal diseño de encabezado de tabla
        
        cant_tablas = df.iat[partes[0][0],partes[0][1]]
        # ver1 = [colyfil['fila'][i] for i in espacios]
        # print(cant_tablas,partes, espacios,ver1)
        can = cant_tablas[-3:-1]
        can = int(can) #siempre tiene que ser 2 o más
        # print(can)
        filas_inicio = [np.nan for i in range(colyfil['fila'][espacios[0]+1])]#[espacios[0]+1]+1)
        # filas_fin = [np.nan for i in range(colyfil['fila'][espacios[1]+1]+1)] #este sirve para cuando estén vacias las columnas en el contenido
        # filas_fin = [np.nan for i in range(colyfil['fila'][espacios[1]+1]+1,colyfil['fila'][-1]+1)]
        # print(len(filas_fin),colyfil['fila'][espacios[1]+1]+1,colyfil['fila'][-1]+1)
        #contruir lista de columnas para el dataframe
        nuevas_columnas = {}
        longitud_tabla = colyfil['fila'][-1]+1-colyfil['fila'][espacios[1]+1]#+1 #la cantidad de filas que tiene la tabla
        llenado = [np.nan for i in range(longitud_tabla)]
        n = 1000
        for tabla in range(1,can):
            filaS = colyfil['fila'][espacios[tabla]]+2 #la fila donde empieza la tabla
            filaSF = colyfil['fila'][espacios[1]+1]#por precision hay que restar con la distancia que tiene el inicio del numeral al inicio del frame
            # print(filaS,filaSF, filaS+filaSF,len(filas_inicio))
            c = 0
            for columna in df:
                ap = list(df[columna])
                # print(len(ap))
                nuevas_columnas[n+c] = filas_inicio + ap[filaS:filaS+filaSF]+llenado
                # print(len(ap[filaS:filaS+filaSF]))
                if n > 0 and len(nuevas_columnas[n+c]) < len(nuevas_columnas[1000]):
                    alfa = len(nuevas_columnas[1000]) - len(nuevas_columnas[n+c])
                    completar = [np.nan for i in range(0,alfa)]
                    nuevas_columnas[n+c] += completar
                #int(str(tabla)+str(c)) lo que iba como indice en nuevas columnas de linea previa
                c += 1
            n += 100
        # print(espacios,colyfil['fila'],aver,partes)
        #eliminar columnas de index
        index = ['1.', '1. ', '01.', '01. ','Código']
        borrar = []
        # print(nuevas_columnas)
        for k in nuevas_columnas:
            c = 0
            for val in nuevas_columnas[k]:
                if val in index:
                    borrar.append(k)
                    nex = nuevas_columnas[k+1]
                    siguiente = list(set(nex[:c]))
                    
                    if len(siguiente) < 2:
                        borrar.append(k+1)
                    break
                c += 1
            if borrar:
                break
        for br in borrar:
            if br  in nuevas_columnas:
                del nuevas_columnas[br]
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
                    if type(elm) == str:
                        x = elm.rstrip('\n')
                        if palabra in x:
                            sad = (cont,vo)
                            entot.append(sad)
                        else:
                            pass
                        vo+=1
                cont+=1
            except:
                traceback.print_exc()
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


