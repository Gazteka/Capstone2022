import numpy as np
import pandas as pd
import os
import random
import datetime 

CARPETA = "Datos"
RUTA_DATOS_PACIENTE = os.path.join(CARPETA,"Datos.csv")
RUTA_DATOS_OPERACIONES = os.path.join(CARPETA,"Datos operaciones origen urgencias.csv")
AREAS = ["URG101_003","DIV101_603","DIV101_604","DIV101_703","DIV102_203","DIV103_107","DIV103_204",
"DIV104_602","OPR101_011","OPR101_033","OPR102_001","OPR102_003","End"]

DIC_DATOS  ={"pacientes" : RUTA_DATOS_PACIENTE,"operaciones": RUTA_DATOS_OPERACIONES}

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


if __name__ == "__main__":
    print(preparar_datos(DIC_DATOS,AREAS))