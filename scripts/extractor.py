# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 13:49:40 2021

@author: AARON.RAMIREZ
"""
import pandas as pd
import string
import os

class Extractor():
    
    def __init__(self):
        
        self.contenido = []
        self.anexo = []
    
    def extraer(self,lista):
        self.anexo += lista
        
    def reiniciar(self):
        self.contenido = []
        self.anexo = []
    
    def juntar(self):
        self.contenido += self.anexo
        a = [] + self.contenido
        self.contenido = []
        self.anexo = []
        return a

class Datos():

    def __init__(self,nombre):
        self.nombre = nombre
        self.db = {
            'seccion':[],
            'pregunta':[],
            'coordenada':[],
            'ID':[],
            'tipo':[],
            'comparacion':[],
            'operacion':[]
            }
        self.dataframe = []
    
    def columna_vacia(self,nombre):
        self.db[nombre] = []
    
    def columna_convalor(self,lista,nombre_columna):
        self.db[nombre_columna] = lista

    def agregar_valor_acolumna(self,valor,nombre_columna):
        self.db[nombre_columna].append(valor)
    
    def ajustar_db(self):
        self.db = ajustar(self.db)
    
    def conjuntar_db(self):
        self.db = conjuntar(self.db)
        
    def crear_df(self):
        di = ajustar(self.db)
        try:
            self.dataframe = pd.DataFrame(di,)
            self.dataframe['ID'] = self.dataframe['seccion'].astype(str)+self.dataframe['pregunta'].astype(str)
        except:
            print('Hay un problema con el diccionario para crear la base de datos')
        return self.dataframe        
    
    def guardar(self):
        if type(self.dataframe) != list:
            if not os.path.isfile(self.nombre+'.csv'):
                self.dataframe.to_csv(self.nombre+'.csv',index=False)
            else:
                a = os.path.isfile(self.nombre+'.csv')
                c = 0
                while a:
                    c += 1
                    a = os.path.isfile(self.nombre+str(c)+'.csv')
                self.dataframe.to_csv(self.nombre+str(c)+'.csv',index=False)
                    
            print('frame guardado correctamente')
        else:
            print('no se guardó porque no hay dataframe')
    
        
def ajustar(diccionario):
    "Agregar ceros a elementos que no tienen nada para poder hacer dataframe sin problema"
    revisar = []
    for key in diccionario:
        revisar.append(len(diccionario[key]))
    variacion = list(set(revisar))
    
    if len(variacion) > 1:
        mayor = max(revisar)
        for key in diccionario:
            if len(diccionario[key]) != mayor:
                faltantes = mayor - len(diccionario[key])
                for valor in range(faltantes):
                    diccionario[key].append(0)
        return diccionario
    
    if len(variacion) <= 1:
        return diccionario

def conjuntar(diccionario):
    "agrupar elementos sobrantes de coordenada en diccionario"
    
    if len(diccionario['coordenada']) > len(diccionario['pregunta']):      
        nel = ''
        c = 0
        for ele in diccionario['coordenada'][len(diccionario['pregunta'])-1:]:
            if c == 0:
                nel += ele 
            else:
                if ',' in ele[0]:
                    nel += ele
                else:
                    nel += ','+ele
            diccionario['coordenada'].remove(ele)
            c += 1
        nel = orden(nel)
        
        diccionario['coordenada'].append(nel)
    return diccionario

def orden(cadena):
    "Ordenar la lista de acuerdo a criterio de excel"
    lista = cadena.split(',')
    lista = list(set(lista))
    lista.sort(key=criterio)
    a = ','.join(lista)
    
    return a
    

def criterio(cadena):
    abc = list(string.ascii_uppercase)+['AA','AB','AC','AD']
    numero = []
    letra = []
    for i in cadena:
        if i.isdigit():
            numero.append(i)
        else:
            letra.append(i)

    val_l = 0
    le = ''
    
    for i in letra:
        le += i
    for l in abc:
        val_l += 1
        if l == le:
            break
        
    n = ''
    for ni in numero:
        n += ni
    val_n = int(n)*40
    
    return val_n+val_l

# alfa = Datos('perez')
# alfa.agregar_valor_acolumna(5,'pregunta')
# alfa.columna_convalor(['jo',5,4,6], 'prueba')
# alfa.columna_vacia('vacia')
# t = alfa.crear_db()
# alfa.guardar()
