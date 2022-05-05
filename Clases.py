from distutils.log import error
from functools import total_ordering
from Herramientas import *
import random
import numpy as np
import json
import os
import math
import datetime
from colorama import init
from termcolor import colored
 

dataset,areas = preparar_datos(DIC_DATOS,AREAS)

class GeneradoraPacientes:
    '''
    Esta clase genera una lista de instancias de la clase pacientes con sus atributos respectivos 
    '''
    def __init__(self, seed=18):
        self.seed = seed
        #self.distribución = None
        self.pacientes = []
        self.ids = []
        self.tipo_pacientes = int() # Se rellena este valor en generar_ruta()
        self.distribucion_llegadas = self.cargar_distribucion(prob='llegadas', nombre_archivo='distribuciones_varias.json')
        self.distribuciones_estadias = self.cargar_distribucion(prob='estadias', nombre_archivo='distribuciones_varias.json')

    def cargar_distribucion(self, prob, nombre_archivo):
       
        direccion = os.path.join('Datos', nombre_archivo) 
        with open(direccion) as file:
            data = json.load(file)

        if prob == 'llegadas':
            self.distribucion = dict(data['tiempo_entre_llegadas']['lognorm'])
        elif prob == 'estadias':
            self.distribucion = dict(data) 

        elif prob == 'transiciones':
            pass
        else:
            raise Exception('Hubo un problema con el cargo de datos de las distribuciones')  
        
        return self.distribucion

    def generar_ruta(self, nombre_archivo_rutas):
        '''
        Retorna una ruta aleatoria
        Esta se escoge una ruta de la lista de tuplas --> [([ruta], prob_relativa), ...]
        El largo de la lista corresponde al máximo de rutas para "escoger", lo que corresponde al total de tipos de pacientes
        '''

        direccion = os.path.join('Datos', nombre_archivo_rutas) 
        with open(direccion) as file:
            rutas_dict = json.load(file)
        
        id_rutas = list(rutas_dict.keys())
        rutas_prob = list(rutas_dict.values())

        self.tipo_pacientes = len(id_rutas)

        posibles_rutas = list()
        prob_relativas = list()

        for ruta_prob_dict in rutas_prob:
            ruta_prob = list(ruta_prob_dict.values())
            posibles_rutas.append(ruta_prob[0])
            prob_relativas.append(ruta_prob[1])

        ruta_para_asignar = random.choices(posibles_rutas, weights=prob_relativas, k=1)
        ruta_para_asignar = ruta_para_asignar[0]
        return ruta_para_asignar

    def generar_valores_aleatorios(self, distribucion, params):
        '''
        Recibe un string que es el nombre de la distribución de probabilidad y un diccionario con sus parámetros correspondientes
        Retorna el valor aleatorio correspondiente
        '''
        if distribucion == 'beta':
            param_a = params['a']
            param_b = params['b']
            location = params['loc']
            scale = params['scale']

            valor_aleotorio = (np.random.beta(a=param_a, b=param_b) - location) / scale
        
        elif distribucion == 'lognorm':
            shape = params['s']
            location = params['loc']
            scale = params['scale']
                        
            valor_aleotorio = (np.random.lognormal(mean=math.log(scale), sigma=shape) - location) / scale

        else:
            raise Exception('Distribución no identificada')
        
        return valor_aleotorio

    def asignar_estadias(self, ruta):
        estadias = []
        
        distibucion_opr = list(self.distribuciones_estadias['estadias_opr'].keys())[0]
        distibucion_urg = list(self.distribuciones_estadias['estadias_urg'].keys())[0]
        distibucion_div = list(self.distribuciones_estadias['estadias_div'].keys())[0]
        
        params_opr = self.distribuciones_estadias['estadias_opr'][distibucion_opr]
        params_urg = self.distribuciones_estadias['estadias_urg'][distibucion_urg]
        params_div = self.distribuciones_estadias['estadias_div'][distibucion_div] 
        
        for parada in ruta:
            if "OPR" in parada:
                estadia = self.generar_valores_aleatorios(distribucion=distibucion_opr, params= params_opr)
    
            elif "URG" in parada:
                estadia = self.generar_valores_aleatorios(distribucion=distibucion_urg, params= params_urg)           
           
            elif "DIV" in parada:
                estadia = self.generar_valores_aleatorios(distribucion=distibucion_div, params= params_div)
            
            elif parada == 'Outside':               # Corroborar esto con el resto
                estadia = 0
           
            elif parada == 'End':
                estadia = 0
            
            else:
                print(parada)
                raise Exception('Distribución no identificada para las estadias')

            estadias.append(estadia)

        return estadias

    def generar_id(self):
        if not self.ids: id = 1
        else: id = max(self.ids)+1                  # Verificar eficiencia
        
        self.ids.append(id)
        return id
    
    def generar_pacientes(self, horas, nombre_archivo_rutas, timestamp_inicio=datetime.datetime(2021,1,1,0,0,0,0)):
        np.random.seed(self.seed)

        location = self.distribucion_llegadas['loc']         # -0.1631080499945431
        scale = self.distribucion_llegadas["scale"]          # 3.01277091110916
        shape = self.distribucion_llegadas["s"]              # 1.1325392177517544
       
        n_pacientes = 0
        timestamp = timestamp_inicio
        timestamp_termino = timestamp_inicio + datetime.timedelta(hours=horas)

        while timestamp < timestamp_termino:
            tiempo_entre_llegadas = (np.random.lognormal(mean=math.log(scale), sigma=shape) - location) / scale  # REVISAR PARAMETROS   
            timestamp += datetime.timedelta(hours=tiempo_entre_llegadas)
            n_pacientes += 1 
            
            id_paciente = self.generar_id()
            ruta_paciente = self.generar_ruta(nombre_archivo_rutas)
            estadias_paciente = self.asignar_estadias(ruta_paciente)
            
            paciente = Paciente(id= id_paciente, ruta=ruta_paciente, marca_tiempo_llegada=timestamp, estadias=estadias_paciente)
            self.pacientes.append(paciente)
             
            print(colored(f'Paciente ID: {paciente.id}','blue')) 
            print(f'Llegada: {paciente.marca_tiempo_llegada} | Tiempo entre llegadas: {round(tiempo_entre_llegadas,2)} horas')
            print(colored(f'Ruta Paciente: {paciente.ruta}', 'yellow'))
            print(colored(f'Estadías Paciente: {paciente.estadias}', 'red'), '\n')
        
        return np.array(self.pacientes)

    def diccionario_pacientes(self):

        pacientes_dict = dict()
        for paciente in self.pacientes:
            pacientes_dict[paciente.id] = paciente
        return pacientes_dict

class Sala:
    def __init__(self,nombre):
        self.nombre = nombre
        self.pacientes = []
    
    def __str__(self):
        return self.nombre
    
    def __repr__(self):
        return self.nombre
      
    def llegada(self,paciente,timestamp):
        entrada = timestamp
        
        print(entrada)
        entrada = datetime.datetime.strptime(str(entrada),"%Y-%m-%d %H:%M:%S")
        estadia = paciente.estadias[self.nombre][0]
        salida = entrada + datetime.timedelta(hours=estadia)
        # salida = datetime.datetime.strftime(salida,"%Y-%m-%d %H:%M:%S")
        dict_paciente = {"paciente":paciente.id,"entrada":entrada,"salida":salida}
        self.pacientes.append(dict_paciente)
        print(f"Paciente {paciente} ha entrado en {self.nombre} a las {entrada};salida a las {salida}")
        traslado = (self.nombre,paciente.estadias[self.nombre][1])
        next_event = {"paciente":paciente,"timestamp":salida,"type":"Traslado","content":traslado}

        if self.nombre == "End":
            return {}


        return next_event
    def salida(self,paciente,timestamp):
        # print(self.pacientes)
        encontrar = [paciente_encontrado for paciente_encontrado in self.pacientes if 
                        paciente_encontrado["paciente"] == paciente.id][0]
        self.pacientes.remove(encontrar)
        print(f"Paciente {paciente} ha salido de {self.nombre}a las {timestamp}")
        
class Paciente:
    def __init__(self, id, ruta, marca_tiempo_llegada, estadias):
        self.id = id
        self.ruta = ruta
        self.marca_tiempo_llegada = marca_tiempo_llegada
        self.estadias = estadias
    
    def __str__(self):
        return str(self.id)
    
    def __repr__(self):
        return str(self.id)

class Hospital:

    def __init__(self,salas):
        self.salas = salas

    def recibir_pacientes(self,pacientes):
        self.pacientes = pacientes
        self.eventos = []
        for case_id in pacientes:
            paciente_individual = pacientes[case_id]
            llegada = paciente_individual.entrada
            event = {"paciente":case_id,"timestamp":llegada,"type":"Entrada","content":paciente_individual.ruta[0]}
            self.eventos.append(event)

        self.ordenar_eventos()

    def ordenar_eventos(self):
        self.eventos = sorted(self.eventos,key= lambda x :x["timestamp"])
        # print(self.eventos)
        pass

    def siguiente_evento(self):
        next_evento = self.eventos.pop(0)
        if next_evento["type"] == "Entrada":
            case_id = next_evento["paciente"]
            print(f"Paciente {case_id} ha llegado al hospital")
            evento = self.salas["URG101_003"].llegada(self.pacientes[case_id],next_evento["timestamp"])
            self.eventos.append(evento)
        if next_evento["type"] == "Traslado":
            paciente = next_evento["paciente"]
            timestamp = next_evento["timestamp"]
            sale_de = next_evento["content"][0]
            
            entra_a = next_evento["content"][1]
            self.salas[sale_de].salida(paciente,timestamp)
            print("traslado hacia",entra_a)
            evento = self.salas[entra_a].llegada(paciente,timestamp)
            if evento != {}:
                self.eventos.append(evento)
        else:
            print(next_evento)

    def simular(self):
        while len(self.eventos) > 0:
            self.siguiente_evento()
            self.ordenar_eventos()
        return 0

if __name__ == "__main__":
    generadora = GeneradoraPacientes()
    pacientes = generadora.generar_pacientes(horas=4368, nombre_archivo_rutas='rutas.json')