from distutils.log import error
from functools import total_ordering
from Herramientas import *

import numpy as np
import json
import os
import math
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

    def cargar_distribucion(self, prob, nombre_archivo):
        direccion = os.path.join('Datos',nombre_archivo) 
        with open(direccion) as file:
            data = json.load(file)

        if prob == 'llegadas':
            self.distribucion = dict(data['tiempo_entre_llegadas']['lognorm'])
        elif prob == 'salas':
            self.distribucion = dict(data)
        elif prob == 'estadias':
            pass
        else:
            raise Exception('Hubo un problema con el cargo de datos de las distribuciones')  
        
        return self.distribucion

    def generar_ruta(self):
        ruta = []
        datos_distribuciones = self.cargar_distribucion(prob='salas', nombre_archivo='distribuciones.json')

        ruta.append('URG101_003')
        ruta.append('DIV101_703')
    
        return ruta

    def asignar_estadias(self):
        pass

    def generar_id(self):
        if not self.ids: id = 1
        else: id = max(self.ids)+1                  # Verificar eficiencia
        
        self.ids.append(id)
        return id
    
    def generar_pacientes(self, horas):
        np.random.seed(self.seed)

        hora_dia = 0
        datos_distribucion = self.cargar_distribucion(prob='llegadas', nombre_archivo='distribuciones_varias.json')
        location = datos_distribucion['loc']         # -0.1631080499945431
        scale = datos_distribucion["scale"]          # 3.01277091110916
        shape = datos_distribucion["s"]              # 1.1325392177517544
       
        n_pacientes = 0

        while hora_dia < horas:
            tiempo_entre_llegadas = np.random.lognormal(mean=math.log(scale), sigma=shape)   # REVISAR PARAMETROS   
            llegada_paciente = hora_dia + tiempo_entre_llegadas
            n_pacientes += 1 
            
            id_paciente = self.generar_id()
            ruta_paciente = self.generar_ruta()
            estadias_paciente = self.asignar_estadias()
            
            paciente = Paciente(id= id_paciente, ruta=ruta_paciente, hora_llegada=llegada_paciente, estadias=estadias_paciente)
            self.pacientes.append(paciente)
            
            hora_dia += llegada_paciente  
            hora_print, minuto_print = int(paciente.hora_llegada), int((paciente.hora_llegada-int(paciente.hora_llegada))*60)
            print(colored(f'Paciente ID: {paciente.id}','blue')) 
            print(f'Hora de llegada: {hora_print}:{minuto_print} - Tiempo entre llegadas: {round(tiempo_entre_llegadas,2)} horas')
            print(colored(f'Ruta Paciente: {paciente.ruta}', 'yellow'), '\n')
        
        return np.array(self.pacientes)



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
    def __init__(self, id, ruta, hora_llegada, estadias):
        self.id = id
        self.ruta = ruta
        self.hora_llegada = hora_llegada
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
  pacientes = generadora.generar_pacientes(horas=48)
