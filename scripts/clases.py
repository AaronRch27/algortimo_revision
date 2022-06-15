# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 21:43:11 2022

@author: AARON.RAMIREZ
"""
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
import joblib
import nltk

def tokenizar(texto):
    puntuacion = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~¿¡'
    tokens = nltk.word_tokenize(texto,"spanish")
    for i,token in enumerate(tokens):
        tokens[i] = token.strip(puntuacion)
    texto = " ".join(tokens)
    tokens = nltk.word_tokenize(texto,"spanish")
    return tokens

class clasificadorBayes():
    
    def fit(self,train):
        self.train = train
        frecuencia_clases = train.groupby(["class"]).size()
        self.apriori = frecuencia_clases/len(train)
        X = train.drop(columns=["class"])
        self.clases = self.apriori.index.values
        frecuencia_caracteristicas = train.groupby(["class"]).sum()+1
        total_clases = frecuencia_caracteristicas.sum(axis=1)
        self.presunciones = frecuencia_caracteristicas.div(total_clases,axis=0)
        self.log_presunciones = np.log(self.presunciones)
    
    def predict(self,X):
        salida = []
        for i,evento in X.iterrows():
            logprob_clases = {clase: np.log(self.apriori[clase]) for clase in self.clases}
            sum_log = self.log_presunciones.dot(evento)
            for clase in self.clases:
                logprob_clases[clase] += sum_log.loc[clase]
            
            etiqueta = max(logprob_clases, key=logprob_clases.get)
            salida.append(etiqueta)
        return salida


datos = pd.read_csv('clas_instrucciones.csv')
# nl = [] #para hacer primer filtro
# for dato in datos['clase']:
#     if dato == 'nada':
#         nl.append('nada')
#     else:
#         nl.append('importa')
# datos['claseB'] = nl
datos = datos.loc[datos['clase']!='nada']
datos.loc[datos.clase == 'mayor'] = 'comparar'
datos.loc[datos.clase == 'menor'] = 'comparar'
datos.loc[datos.clase == 'igual'] = 'comparar'

instrucciones = datos['instruccion'].tolist()
clases = datos['clase'].tolist()


vectorizador = CountVectorizer(input="content",analyzer="word",tokenizer=tokenizar,ngram_range=(2, 2))
matriz_frecuencias = vectorizador.fit_transform(instrucciones)

vocabulario = vectorizador.get_feature_names()
data = pd.DataFrame(matriz_frecuencias.toarray(),index=instrucciones)


data["class"] = clases


train_temas, test_temas = train_test_split(data,test_size=0.2,random_state=0)


clasificador = clasificadorBayes()
clasificador.fit(train_temas)

X = test_temas.drop(columns=["class"])
y_true = list(test_temas["class"])
y_pred = clasificador.predict(X)
print(metrics.confusion_matrix(y_true,y_pred))

print("Exactitud:\t\t",metrics.accuracy_score(y_true,y_pred))
print("F1-score (micro):\t",metrics.f1_score(y_true,y_pred,average="micro"))
print("F1-score (macro):\t",metrics.f1_score(y_true,y_pred,average="macro"))
print("F1-score (ponderado):\t",metrics.f1_score(y_true,y_pred,average="weighted"))


#proceso fundamenta para analizar nuevos datos
vectorizador_fit = vectorizador.fit(instrucciones)
new = ['Para cada tipo de procedimiento, los datos registrados deben ser consistentes con la información reportada como respuesta en la pregunta anterior.']
matriz = vectorizador_fit.transform(new)
data1 = pd.DataFrame(matriz.toarray(),index=new)
res = clasificador.predict(data1)
print(res)

#guardar modelo
save = 'modelo_segundo_filtro.sav'
el_fit = 'vectorizador_fil2.sav'
joblib.dump(clasificador,save)
joblib.dump(vectorizador_fit,el_fit)
