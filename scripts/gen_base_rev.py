# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 12:33:15 2022

@author: AARON.RAMIREZ
"""

import pandas as pd
import tkinter as tk
from tkinter import IntVar, StringVar, messagebox, Checkbutton, ttk

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
            ## se agrega .- a las preguntas para la base, no olvidar quitarlo cuando se use para buscar en  cuestionario!!!!
            ll = [str(i)+'.-' for i in list(c[seccion])]
            r += ll
        for k in base:
            base[k] = ['P' for p in range(len(r))]
        base['preguntas'] = r
        df = pd.DataFrame(base)
        # df.to_csv('veamos.csv')
        # print(r,list(df['preguntas']))
        #al hacer el save queda mal la columna de preguntas porque no es string, puede solucionarse agregando algo y borrandolo al leerlo
        return r, base
    
    @staticmethod    
    def bp(self,pregunta):
        cues = self.cues
        objeto = 0
        for seccion in cues:
            #pregunta con slice de menos dos para quotar el punto y guion agregados para la base
            if pregunta[:-2] in cues[seccion]:
                objeto = cues[seccion][pregunta[:-2]]
                break
        return objeto
    
    def rec(self,pregunta):
        self.n_deprgunta = pregunta #esto se usa sobre todo en relaciones entre preguntas
        br = self.pack_slaves()#limpiar interfaz
        for val in br:
            val.destroy()
        #variables control
        self.blanco = IntVar(self) #bool cero o uno
        self.arit = IntVar(self) #bool cero o uno
        self.sum_n = IntVar(self) #bool cero o uno
        self.espec = IntVar(self) #bool cero o uno será? el algoritmo ya detecta esto...
        self.registro = IntVar(self) #bool cero o uno. donde hay columnas que no se responden con numeros, como ids y eso
        self.salto = IntVar(self) #bool cero o uno
        self.p_rel1 = IntVar(self) #bool cero o uno
        self.p_relcol = StringVar(self) #bool cero o uno
        #despliegue de ventanas con instrucciones y tablas de pregunta
        ob_pre = self.bp(self,pregunta) #objeto pregunta
        #las partes comentadas acontinuacion se deshabilitaron por practicidad en la ejecucion de la aplicacion. Eran lineas para mostrar instrucciones y tablas, pero es incómodo para navegar entre preguntas. 
        # self.NV = tk.Toplevel(self)
        # self.NV.title('Pregunta e instrucciones')
        # self.NV.geometry('800x500')
        # can = tk.Canvas(self.NV, width=800, height = 500,
        #                 scrollregion=(0,0,800,500))
        # can.pack()
        # barra = tk.Scrollbar(can)
        # barra.pack(side=tk.RIGHT, fill=tk.Y)
        
        # # can.config(yscrollcommand = barra.set)
        # ll1 = tk.Label(can, text='Pregunta: '+ob_pre.pregunta,wraplength=450)
        # ll1.pack()
        # instrucciones = tk.Listbox(can, yscrollcommand = barra.set,
        #                            selectmode=tk.EXTENDED)
        # for instruccion in ob_pre.instrucciones:
        #     instrucciones.insert(tk.END,instruccion)
        #     # ll2 = tk.Label(can, text=instruccion,wraplength=650)
        #     # ll2.pack()
        # instrucciones.pack(fill = tk.BOTH, expand=True)
        # barra.config(command=instrucciones.yview)
        # if type(ob_pre.tablas) != str: #hay preguntas que no son tablas y se pasa una string aquí en vez del frame
        #     for tabla in ob_pre.tablas:
        #         self.NV1 = tk.Toplevel(self)
        #         self.NV1.title('Contenido de pregunta')
        #         barra = tk.Scrollbar(self.NV1,orient='horizontal')
        #         barra.pack(side=tk.BOTTOM, fill=tk.X)
        #         tab = tk.Text(self.NV1,xscrollcommand=barra.set,wrap=tk.NONE)#,width=100
        #         tab.insert(tk.INSERT, ob_pre.tablas[tabla].to_string())
        #         barra.config(command=tab.xview)
        #         tab.pack()
                
        #encabezado de ventana con tipos de validacion
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
        #seleccionar botones que se usan casi siempre
        v1.select()
        v2.select()
        
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
            boton3 = tk.Button(self, text ="Guardar", command = self.nex)
            boton3.pack()
        
        
        # be = tk.Button(self, text ="Salir", command = self.destroy)
        # be.pack()
    
    def guarda(self):
        messagebox.showinfo(
            message = 'Todavía no hago nada',
            title = 'Guardado'
            )
        
    def nex(self):
        #comprobar validacion de sumas numerales. Así para que no cambie de pregunta al poner los datos adicionales. Por lo tanto funcion de suma de numerales debe hacer referencia nuevamente a esta función 
        if self.sum_n.get() == 1 and self.base['s_num_lis'][self.cont] =='P':
            self.base['s_num_lis'][self.cont] = []#porque va a ser lista de listas
            #sus variables de control
            self.inicio_suma = StringVar(self)
            self.fin_suma = StringVar(self)
            #la funcion autoreferencial a esta
            self.sumas_de_numerales()
        elif self.p_rel1.get() == 1 and self.base['preg_rel'][self.cont] =='P':
            #variables control
            self.preg_rel_var = []#esta lista es la variable que va a condensar los diccionarios con la info de la spreguntas que se deben relacionar usando todas las variables definidas abajo
            #pregnta actual
            self.columnas_pact = StringVar(self)
            self.filas_pact = StringVar(self)
            self.suma_pact = StringVar(self)#esta es bool si o no y de ella dependenden las variables de abajo
            self.inicio_suma_pact = StringVar(self)
            self.fin_suma_pact = StringVar(self)
            #pregunta a comparar (referente)
            self.columnas_pref = StringVar(self)
            self.filas_pref = StringVar(self)
            self.suma_pref = StringVar(self)#bool y de ela derivan las de abajo
            self.inicio_suma_pref = StringVar(self)
            self.fin_suma_pref = StringVar(self)

            #restantes para el diccionario
            self.op_p_r = 0
            self.op_p_r1 = StringVar(self)
            self.op_p_r2 = StringVar(self)
            self.op_p_r3 = StringVar(self)
            self.op_p_r4 = StringVar(self)
            self.op_p_r5 = StringVar(self)
            self.comparar = ''
            #funcion autoreferencial
            self.preguntas_rel()
            
        else:
            #cerrar ventanas de instrucciones y tablas
            # self.NV.destroy()
            # self.NV1.destroy()
            #almacenar validaciones en base
            copia = self.base.copy()
            copia['blanco'][self.cont] = self.blanco.get()
            copia['aritmetico'][self.cont] = self.arit.get()
            copia['suma_numeral'][self.cont] = self.sum_n.get()
            
            copia['espeficique'][self.cont] = self.espec.get()
            copia['errores_registro'][self.cont] = self.registro.get()
            copia['salto_preguntas'][self.cont] = self.salto.get()
            copia['preguntas_relacionadas'][self.cont] = self.p_rel1.get()
            self.base=pd.DataFrame(copia)
            self.base.to_csv('veamos.csv',index=False)
            #cambiar pregunta
            self.cont += 1
            if self.cont > len(self.lista)-1:
                self.cont = 0
            self.rec(self.lista[self.cont])
    
    def preguntas_rel(self):
        #objeto pregunta actual
        self.p_act = self.bp(self, self.n_deprgunta)
        clasificadas = self.p_act.instruccio_clasificadas
        self.ins_cons = [] #instrucciones de consistencia
        for instruc in clasificadas:
            if clasificadas[instruc] == 'consistencia':
                self.ins_cons.append(instruc)
        
        if self.ins_cons:
            self.segundo_contador = 0 
            self.iterar_instrucciones()
        else:
            self.iterar_sin_instr()
            
    def iterar_sin_instr(self):
        self.w11 = tk.Toplevel(self)
        self.w11.title('Preguntas relacionadas')
        self.w11.geometry('500x700')
        inst = tk.Label(self.w11,text='No detecto instrucciones de comparación, pero puedes agregar una comparación entre preguntas llenando los siguientes datos: ',
                        wraplength=450)
        inst.pack()
        #variable control op r se vuelve stringvar
        self.op_p_r = StringVar()
        tk.Label(self.w11,text='Selecciona el tipo de comparación: ').pack()
        lista = ['Igual','Menor o igual','Mayor o igual']
        entrada1 = ttk.Combobox(self.w11,
                             state='readonly',
                             values = lista,
                             textvariable=self.op_p_r)
        entrada1.pack()
        #seleciconar pregunta a comparar
        tk.Label(self.w11,text='Selecciona la pregunta con la que se debe comparar: ').pack()
        entrada2 = ttk.Combobox(self.w11,
                             state='readonly',
                             values = self.lista,
                             textvariable=self.op_p_r5)
        entrada2.pack()
        self.w1 = tk.Frame(self.w11)#frame de prgeunta actual
        self.w1.pack(pady=(30,0))
        tk.Label(self.w1,text='Datos de pregunta actual').pack()
        tk.Label(self.w1,text='Filas de interés (en números del 1 en adelante):').pack()
        entrada1 = ttk.Entry(self.w1,validate='key',
                             textvariable = self.filas_pact)
        entrada1.pack()
        tk.Label(self.w1,text='Columnas de interés (en números del 1 en adelante):').pack()
        entrada2 = ttk.Entry(self.w1,validate='key',
                             textvariable = self.columnas_pact)
        entrada2.pack()
        tk.Label(self.w1,text='¿Hay filas que se tienen que sumar?').pack()
        lista = ['Sí','No']
        entrada3 = ttk.Combobox(self.w1,
                             state='readonly',
                             values = lista,
                             textvariable=self.op_p_r2)
        entrada3.pack()
        #estos quedaron como fuciones dentro de la funcion debido a que así fue más sencillo enlazar las variables de control que si solo se hubiese hecho una función aparte, pensando en utilizarla también para el apartado siguiente. 
        def llamado_prel_bool(evento):
            var = evento.widget.get()
            
            if var == 'Sí':
                if len(self.w1.pack_slaves())==7:
                    
                    L1 = tk.Label(self.w1,text='Indica el número de fila donde inicia la suma:')
                    L1.pack()
                    entrada4 = ttk.Entry(self.w1,validate='key',
                                         textvariable = self.inicio_suma_pact)
                    entrada4.pack()
                    L2 = tk.Label(self.w1,text='Indica el número de fila donde termina la suma:')
                    L2.pack()
                    entrada5 = ttk.Entry(self.w1,validate='key',
                                         textvariable = self.fin_suma_pact)
                    entrada5.pack()
            if var =='No':
                li = self.w1.pack_slaves()
                if len(li)>7:
                    for widget in li[7:]:
                        widget.destroy()
                    
        entrada3.bind("<<ComboboxSelected>>", llamado_prel_bool)
    
        #copia para pregunta referente
        self.w2 = tk.Frame(self.w11)#frame de prgeunta actual
        self.w2.pack(pady=(50, 0))
        tk.Label(self.w2,text='Datos de pregunta a comparar').pack()
        tk.Label(self.w2,text='Filas de interés (en números del 1 en adelante):').pack()
        entrada1 = ttk.Entry(self.w2,validate='key',
                             textvariable = self.filas_pref)
        entrada1.pack()
        tk.Label(self.w2,text='Columnas de interés (en números del 1 en adelante):').pack()
        entrada2 = ttk.Entry(self.w2,validate='key',
                             textvariable = self.columnas_pref)
        entrada2.pack()
        tk.Label(self.w2,text='¿Hay filas que se tienen que sumar?').pack()
        lista = ['Sí','No']
        entrada3 = ttk.Combobox(self.w2,
                             state='readonly',
                             values = lista,
                             textvariable=self.op_p_r3)
        entrada3.pack()
        
        def llamado_prel_bool2(evento):
            var = evento.widget.get()
            
            if var == 'Sí':
                if len(self.w2.pack_slaves())==7:
                    
                    L1 = tk.Label(self.w2,text='Indica el número de fila donde inicia la suma:')
                    L1.pack()
                    entrada4 = ttk.Entry(self.w2,validate='key',
                                         textvariable = self.inicio_suma_pref)
                    entrada4.pack()
                    L2 = tk.Label(self.w2,text='Indica el número de fila donde termina la suma:')
                    L2.pack()
                    entrada5 = ttk.Entry(self.w2,validate='key',
                                         textvariable = self.fin_suma_pref)
                    entrada5.pack()
            if var =='No':
                li = self.w2.pack_slaves()
                if len(li)>7:
                    for widget in li[7:]:
                        widget.destroy()
                    
        entrada3.bind("<<ComboboxSelected>>", llamado_prel_bool2)
        #finalmente un botón para por si hay otras instrucciones o comparaciones adicionales a lo detectado por el algoritmo.
        tk.Label(self.w11,text='¿Hay otra comparación que se deba hacer?').pack()
        lista = ['Sí','No']
        ent = ttk.Combobox(self.w11,
                              state='readonly',
                              values = lista,
                              textvariable=self.op_p_r4)
        ent.pack()
        boton = tk.Button(self.w11,
                           text='Continuar',
                           command = self.continuar)
        boton.pack()
                    
    def iterar_instrucciones(self):
        self.w11 = tk.Toplevel(self)
        self.w11.title('Preguntas relacionadas')
        self.w11.geometry('500x700')
        
        inst = tk.Label(self.w11,text=self.ins_cons[self.segundo_contador],wraplength=450)
        inst.pack()
        # op = 0 #op ya es self.op_p_r y se trata de una variable control en función previa
        self.w1 = tk.Frame(self.w11)#frame de prgeunta actual
        self.w1.pack()
        rev = self.ins_cons[self.segundo_contador].lower()
        if 'igual' in rev:
            self.op_p_r = 1

        if 'menor' in rev:
            self.op_p_r = 2

        if 'mayor' in rev:
            self.op_p_r = 3
  
        if self.op_p_r == 0:
            #no se encontró forma de comparación, entonces solicitarla al usuario
            #buscar definir self.op_p_r mediante otra funcion
            # iin = tk.Label(self.w11,text='Favor de indicar el tipo de comparación que se debe hacer: ')
            # iin.pack()
            # lista = ['Igual','Menor o igual','Mayor o igual']
            # despl = ttk.Combobox(self.w1,
            #                      state='readonly',
            #                      values = lista,
            #                      textvariable=self.op_p_r1)
            # despl.pack()
            self.w11.destroy()
            self.iterar_sin_instr()
            return

        if self.op_p_r > 0: 
            self.comparar = self.pregunta_comparar(self.p_act.nombre,self.ins_cons[self.segundo_contador])#string con el nombre de la pregunta que se va a comparar
        #comenzar a poner los widgets en la ventana
        tk.Label(self.w1,text='Datos de pregunta actual').pack()
        tk.Label(self.w1,text='Filas de interés (en números del 1 en adelante):').pack()
        entrada1 = ttk.Entry(self.w1,validate='key',
                             textvariable = self.filas_pact)
        entrada1.pack()
        tk.Label(self.w1,text='Columnas de interés (en números del 1 en adelante):').pack()
        entrada2 = ttk.Entry(self.w1,validate='key',
                             textvariable = self.columnas_pact)
        entrada2.pack()
        tk.Label(self.w1,text='¿Hay filas que se tienen que sumar?').pack()
        lista = ['Sí','No']
        entrada3 = ttk.Combobox(self.w1,
                             state='readonly',
                             values = lista,
                             textvariable=self.op_p_r2)
        entrada3.pack()
        #estos quedaron como fuciones dentro de la funcion debido a que así fue más sencillo enlazar las variables de control que si solo se hubiese hecho una función aparte, pensando en utilizarla también para el apartado siguiente. 
        def llamado_prel_bool(evento):
            var = evento.widget.get()
            
            if var == 'Sí':
                if len(self.w1.pack_slaves())==7:
                    
                    L1 = tk.Label(self.w1,text='Indica el número de fila donde inicia la suma:')
                    L1.pack()
                    entrada4 = ttk.Entry(self.w1,validate='key',
                                         textvariable = self.inicio_suma_pact)
                    entrada4.pack()
                    L2 = tk.Label(self.w1,text='Indica el número de fila donde termina la suma:')
                    L2.pack()
                    entrada5 = ttk.Entry(self.w1,validate='key',
                                         textvariable = self.fin_suma_pact)
                    entrada5.pack()
            if var =='No':
                li = self.w1.pack_slaves()
                if len(li)>7:
                    for widget in li[7:]:
                        widget.destroy()
                    
        entrada3.bind("<<ComboboxSelected>>", llamado_prel_bool)
    
        #copia para pregunta referente
        self.w2 = tk.Frame(self.w11)#frame de prgeunta actual
        self.w2.pack(pady=(50, 0))
        tk.Label(self.w2,text='Datos de pregunta a comparar').pack()
        tk.Label(self.w2,text='Filas de interés (en números del 1 en adelante):').pack()
        entrada1 = ttk.Entry(self.w2,validate='key',
                             textvariable = self.filas_pref)
        entrada1.pack()
        tk.Label(self.w2,text='Columnas de interés (en números del 1 en adelante):').pack()
        entrada2 = ttk.Entry(self.w2,validate='key',
                             textvariable = self.columnas_pref)
        entrada2.pack()
        tk.Label(self.w2,text='¿Hay filas que se tienen que sumar?').pack()
        lista = ['Sí','No']
        entrada3 = ttk.Combobox(self.w2,
                             state='readonly',
                             values = lista,
                             textvariable=self.op_p_r3)
        entrada3.pack()
        
        def llamado_prel_bool2(evento):
            var = evento.widget.get()
            
            if var == 'Sí':
                if len(self.w2.pack_slaves())==7:
                    
                    L1 = tk.Label(self.w2,text='Indica el número de fila donde inicia la suma:')
                    L1.pack()
                    entrada4 = ttk.Entry(self.w2,validate='key',
                                         textvariable = self.inicio_suma_pref)
                    entrada4.pack()
                    L2 = tk.Label(self.w2,text='Indica el número de fila donde termina la suma:')
                    L2.pack()
                    entrada5 = ttk.Entry(self.w2,validate='key',
                                         textvariable = self.fin_suma_pref)
                    entrada5.pack()
            if var =='No':
                li = self.w2.pack_slaves()
                if len(li)>7:
                    for widget in li[7:]:
                        widget.destroy()
                    
        entrada3.bind("<<ComboboxSelected>>", llamado_prel_bool2)
        #finalmente un botón para por si hay otras instrucciones o comparaciones adicionales a lo detectado por el algoritmo.
        if self.segundo_contador+1==len(self.ins_cons):
            tk.Label(self.w11,text='¿Hay otra comparación que se deba hacer?').pack()
            lista = ['Sí','No']
            ent = ttk.Combobox(self.w11,
                                  state='readonly',
                                  values = lista,
                                  textvariable=self.op_p_r4)
            ent.pack()
        boton = tk.Button(self.w11,
                           text='Continuar',
                           command = self.continuar)
        boton.pack()
        
    def continuar(self):
        "esta funcion es para reclectar todos los valores detectados de preguntas relacionadas"
        #se hace la extraccion aqui
        recolector = {}
        if self.comparar:#si hay esta variable es porque fue en funcion de iterar instrucciones
            recolector['pregunta_ref'] = self.comparar
            recolector['operacion'] = self.op_p_r
            recolector['filas_act'] = [self.filas_pact.get()]
            recolector['columnas_act'] = [self.columnas_pact.get()]
            if self.op_p_r2.get()=='Sí':
                recolector['suma_numeral_act'] = [self.inicio_suma_pact.get(),self.fin_suma_pact.get()]
            if self.op_p_r2.get()=='No':
                recolector['suma_numeral_act'] = []
            recolector['filas_ref'] = [self.filas_pref.get()]
            recolector['columnas_ref'] = [self.columnas_pref.get()]
            if self.op_p_r3.get()=='Sí':
                recolector['suma_numeral_ref'] = [self.inicio_suma_pref.get(),self.fin_suma_pref.get()]
            if self.op_p_r3.get()=='No':
                recolector['suma_numeral_ref'] = []
                
        if not self.comparar:#si se cumple esto entonces viene de funcion iterar sin instrucciones
            recolector['pregunta_ref'] = self.op_p_r5.get()
            #convertir valor de operacion a numero porque esta en string
            op = self.op_p_r.get()
            if op == 'Igual':
                a = 1
            if op == 'Menor o igual':
                a = 2
            if op == 'Mayor o igual':
                a = 3
            recolector['operacion'] = a
            recolector['filas_act'] = [self.filas_pact.get()]
            recolector['columnas_act'] = [self.columnas_pact.get()]
            if self.op_p_r2.get()=='Sí':
                recolector['suma_numeral_act'] = [self.inicio_suma_pact.get(),self.fin_suma_pact.get()]
            if self.op_p_r2.get()=='No':
                recolector['suma_numeral_act'] = []
            recolector['filas_ref'] = [self.filas_pref.get()]
            recolector['columnas_ref'] = [self.columnas_pref.get()]
            if self.op_p_r3.get()=='Sí':
                recolector['suma_numeral_ref'] = [self.inicio_suma_pref.get(),self.fin_suma_pref.get()]
            if self.op_p_r3.get()=='No':
                recolector['suma_numeral_ref'] = []
                
        self.preg_rel_var.append(recolector)
            
        #Se avanza a otra instrucción
        if self.ins_cons:
            if self.segundo_contador+1<len(self.ins_cons):
                self.segundo_contador += 1 
                self.iterar_instrucciones()
            elif self.op_p_r4.get()=='Sí':
                self.iterar_sin_instr()
                
            else:
                self.w11.destroy()
                self.base['preg_rel'][self.cont] = self.preg_rel_var
                self.nex()
        else:
            if self.op_p_r4.get()=='Sí':
                self.iterar_sin_instr()
            else:
                self.w11.destroy()
                self.base['preg_rel'][self.cont] = self.preg_rel_var
                self.nex()
                       
    @staticmethod
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
    
    def sumas_de_numerales(self):
        self.vv1 = tk.Toplevel(self)
        self.vv1.title('Numerales de interés')
        self.vv1.geometry('500x500')
        ins = tk.Label(self.vv1, text='Indicar el numero de fila (no de numeral) en donde se encuentra el numeral que es considerado como el total. A continuación, indicar el número de fila (no de numeral!) donde se encuentra el último numeral que es parte de los desagregados a sumar. ',wraplength=450)
        ins.pack()
        tk.Label(self.vv1, text='Fila de total: ').pack()
        entrada1 = ttk.Entry(self.vv1,validate='key',
                             textvariable = self.inicio_suma,
                             validatecommand=(self.vv1.register(self.validate_entry), "%S","%P"))
        entrada1.pack()
        tk.Label(self.vv1, text='Fila de último numeral desagregado: ').pack()
        entrada2 = ttk.Entry(self.vv1,validate='key',
                             textvariable = self.fin_suma,
                             validatecommand=(self.vv1.register(self.validate_entry), "%S","%P"))
        entrada2.pack()
        tk.Label(self.vv1, text='¿Hay otro numeral que deba ser sumado con sus desagregados?').pack()
        boton1 = tk.Button(self.vv1, text ="Sí", command = self.si_sumanum)
        boton1.pack()
        boton2 = tk.Button(self.vv1, text ="No", command = self.no_sumanum)
        boton2.pack()
        
    def si_sumanum(self):
        self.base['s_num_lis'][self.cont].append([int(self.inicio_suma.get())-1,int(self.fin_suma.get())-1])
        #borrar ventana y crear una nueva para otro ingreso de texto
        self.vv1.destroy()
        self.sumas_de_numerales()
        
    def no_sumanum(self):
        self.base['s_num_lis'][self.cont].append([int(self.inicio_suma.get()),int(self.fin_suma.get())])
        #solo destruir ventana e ir nuevaente a nex
        self.vv1.destroy()
        self.nex()
        
    @staticmethod    
    def validate_entry(texto,nuevo):
        if texto.isdigit():
            if nuevo.isdigit():
                comp = texto+nuevo
                if int(comp)==0:
                    False
                else:
                    True
            else:
                return False
        else:
            return False
    
    def prev(self):
        #cerrar ventanas de instrucciones y tablas
        # self.NV.destroy()
        self.NV1.destroy()
        #actualizar el contador
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
            'preguntas_relacionadas':[],'s_num_lis':[],'preg_rel':[]
            }
    #primer paso es conseguir lista con nombres de preguntas
    # lista_preguntas = consg_p(cuestionario)
    # base['preguntas'] = lista_preguntas
    ventana = tk.Tk()
    clase = aplicacion(base,cuestionario,master=ventana)
    clase.mainloop()
    
    return


    