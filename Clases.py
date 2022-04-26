from Herramientas import *

dataset,areas = preparar_datos(DIC_DATOS,AREAS)

class Sala:
    
    def __init__(self,nombre):
        self.nombre = nombre
        self.pacientes = []
        self.recursos = dict()
    
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


    def simular():
        pass

    
    