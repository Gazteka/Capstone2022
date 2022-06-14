import numpy as np
import pandas as pd
import os
import random
import datetime 
import json
import time
from collections import Counter


CARPETA = "Datos"
RUTA_DATOS_PACIENTE = os.path.join(CARPETA,"Datos.csv")
RUTA_DATOS_OPERACIONES = os.path.join(CARPETA,"Datos operaciones origen urgencias.csv")
AREAS = ["URG101_003","DIV101_603","DIV101_604","DIV101_703","DIV102_203","DIV103_107","DIV103_204",
"DIV104_602","OPR101_011","OPR101_033","OPR102_001","OPR102_003","End"]


DIC_DATOS  ={"pacientes" : RUTA_DATOS_PACIENTE,"operaciones": RUTA_DATOS_OPERACIONES}


def cargar_matriz_transicion(dic_datos,areas):
    df_heatmap = pd.DataFrame(index = areas,columns = areas)
    datos_pacientes = dic_datos["pacientes"]
    for area in areas:
        derivacion_urgencia = datos_pacientes[datos_pacientes["Area"] == area]["Siguiente Área"]
        transiciones = (derivacion_urgencia.value_counts()/derivacion_urgencia.shape[0])
        df_heatmap[area] = transiciones
    df_heatmap = df_heatmap.fillna(0)
    df_heatmap.to_json("Datos\heatmap.json", orient = 'columns')
    return df_heatmap

def generar_ruta_aleatoria(archivo_heatmap_json):
    '''
    Genera 1 ruta aleatoria de la forma --> ['URG101_003', ... , 'End']
    Se realiza de manera aleatoria, con las probabilidades de transición de heatmap.json
    '''

    direccion = os.path.join('Datos', str(archivo_heatmap_json)) 
    with open(direccion) as file:
        data = json.load(file)

    sala_inicial = 'URG101_003'
    sala_final   = 'End'
    sala_actual = sala_inicial

    ruta = list()
    ruta.append(sala_actual)
    # Mientras no salga de urgencias
    while sala_actual != sala_final:

        salas = list(data[sala_actual].keys()) # A modo de eficiencia podría ir fuera del while, creo.
        prob_transicion_salas = list(data[sala_actual].values())

        sala_siguiente = random.choices(salas, weights=prob_transicion_salas, k=1)
        sala_actual = sala_siguiente[0]

        ruta.append(sala_actual)
    return ruta

def encontrar_rutas_probables(archivo_heatmap_json, repeticiones_totales=1000, hacer_print = False):
    '''
    Genera muuuchas rutas aleatorias, para luego ordenarlas desde la más frecuente/repetida.
    Genera un json. 500mil repeticiones record
    Retorna una lista de tuplas, de la forma --> [([ruta], prob_relativa), ...]
    '''
    muchas_rutas_aleatorias = list()
    for i in range(repeticiones_totales):
        nueva_ruta = generar_ruta_aleatoria(archivo_heatmap_json)
        muchas_rutas_aleatorias.append(nueva_ruta)

    # Crea un diccionario {ruta1: n° de repeticiones, ruta2: n° de repeticiones, ...}
    contar_repeticiones = dict(Counter(tuple(x) for x in muchas_rutas_aleatorias))
    
    # Ordena el diccionario. Las rutas con mayor repetición estarán al comienzo.
    # Esta nueva variable es una lista de tuplas --> [(1era ruta+repetida, n°rep), (2da ruta+repetida, n°rep), ...]
    contar_repeticiones_ordenado = sorted(contar_repeticiones.items(), key = lambda x: x[1], reverse=True)
    
    # Escogen los 95 rutas más frecuentes
    contar_repeticiones_ordenado = contar_repeticiones_ordenado[:95]

    rep_total = 0
    rutas = list()
    for ruta, rep in contar_repeticiones_ordenado:
        rep_total += rep
        rutas.append(ruta)
    
    probabilidades = list()
    for rupa, rep in contar_repeticiones_ordenado:
        probabilidades.append(round(rep/rep_total, 8))

    rutas_dict = dict()
    for index in range(len(rutas)):
        ruta_prob = dict()
        ruta_prob['ruta'] = list(rutas[index])
        ruta_prob['prob'] = probabilidades[index]
        rutas_dict[f'{index+1}'] = ruta_prob

    # Hacer el json
    direccion = os.path.join('Datos', 'rutas.json') 
    with open(direccion, 'w') as file:
        json.dump(rutas_dict, file)

    if hacer_print == True:
        for index in range(len(rutas)):
            print(f'{index+1}. {rutas[index]}')
            print(f'{index+1}. Prob: {probabilidades[index]}%')

    return contar_repeticiones_ordenado

def cantidad_total_rutas(archivo_heatmap_json, tiempo_ejecucion_segundos):
    '''
    ¿Cuántas rutas distintas existirán en total?
    10min --> 9187 rutas en total
    '''
    
    tiempo_termino = time.time() + tiempo_ejecucion_segundos
    rutas = list()
    while time.time() <= tiempo_termino:

        posible_nueva_ruta = generar_ruta_aleatoria(archivo_heatmap_json)
        # Si es una nueva ruta
        if posible_nueva_ruta not in rutas:
            rutas.append(posible_nueva_ruta)
    
    return len(rutas)

def preparar_datos(dic_datos,areas):
    dataset = {}
    for key in dic_datos:
        file = dic_datos[key]
        if key == "pacientes":
            datos_pacientes = pd.read_csv(file,sep = ";")
            datos_pacientes["Marca de tiempo"] = pd.to_datetime(datos_pacientes["Marca de tiempo"])

            # dataset["pacientes"] = datos_pacientes
            filtro_fuera = (~datos_pacientes["Area"].isin(areas))
            datos_pacientes.loc[filtro_fuera,"Area"] = "Outside"
            filtro_doble_fuera = (
                ~datos_pacientes["Area"].isin(areas))&((~datos_pacientes["Area"].shift(1).isin(areas))
                                )
            datos_pacientes = datos_pacientes[~filtro_doble_fuera]
            datos_pacientes["Hora derivacion"] = datos_pacientes["Marca de tiempo"].shift(-1)
            datos_pacientes["Estadia"] = datos_pacientes["Hora derivacion"]  - datos_pacientes["Marca de tiempo"]
            datos_pacientes["Estadia"] = datos_pacientes["Estadia"]/np.timedelta64(1,"h")
            datos_pacientes["Siguiente Área"] = datos_pacientes["Area"].shift(-1)
            set_pacientes = set(datos_pacientes["Case ID"])
            entrada = "URG101_003"
            salida = "End"
            dic_info_pacientes = dict.fromkeys(set_pacientes,{})
            for paciente in set_pacientes:
                info_paciente = datos_pacientes[datos_pacientes["Case ID"] == paciente]
                hora_entrada = info_paciente.iloc[0]["Marca de tiempo"]
                hora_salida = info_paciente.iloc[-1]["Marca de tiempo"]
                dic_paciente ={"Entrada":hora_entrada,"Salida":hora_salida}
                duracion = hora_salida - hora_entrada
                dic_paciente["Duracion"] = duracion/np.timedelta64(1,"h")
                procedimiento = list(info_paciente["Area"])
                ruta = "".join(procedimiento)
                dic_paciente["Ruta"] = ruta
                dic_info_pacientes[paciente] = dic_paciente
            df_info_pacientes = pd.DataFrame(dic_info_pacientes).T
            dataset["pacientes"] = datos_pacientes
            dataset["info_pacientes"] = df_info_pacientes
    
    areas.append("Outside")
    return dataset,areas


def cargar_distribuciones(dic_salas):
    file = os.path.join("Datos","distribuciones_varias.json")
    file = open(file,"r")
    file = json.load(file)
    for sala in dic_salas:
        if "OPR" in sala:
            print(sala)
            dic_salas[sala].distribucion = file["estadias_opr"]
        elif "DIV" in sala:
            dic_salas[sala].distribucion = file["estadias_div"]
        elif "URG" in sala:
            dic_salas[sala].distribucion = file["estadias_urg"]
        else:
            dic_salas[sala].distribucion = {}
    return dic_salas

def preparar_pacientes_generadora(pacientes):
    dic_pacientes = {}
    for j  in range(len(pacientes)):
        paciente = pacientes[j]
        estadias_final = []
        for i in range(len(paciente.estadias)-1):
            estadia = abs(paciente.estadias[i])
            entra = paciente.ruta[i]
            sale = paciente.ruta[i+1]
            info = (entra,estadia,sale)
            estadias_final.append(info)
        paciente.estadias = estadias_final
        dic_pacientes[paciente.id] = paciente
    return dic_pacientes


def obtener_lead_time_medio(pacientes):
    tiempos = []
    entradas = []
    salidas = []
    entradas = [pacientes[pat].datos["llegada"] for pat in pacientes]
    entradas = sorted(entradas)
    ult_entrada = entradas[-1]
    for pat in pacientes :
        datos = pacientes[pat].datos
        diff = datos["salida"]-datos["llegada"]
        entradas.append(datos["llegada"])
        salidas.append(datos["salida"])
        diff = diff/datetime.timedelta(hours = 1)
        diff_w_last = (datos["salida"] -ult_entrada)/datetime.timedelta(hours = 1)
        if diff_w_last > 0:
            continue
        else:
            tiempos.append(diff)
    
    return np.mean(tiempos)


    
if __name__ == "__main__":
    DIC_DATOS,AREA = preparar_datos(DIC_DATOS,AREAS)
    print(cargar_distribuciones({}))