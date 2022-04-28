from Herramientas import *


dataset,areas = preparar_datos(DIC_DATOS,AREAS)



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