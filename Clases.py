from functools import total_ordering
from Herramientas import *
import numpy as np
import json
import os
import math

dataset,areas = preparar_datos(DIC_DATOS,AREAS)

class GeneradoraPacientes:
    '''
    Esta clase...
    '''
    def __init__(self, seed=17):
        self.seed = seed
        self.distribución = None

    def cargar_distribucion(self):
        direccion = os.path.join('Datos','distribuciones_varias.json') 
        with open(direccion) as file:
            data = json.load(file)
        self.distribución = dict(data['tiempo_entre_llegadas']['lognorm'])
        
        return self.distribución
    
    def generar(self):
        np.random.seed(self.seed)

        hora_dia = 0
        pacientes =[]
        
        datos_distribucion = self.cargar_distribucion()
        location = datos_distribucion['loc'] 
        scale = datos_distribucion["scale"] 
        shape = datos_distribucion["s"]  # Shape
        mu = math.log(scale)
        #sigma = (math.e**(shape**2) * (math.e**(shape**2)-1))**(1/2)
        sigma = ((math.e**(shape**2)-1))**(1/2)
        
        print(f'Parametros: mu:{mu}, sigma:{sigma}')
       
        n_pacientes = 0
        total_pacientes =0
        iter = 10
        for n in range(0, iter):
            print(f'Iteración: {n}')
            print(f'---------------')

            while hora_dia < (24):
                x = np.random.lognormal(1, 0.5)
                #x = -(x*location)/scale
                llegada_paciente = hora_dia + x
                n_pacientes += 1 
                paciente = np.array(['ID', llegada_paciente, x])
                hora_dia += llegada_paciente
                
                print(f'Hora del día: {hora_dia}')
                print(f'Paciente {n_pacientes} \nHora de llegada: {llegada_paciente} - Tiempo entre llegadas: {x}')

            hora_dia = 0
            print(f'# pacientes del día: {n_pacientes}')
            total_pacientes += n_pacientes
            n_pacientes = 0

        print("")
        print("--- Termino el día ---")
        print(f'Pacientes promedio por día: {total_pacientes/iter}')
        pass



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
    def __init__(self,id,ruta,entrada,estadias):
        self.id = id
        self.ruta = ruta
        self.entrada = entrada
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
    generadora.generar()