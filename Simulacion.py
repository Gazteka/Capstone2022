from Herramientas import  * 
from Clases import Sala,Paciente,Hospital
# Importamos la seed
np.random.seed(222)

def preparar_pacientes(datos_pacientes):

    pacientes = datos_pacientes["Case ID"]
    set_pacientes = set(pacientes)

    pacientes_listos = dict.fromkeys(set_pacientes)
    for paciente in set_pacientes:
        paciente_df = datos_pacientes[datos_pacientes["Case ID"] == paciente]
        id =paciente_df["Case ID"].iloc[0]
        ruta = list(paciente_df["Area"])
        entrada = paciente_df[paciente_df["Area"] == "URG101_003"]["Marca de tiempo"].iloc[0]
        estadias = dict.fromkeys(ruta,0)
        for area in ruta:
            estadia = paciente_df[paciente_df["Area"] == area]["Estadia"].iloc[0]
            siguiente = paciente_df[paciente_df["Area"] == area]["Siguiente Área"].iloc[0]
            estadias[area] = (estadia,siguiente)
        estadias["End"] = 0
        paciente_class = Paciente(id,ruta,entrada,estadias)
        pacientes_listos[paciente] = paciente_class
    return pacientes_listos



dataset,areas = preparar_datos(DIC_DATOS,AREAS)


hospital = dict.fromkeys(areas)
for area in areas:
    hospital[area] = Sala(area)

info_pacientes = dataset["info_pacientes"]
llegadas = info_pacientes["Entrada"].sort_values()

datos_pacientes = dataset["pacientes"]
pacientes = preparar_pacientes(datos_pacientes)
# for paciente in pacientes:
#     print(pacientes[paciente].estadias)

## Cargamos el hospital
hospital = Hospital(hospital)
hospital.recibir_pacientes(pacientes)
hospital.simular()

# print(hospital)



sala = Sala("URG101_003")
# for paciente in pacientes:
#     sala.llegada(pacientes[paciente])
#     sala.salida(pacientes[paciente])
#     break