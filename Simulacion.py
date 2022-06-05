from Herramientas import  * 
from Clases import Sala,Paciente,Hospital,GeneradoraPacientes,timer

def preparar_pacientes(datos_pacientes):
    """Crea las clases de pacientes y las devuelve en formato clases
        rutas :lista
        estadias : lista de sets (salaActual,estadia,siguienteSala)
        hora_llegada :timestamp"""
    pacientes = datos_pacientes["Case ID"]
    set_pacientes = set(pacientes)

    pacientes_listos = dict.fromkeys(set_pacientes)
    for paciente in set_pacientes:
        #Iteramos sobre los pacientes
        paciente_df = datos_pacientes[datos_pacientes["Case ID"] == paciente]
        id =paciente_df["Case ID"].iloc[0]
        ruta = list(paciente_df["Area"])
        entrada = paciente_df[paciente_df["Area"] == "URG101_003"]["Marca de tiempo"].iloc[0]
        estadias = []
        for i in range(paciente_df.shape[0]):
            row = paciente_df.iloc[i]
            area_actual = row["Area"]
            estadia = row["Estadia"]
            siguiente_area = row["Siguiente Área"]
            if area_actual == "End":
                continue
            estadias.append((area_actual,estadia,siguiente_area))
        paciente_class = Paciente(id,ruta,entrada,estadias)
        pacientes_listos[paciente] = paciente_class
    return pacientes_listos

def cargar_recursos_sala():
    direccion = os.path.join('Datos', 'recursos_salas.json')
    dic_salas = dict()
    with open(direccion) as file:
        recursos_sala = json.load(file)
    for nombre_sala in recursos_sala:
        sala_actual = Sala(nombre_sala)
        if nombre_sala == 'URG101_003' or nombre_sala == 'DIV101_703':
            sala_actual.recursos['box_atencion'] = dict()
            for box_atencion in range(1, recursos_sala[nombre_sala]['box_atencion']+1):
                sala_actual.recursos['box_atencion'][box_atencion] = False
            sala_actual.recursos['ampliacion_max'] = recursos_sala[nombre_sala]['ampliacion_max']

        elif "DIV" in nombre_sala and nombre_sala != 'DIV_101_703':
            sala_actual.recursos['camas'] = dict()
            for cama in range(1, recursos_sala[nombre_sala]['camas']+1):
                sala_actual.recursos['camas'][cama] = False
            sala_actual.recursos['ampliacion_max'] = recursos_sala[nombre_sala]['ampliacion_max']

        elif nombre_sala == 'OPR102_001':
            sala_actual.recursos['quirofanos'] = dict()
            for quirofano in range(1, recursos_sala[nombre_sala]['quirofanos']+1):
                sala_actual.recursos['quirofanos'][quirofano] = False
            sala_actual.recursos['hora_inicio'] = recursos_sala[nombre_sala]['hora_inicio']
            sala_actual.recursos['hora_final'] = recursos_sala[nombre_sala]['hora_final']

        elif nombre_sala == 'OPR101_011':
            sala_actual.recursos['quirofanos'] = dict()
            for quirofano in range(1, recursos_sala[nombre_sala]['quirofanos']+1):
                sala_actual.recursos['quirofanos'][quirofano] = False
            sala_actual.recursos['hora_inicio'] = recursos_sala[nombre_sala]['hora_inicio']
            sala_actual.recursos['hora_final'] = recursos_sala[nombre_sala]['hora_final']
            sala_actual.recursos['hora_limite'] = recursos_sala[nombre_sala]['hora_limite']

        elif nombre_sala == 'OPR102_003':
            sala_actual.recursos['quirofanos'] = dict()
            for quirofano in range(1, recursos_sala[nombre_sala]['quirofanos']+1):
                sala_actual.recursos['quirofanos'][quirofano] = False
            sala_actual.recursos['hora_inicio'] =  recursos_sala[nombre_sala]['hora_inicio']
            sala_actual.recursos['hora_final'] = recursos_sala[nombre_sala]['hora_final']
            sala_actual.recursos['hora_limite'] = recursos_sala[nombre_sala]['hora_limite']
        
        elif nombre_sala == 'OPR101_033':
            sala_actual.recursos['quirofanos'] = dict()
            for quirofano in range(1, recursos_sala[nombre_sala]['quirofanos']+1):
                sala_actual.recursos['quirofanos'][quirofano] = False
            sala_actual.recursos['hora_inicio'] = recursos_sala[nombre_sala]['hora_inicio']
            sala_actual.recursos['hora_final'] = recursos_sala[nombre_sala]['hora_final']

        dic_salas[nombre_sala] = sala_actual
        dic_salas["Outside"] = Sala("Outside")
        dic_salas["End"] = Sala("End")
    return dic_salas

def vector_cromosoma(cromosoma):
    diccionario_salas = cargar_recursos_sala()

    for key in diccionario_salas:
        #print(diccionario_salas[key].recursos)
        if key == "URG101_003":
            recurso = dict.fromkeys(range(1,cromosoma[0]+1),False)
            diccionario_salas[key].recursos["box_atencion"] = recurso

        elif key == "DIV101_703":
            recurso = dict.fromkeys(range(1,cromosoma[1]+1),False)
            diccionario_salas[key].recursos["box_atencion"] = recurso

        elif key == "DIV101_603":
            recurso = dict.fromkeys(range(1,cromosoma[2]+1),False)
            diccionario_salas[key].recursos["camas"] = recurso
        
        elif key == "DIV101_604":
            recurso = dict.fromkeys(range(1,cromosoma[3]+1),False)
            diccionario_salas[key].recursos["camas"] = recurso

        elif key == "DIV102_203":
            recurso = dict.fromkeys(range(1,cromosoma[4]+1),False)
            diccionario_salas[key].recursos["camas"] = recurso
        
        elif key == "DIV103_107":
            recurso = dict.fromkeys(range(1,cromosoma[5]+1),False)
            diccionario_salas[key].recursos["camas"] = recurso
        
        elif key == "DIV103_204":
            recurso = dict.fromkeys(range(1,cromosoma[6]+1),False)
            diccionario_salas[key].recursos["camas"] = recurso
        
        elif key == "DIV104_602":
            recurso = dict.fromkeys(range(1,cromosoma[7]+1),False)
            diccionario_salas[key].recursos["camas"] = recurso

        #elif key == "OPR101_033":
        #    recurso = dict.fromkeys(range(1,cromosoma[8]+1),False)
        #    diccionario_salas[key].recursos["disponibilidad"] = recurso

    return diccionario_salas
        

def generar_muestras_pacientes(n_seeds = 30,n_horas = 24*30):
    muestras = {}
    for i in range(n_seeds):
        generadora = GeneradoraPacientes(seed = i)
        pacientes = generadora.generar_pacientes(horas=n_horas, nombre_archivo_rutas='rutas.json')
        pacientes = preparar_pacientes_generadora(pacientes)
        muestras[i] = pacientes
    return muestras
@timer
def realizar_simulacion_completa(dic_salas,muestras):
    resultados = []
    for seed in muestras:
        hospital = Hospital(dic_salas)
        hospital.recibir_pacientes(muestras[seed])
        hospital.simular()

        p = hospital.pacientes


        lead_time_promedio = obtener_lead_time_medio(p)
        resultados.append(lead_time_promedio)
    return resultados

if __name__ == "__main__":
    cromosoma_inicial = [3, 5, 12, 5, 12, 8, 10, 14 ]#,0] #x, y, z_1, z_2, z_4, z_5, z_6, z_7, e
    dic_salas = vector_cromosoma(cromosoma_inicial)
    dataset,areas = preparar_datos(DIC_DATOS,AREAS)
    # info_pacientes = dataset["info_pacientes"]
    # llegadas = info_pacientes["Entrada"].sort_values()
    # datos_pacientes = dataset["pacientes"]
    # pacientes_originales = preparar_pacientes(datos_pacientes)
    dic_salas = cargar_distribuciones(dic_salas)
    muestras = generar_muestras_pacientes()
    res = realizar_simulacion_completa(dic_salas,muestras)
    print(res)
    