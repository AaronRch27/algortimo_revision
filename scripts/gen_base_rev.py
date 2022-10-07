# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 12:33:15 2022

@author: AARON.RAMIREZ
"""

import pandas as pd
import tkinter as tk
from tkinter import IntVar, StringVar, messagebox, Checkbutton

#se hará una app para guiar el proceso de validaciones necesarias para cada pregunta
class aplicacion(tk.Frame):
    def __init__(self,base,cues,master=None):
        super().__init__(master)
        self.master = master
        self.master.title('Prueba')
        self.master.geometry('900x600')
        self.pack() 
        self.cues = cues
        self.lista, self.base = self.consg_p(cues,base)
        self.cont = 0
        self.rec(self.lista[self.cont])
        
        
    @staticmethod
    def consg_p(c,base):
        "c es cuesitonario"
        r = []
        for seccion in c:
            ll = [str(i) for i in list(c[seccion])]
            r += ll
        for k in base:
            base[k] = ['P' for p in range(len(r))]
        base['preguntas'] = r
        df = pd.DataFrame(base)
        df.to_csv('veamos.csv')
        print(r,list(df['preguntas']))
        #al hacer el save queda mal la columna de preguntas porque no es string, puede solucionarse agregando algo y borrandolo al leerlo
        return r, base
        
    def rec(self,pregunta):
        br = self.pack_slaves()#limpiar interfaz
        for val in br:
            val.destroy()
        #variables control
        self.blanco = IntVar() #bool cero o uno
        self.arit = IntVar() #bool cero o uno
        self.sum_n = IntVar() #bool cero o uno
        self.espec = IntVar() #bool cero o uno será? el algoritmo ya detecta esto...
        self.registro = IntVar() #bool cero o uno. donde hay columnas que no se responden con numeros, como ids y eso
        self.salto = IntVar() #bool cero o uno
        self.p_rel1 = IntVar() #bool cero o uno
        self.p_relcol = StringVar() #bool cero o uno
        
        l1 = tk.Label(self, text=f"Selecciona las validaciones que aplican para pregunta {pregunta}")
        l1.pack()
        #apartado de validacion checkbox
        v1 = Checkbutton(self,
                          text = 'Blanco', variable= self.blanco,
                          onvalue = 1, offvalue = 0,
                          )
        v2 = Checkbutton(self,
                          text = 'Artmético', variable=self.arit,
                          onvalue = 1, offvalue = 0,
                          )
        v3 = Checkbutton(self,
                          text = 'Suma_numerales', variable=self.sum_n,
                          onvalue = 1, offvalue = 0,
                          )
        v4 = Checkbutton(self,
                          text = 'Especifique', variable=self.espec,
                          onvalue = 1, offvalue = 0,
                          )
        v5 = Checkbutton(self,
                          text = 'Registro', variable=self.registro,
                          onvalue = 1, offvalue = 0,
                          )
        v6 = Checkbutton(self,
                          text = 'Salto de preguntas', variable=self.salto,
                          onvalue = 1, offvalue = 0,
                          )
        v7 = Checkbutton(self,
                          text = 'Pregunta relacionada', variable=self.p_rel1,
                          onvalue = 1, offvalue = 0,
                          )
        v1.pack()
        v2.pack()
        v3.pack()
        v4.pack()
        v5.pack()
        v6.pack()
        v7.pack()
        
        
        #botones de navegacion
        if self.cont == 0:
            boton1 = tk.Button(self, text ="Siguiente", command = self.nex)
            boton1.pack()
        if self.cont > 0 and self.cont < len(self.lista)-1:
            boton1 = tk.Button(self, text ="Siguiente", command = self.nex)
            boton1.pack()
            boton2 = tk.Button(self, text ="Anterior", command = self.prev)
            boton2.pack()
        if self.cont == len(self.lista)-1:
            boton2 = tk.Button(self, text ="Anterior", command = self.prev)
            boton2.pack()
            boton3 = tk.Button(self, text ="Guardar", command = self.guarda)
            boton3.pack()
        
        
        # be = tk.Button(self, text ="Salir", command = self.destroy)
        # be.pack()
    
    def guarda(self):
        messagebox.showinfo(
            message = 'Todavía no hago nada',
            title = 'Guardado'
            )
        
    def nex(self):
        #almacenar validaciones en base
        
        #cambiar pregunta
        self.cont += 1
        if self.cont > len(self.lista)-1:
            self.cont = 0
        self.rec(self.lista[self.cont])
    
    def prev(self):
        self.cont -= 1
        self.rec(self.lista[self.cont])
        
        
    
    
def recibir(cuestionario,libro):
    """
    

    Parameters
    ----------
    cuestionario : un diccionario con los objeto pregunta organizados por
    sección
    libro : str nombre del archivo que está siendo leído

    Returns
    -------
    None.

    """
    base = {'preguntas':[],'blanco':[],'aritmetico':[],'suma_numeral':[],
            'espeficique':[],'errores_registro':[],'salto_preguntas':[],
            'preguntas_relacionadas':[]
            }
    #primer paso es conseguir lista con nombres de preguntas
    # lista_preguntas = consg_p(cuestionario)
    # base['preguntas'] = lista_preguntas
    ventana = tk.Tk()
    clase = aplicacion(base,cuestionario,master=ventana)
    clase.mainloop()
    
    return


    