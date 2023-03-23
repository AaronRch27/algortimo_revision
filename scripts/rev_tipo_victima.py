# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 10:25:45 2022

@author: AARON.RAMIREZ
"""

import pandas as pd



archivo = pd.read_excel('delitos.xlsx',
                        sheet_name='Hoja1')

referente = pd.read_csv('tipo_victima.csv')
col_nom = list(referente.columns)


#buscar columnas


sa = pd.isna(archivo)
listas = sa.to_numpy().tolist()
cont = 0
entot = {'fila':[],'columna':[]}
total_cords = []
for lista in listas:
    vo = 0
    for elm in lista:
        if False == elm:
            total_cords.append((cont,vo))
            entot['fila'].append(cont)
            entot['columna'].append(vo)          
        else:
            pass
        vo+=1
    cont+=1




def buscar_palabra(df,palabra):
    sa = df.fillna('')
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

test = buscar_palabra(archivo, 'Hombres')

cordenada_hombres = test[0]

filtro = [tu for tu in total_cords if tu[0]<=cordenada_hombres[0] and tu[1]>=cordenada_hombres[1]] 
lista_columnas = [tu[1] for tu in filtro]
columnas = list(set(lista_columnas))  
if len(columnas) == len(col_nom)-1:
    print('se puede comparar')

cod = referente['codigo'].values
nfr = pd.DataFrame(cod,columns=['codigo'])

h = 0
for nom in col_nom[1:]:
    cont = archivo.iloc[cordenada_hombres[0]+1:cordenada_hombres[0]+165,
                            [columnas[h]]].values
    nfr[nom] = cont
    h +=1 
    
    
nfr = nfr.fillna('blanco')
if nfr.isin(['blanco']).any().any():
    print('error de blancos')

#Iterar para comparar cada uno de los elementos bajo criterios especificados
#nfr no tiene columna de totales y la primera es código, el resto son las columnas a comparar
errores = []
er_col = {}
for col in nfr[1:]:
    fila = 0
    er_nc = []
    for val in nfr[col]:
        if referente[col][fila] == 1:
            if type(val) == int:
                if val < 0:
                    errores.append(referente['codigo'][fila])
                    er_nc.append(referente['codigo'][fila])
            if type(val) == str:
                if val != 'NS':
                    errores.append(referente['codigo'][fila])
                    er_nc.append(referente['codigo'][fila])
        if referente[col][fila] == 0:
            if type(val) == int:
                if val > 0:
                    errores.append(referente['codigo'][fila])
                    er_nc.append(referente['codigo'][fila])
            if type(val) ==str:
                if val !='0': #aquí se agregaría el NA si aplica
                    errores.append(referente['codigo'][fila])
                    er_nc.append(referente['codigo'][fila])
        fila += 1
    if er_nc:
        er_col[col] = er_nc
        
    