from Herramientas import  * 
from Clases import Sala,Paciente,Hospital
# Importamos la seed
np.random.seed(222)

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



dic_salas = cargar_recursos_sala()
dataset,areas = preparar_datos(DIC_DATOS,AREAS)
info_pacientes = dataset["info_pacientes"]
llegadas = info_pacientes["Entrada"].sort_values()
datos_pacientes = dataset["pacientes"]
pacientes = preparar_pacientes(datos_pacientes)
dic_salas = cargar_distribuciones(dic_salas)



# for paciente in pacientes:
#     print(pacientes[paciente].estadias)
#     print(pacientes[paciente].ruta)
#     print(pacientes[paciente].hora_llegada)


muestra ={14570860:pacientes[14570860]}
# for paciente in muestra:
#     print(pacientes[paciente].estadias)
#     print(pacientes[paciente].ruta)
#     print(pacientes[paciente].hora_llegada)

## Cargamos el hospital
hospital = Hospital(dic_salas)
hospital.recibir_pacientes(pacientes)
hospital.simular()
# print(hospital.eventos)

# print(hospital)



# for paciente in pacientes:
#     sala.llegada(pacientes[paciente])
#     sala.salida(pacientes[paciente])
#     break


#Contar con una decision sobre el modelo
#analsis detallado de los datos
#tener ya una metodologia del problema
#Solucion computacional inicial
#detallar las herramientas utilizadas (Incluyendo supuestos ) 
# En base a la metodologia mostrar resultados obtenidos
#mostrar una discusion más completa, explicar las razones de su seleccion
# Dejar claramente especificado los puntos fuertes de la solucion propuesta
# Plan de trabajo definido para las siguientes etapas


