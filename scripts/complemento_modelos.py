# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 15:45:12 2022

@author: ASUS
"""
import numpy as np
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