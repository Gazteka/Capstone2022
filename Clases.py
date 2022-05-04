from distutils.log import error
from functools import total_ordering
from Herramientas import *
from collections import Counter
import random
import numpy as np
import json
import os
import math
from colorama import init
from termcolor import colored
import time

def timer(funcion):
    """
    Se crea un decorador (googlear) del tipo timer para testear el tiempo
    de ejecucion del programa
    """
    def inner(*args, **kwargs):

        inicio = time.time()
        resultado = funcion(*args, **kwargs)
        final = round(time.time() - inicio, 3)
        print("\nTiempo de ejecucion total: {}[s]".format(final))

        return resultado
    return inner

 

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

    def generar_ruta(self, cantidad_tipo_pacientes):
        '''
        Genera muuuchas rutas aleatorias, para luego ordenarlas según su repetición.
        Retorna una lista de tuplas de la forma ([ruta], prob_relativa)
        El n° de TIPO de pacientes determina el largo de esta lista.
        Esta elección de rutas recurrentes determina la prob_relativa de escoger alguna en particular
        '''

        # Genera lista de "rutas" aleatorias --> algunas "rutas" se repetirán porque son concurridas
        muchas_rutas_aleatorias = [random.randint(0, 12) for x in range(1000)] # MODIFICAR POR LA DISTRIBUCIONES

        # Crea un diccionario {ruta1: n° de repeticiones, ruta2: n° de repeticiones, ...}
        contar_repeticiones = dict(Counter(muchas_rutas_aleatorias))

        # Ordena el diccionario. Las rutas con mayor repetición estarán al comienzo.
        # Esta nueva variable es una lista de tuplas --> [(ruta+repetida, n°rep), (2da ruta+repetida, n°rep), ...]
        contar_repeticiones_ordenado = sorted(contar_repeticiones.items(), key = lambda x: x[1], reverse=True)

        # Se corta la lista anterior según la cantidad de tipos de pacientes que definimos
        contar_repeticiones_ordenado = contar_repeticiones_ordenado[:cantidad_tipo_pacientes]

        suma_repeticiones = 0
        for ruta, repeticion in contar_repeticiones_ordenado:
            suma_repeticiones += repeticion

        rutas_prob_relativas = list()
        for ruta, repeticion in contar_repeticiones_ordenado:
            prob_relativa = repeticion / suma_repeticiones
            ruta_prob_relativa = (ruta, prob_relativa)

            rutas_prob_relativas.append(ruta_prob_relativa)

        # print(contar_repeticiones_ordenado)
        # print(rutas_prob_relativas)
        return rutas_prob_relativas

    def asignar_estadias(self, ruta):
        estadias = []
        distribuciones_estadias = self.cargar_distribucion(prob='estadias', nombre_archivo='distribuciones.json')
        salas = distribuciones_estadias.keys()
        for parada in ruta:
            for sala in salas:
                if parada == sala:
                    distribucion = list(distribuciones_estadias[sala].keys())[0]
                    if distribucion == 'beta':
                        param_a = distribuciones_estadias[sala]['beta']['a']
                        param_b = distribuciones_estadias[sala]['beta']['b']
                        location = distribuciones_estadias[sala]['beta']['loc']
                        scale = distribuciones_estadias[sala]['beta']['scale']
                        
                        estadia = (np.random.beta(a=param_a, b=param_b) - location) / scale 

                    elif distribucion == 'lognorm':
                        shape = distribuciones_estadias[sala]['lognorm']['s']
                        location = distribuciones_estadias[sala]['lognorm']['loc']
                        scale = distribuciones_estadias[sala]['lognorm']['scale']
                        
                        estadia = (np.random.lognormal(mean=math.log(scale), sigma=shape) - location) / scale

                    else:
                        raise Exception('Distribución no identificada para las estadias')
                    
                    estadias.append(estadia)

        return estadias

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
            tiempo_entre_llegadas = (np.random.lognormal(mean=math.log(scale), sigma=shape) - location) / scale  # REVISAR PARAMETROS   
            llegada_paciente = hora_dia + tiempo_entre_llegadas
            n_pacientes += 1 
            
            id_paciente = self.generar_id()
            ruta_paciente = self.generar_ruta()
            estadias_paciente = self.asignar_estadias(ruta_paciente)
            
            paciente = Paciente(id= id_paciente, ruta=ruta_paciente, hora_llegada=llegada_paciente, estadias=estadias_paciente)
            self.pacientes.append(paciente)
            
            hora_dia += llegada_paciente  
            hora_print, minuto_print = int(paciente.hora_llegada), int((paciente.hora_llegada-int(paciente.hora_llegada))*60)
            print(colored(f'Paciente ID: {paciente.id}','blue')) 
            print(f'Hora de llegada: {hora_print}:{minuto_print} - Tiempo entre llegadas: {round(tiempo_entre_llegadas,2)} horas')
            print(colored(f'Ruta Paciente: {paciente.ruta}', 'yellow'))
            print(colored(f'Estadías Paciente: {paciente.estadias}', 'yellow'), '\n')
        
        return np.array(self.pacientes)


class Sala:
    def __init__(self,nombre):
        self.nombre = nombre
        self.pacientes = []
        self.recursos = dict()
        self.salas_prohibidas = ["End","Outside"]
        self.fila = []

    
    def __str__(self):
        return self.nombre
    
    def __repr__(self):
        return self.nombre
      
    def llegada(self,paciente,timestamp):
        #Separamos el traslado
        entrada = timestamp
        if self.nombre == "End":
            return {}

        ans = self.atender_pacientes(paciente,timestamp)
        if type(ans) == bool:
            self.fila.append(paciente)
            print(colored(self.fila,"red","on_grey"))
            return {}
        elif type(ans) == datetime.datetime: #Caso quirofano cerrado
            self.fila.append(paciente)
            print(colored(self.fila,"red","on_grey"))
            return {"timestamp":ans,"type":"Apertura","content":self.nombre}
            pass
        # elif type(ans) == int:
        #     print("Usa recursos")
        traslado = paciente.estadias.pop(0)
        if traslado[0] != self.nombre:
            print(self.nombre)
            print(colored("*"*20,"red"))
            print(colored(f"ERROR {traslado}","red"))
            print(colored("*"*20,"red"))
        siguiente_sala = traslado[2]
        estadia = traslado[1]
        salida = entrada + datetime.timedelta(hours = estadia)
        traslado =(self.nombre,siguiente_sala)
        #Agregamos el paciente a la sala
        dict_paciente = {"paciente":paciente.id,"entrada":entrada,"salida":salida}
        self.pacientes.append(dict_paciente)
        n = len(self.fila)
        print(colored(f"Fila : {self.nombre},{n}","magenta"))
    
        next_evento = {"paciente":paciente,"timestamp":salida,"type":"Traslado","content":traslado}

        return next_evento

    def atender_pacientes(self,paciente,timestamp):
        keys = self.recursos
        hora_actual = timestamp.hour
        if "camas" in keys:
            camas = self.recursos["camas"]
            for cama in camas:
                if camas[cama] == False:
                    print(colored(f"Cama {cama} disponible","red"))
                    camas[cama] = paciente
                    return cama
            return False

        elif "box_atencion" in keys:
            boxes = self.recursos["box_atencion"]
            for box in boxes:
                if boxes[box] == False:
                    print(colored(f"Box {box} disponible","red"))
                    boxes[box] = paciente
                    return box
            return False

        elif "quirofanos" in keys:
            hora_inicio = self.recursos["hora_inicio"]
            hora_final = self.recursos["hora_final"]
            if (hora_actual >= hora_inicio) :
                    if hora_actual < hora_final:
                        quirofanos = self.recursos["quirofanos"]
                        for quirofano in quirofanos:
                            quirofanos[quirofano] = paciente
                            return quirofano

                        return False
                    else:
                        print("DIA HOY",timestamp)
                        proximo_dia = timestamp +datetime.timedelta(days = 1)
                        año = proximo_dia.year
                        mes = proximo_dia.month
                        dia = proximo_dia.day
                        proxima_atencion = datetime.datetime(año,mes,dia,hora_inicio)
                        return proxima_atencion
            else :
                    print("DIA HOY",timestamp)
                    proximo_dia = timestamp 
                    año = proximo_dia.year
                    mes = proximo_dia.month
                    dia = proximo_dia.day
                    proxima_atencion = datetime.datetime(año,mes,dia,hora_inicio)
                    return proxima_atencion



        else:
            return "No aplica"
        pass



    def salida(self,paciente,timestamp):
        encontrar = [paciente_encontrado for paciente_encontrado in self.pacientes if 
                        paciente_encontrado["paciente"] == paciente.id][0]
        self.pacientes.remove(encontrar)
        keys = self.recursos.keys()
        if "camas" in keys:
            camas = self.recursos["camas"]
            for cama in camas:
                if camas[cama] == paciente:
                    print(colored(f"{paciente} encontrado en cama{cama} ","cyan"))
                    camas[cama] = False
        elif "box_atencion" in keys:
            boxes = self.recursos["box_atencion"]
            for box in boxes:
                if boxes[box] == paciente:
                    print(colored(f"{paciente} encontrado en box{box}","cyan"))
                    boxes[box] = False
        elif "quirofanos" in keys:
            quirofanos = self.recursos["quirofanos"]
            for quirofano in quirofanos:
                if quirofanos[quirofano] == paciente:
                    print(colored(f"{paciente} encontrado en {quirofano}","cyan"))
                    quirofanos[quirofano] = False

        else:
            pass
        print(colored(f"Paciente {paciente} ha salido de {self.nombre}a las {timestamp}","yellow"))
        largo_fila = len(self.fila)
        if largo_fila > 0:
            siguiente_paciente = self.fila.pop(0)
            next_evento = self.llegada(siguiente_paciente,timestamp)
            if next_evento != {}:
                print(colored(f"Paciente {paciente.id} ha salido de la fila ","magenta"))
            return next_evento
        else:
            return {}

        
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
        self.hora = 0

    
    def recibir_pacientes(self,pacientes):
        self.pacientes = pacientes
        self.eventos = []
        for case_id in pacientes:
            paciente_individual = pacientes[case_id]
            llegada = paciente_individual.hora_llegada
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
            self.hora = next_evento["timestamp"]

            case_id = next_evento["paciente"]
            print(colored(f"Paciente {case_id} ha llegado al hospital","green"))
            evento = self.salas["URG101_003"].llegada(self.pacientes[case_id],next_evento["timestamp"])
            if evento == {}:
                return
            self.eventos.append(evento)
        elif next_evento["type"] == "Traslado":
            self.hora = next_evento["timestamp"]
            paciente = next_evento["paciente"]
            timestamp = next_evento["timestamp"]
            sale_de = next_evento["content"][0]
            
            entra_a = next_evento["content"][1]
            evento_fila = self.salas[sale_de].salida(paciente,timestamp)
            if evento_fila != {}:
                self.eventos.append(evento_fila)
            if entra_a == "End":
                print(colored(f"Paciente terminó su tratamiento {paciente}","green"))
                return 
            print(colored(f"Traslado hacia {entra_a}:paciente n°{paciente}","blue"))
            evento = self.salas[entra_a].llegada(paciente,timestamp)
            if evento != {}:
                self.eventos.append(evento)
        elif  next_evento["type"] == "Apertura":
            self.hora = next_evento["timestamp"]
            sala_abrir = next_evento["content"]
            fila = self.salas[sala_abrir].fila
            if len(fila) > 0:
                paciente = self.salas[sala_abrir].fila.pop(0)
                evento = self.salas[sala_abrir].llegada(paciente,self.hora)
                print(colored(f"Paciente({paciente.id}) entró a la apertura de {sala_abrir}","blue"))
                if evento != {}:
                    self.eventos.append(evento)

        else:
            # print(next_evento)
            return 
    @timer
    def simular(self):
        while len(self.eventos) > 0:
            self.siguiente_evento()
            self.decir_hora()
            self.ordenar_eventos()
        return 0
    def decir_hora(self):
        print(self.hora)


if __name__ == "__main__":
  generadora = GeneradoraPacientes()
  ruta = ['URG101_003', 'DIV101_703', 'DIV101_603','OPR102_001', 'OPR102_003', 'DIV101_603', 'END']
#   pacientes = generadora.generar_pacientes(horas=48)
  generadora.generar_ruta(cantidad_tipo_pacientes=5)