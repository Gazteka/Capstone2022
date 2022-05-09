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
            print(f'Llegada: {paciente.hora_llegada} | Tiempo entre llegadas: {round(tiempo_entre_llegadas,2)} horas')
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
        paciente.datos.append({self.nombre : timestamp})
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
    def __init__(self, id, ruta, marca_tiempo_llegada, estadias):
        self.id = id
        self.ruta = ruta
        self.hora_llegada = marca_tiempo_llegada
        self.estadias = estadias
        self.datos = []
    
    def __str__(self):
        return str(self.id)
    
    def __repr__(self):
        return str(self.id)

class Hospital:

    def __init__(self, salas):
        self.salas = salas
        self.hora = 0
        self.datos = {}

    def recibir_pacientes(self, pacientes):
        self.pacientes = pacientes
        self.eventos = []
        for case_id in pacientes:
            paciente_individual = pacientes[case_id]
            llegada = paciente_individual.hora_llegada
            event = {"paciente":case_id,"timestamp":llegada,"type":"Entrada","content":paciente_individual.ruta[0]}
            self.eventos.append(event)

        self.ordenar_eventos()

    def ordenar_eventos(self):
        self.eventos = sorted(self.eventos, key= lambda x :x["timestamp"])
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
              
            print(f"Paciente {case_id} ha llegado al hospital")
            evento = self.salas["URG101_003"].llegada(self.pacientes[case_id], next_evento["timestamp"])

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
                evento = self.salas[entra_a].llegada(paciente,timestamp)
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
            # self.decir_hora()
            self.ordenar_eventos()
            self.obtener_estado()
        return 0
    def decir_hora(self):
        print(self.hora)
    
    def obtener_estado(self):
        info_actual = {}
        for sala in self.salas:
            fila = len(self.salas[sala].fila)
            en_atencion = len(self.salas[sala].pacientes)
            info_actual[f"{sala}_fila"] = fila
            info_actual[f"{sala}_atencion"] = en_atencion
        self.datos[self.hora] = info_actual

if __name__ == "__main__":
    generadora = GeneradoraPacientes()
    pacientes = generadora.generar_pacientes(horas=4368, nombre_archivo_rutas='rutas.json')