from functools import total_ordering
from Herramientas import *

import numpy as np
import json
import os
import math

from scipy.stats import lognorm


dataset,areas = preparar_datos(DIC_DATOS,AREAS)

class GeneradoraPacientes:
    '''
    Esta clase genera una lista de instancias de la clase pacientes con sus atributos respectivos 
    '''
    
    def __init__(self, seed=17):
        self.seed = seed
        self.distribución = None
        self.pacientes = []
        self.ids = []

    def cargar_distribucion(self):
        direccion = os.path.join('Datos','distribuciones_varias.json') 
        with open(direccion) as file:
            data = json.load(file)
        self.distribucion = dict(data['tiempo_entre_llegadas']['lognorm'])
        
        return self.distribucion

    def generar_ruta(self):
        pass

    def asignar_estadias(self):
        pass

    def generar_id(self):
        if not self.ids: id = 1
        else: id = max(self.ids)+1
        
        self.ids.append(id)
        return id
    
    def generar_pacientes(self, horas):
        np.random.seed(self.seed)

        hora_dia = 0
        
        datos_distribucion = self.cargar_distribucion()
        location = datos_distribucion['loc']         # -0.1631080499945431
        scale = datos_distribucion["scale"]          # 3.01277091110916
        shape = datos_distribucion["s"]              # 1.1325392177517544
       
        n_pacientes = 0

        while hora_dia < horas:
            print(f'Hora del día: {hora_dia}')
            tiempo_entre_llegadas = np.random.lognormal(mean=math.log(scale), sigma=shape)   # REVISAR PARAMETROS   
            llegada_paciente = hora_dia + tiempo_entre_llegadas
            n_pacientes += 1 
            
            id_paciente = self.generar_id()
            ruta_paciente = self.generar_ruta()
            estadias_paciente = self.asignar_estadias()
            
            paciente = Paciente(id= id_paciente, ruta=ruta_paciente, hora_llegada=llegada_paciente, estadias=estadias_paciente)
            self.pacientes.append(paciente)
            
            hora_dia += llegada_paciente    
            print(f'Paciente {n_pacientes} \nHora de llegada: {llegada_paciente} - Tiempo entre llegadas: {tiempo_entre_llegadas}')
        
        print(f'# pacientes generados: {n_pacientes}')

        return np.array(self.pacientes)



class Sala:
    def __init__(self,nombre):
        self.nombre = nombre
        self.pacientes = []
    
    def __str__(self):
        return self.nombre
    
    def __repr__(self):
        return self.nombre
    
    def llegada(self,paciente):
        entrada = paciente.entrada
        print(entrada)
        entrada = datetime.datetime.strptime(str(entrada),"%Y-%m-%d %H:%M:%S")
        estadia = paciente.estadias[self.nombre]
        salida = entrada + datetime.timedelta(hours=estadia)
        # salida = datetime.datetime.strftime(salida,"%Y-%m-%d %H:%M:%S")
        dict_paciente = {"paciente":paciente.id,"entrada":entrada,"salida":salida}
        self.pacientes.append(dict_paciente)

        
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


if __name__ == "__main__":
    generadora = GeneradoraPacientes()
    pacientes = generadora.generar_pacientes(horas=48)
    for paciente in pacientes:
        print(paciente.id)
        print(paciente.hora_llegada)