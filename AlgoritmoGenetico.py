import random
import numpy as np
# import pygad
from Simulacion import obtener_intervalo_confianza, realizar_simulacion_completa, generar_muestras_pacientes, vector_cromosoma,timer
import time
import copy
random.seed(333)
import json
import os
import copy

class AlgoritmoGenetico: 
    def __init__(self, cromosoma_inicial,n_iter = 5):
        self.cromosoma_inicial = cromosoma_inicial
        self.crom_sup = [5, 8, 15, 6, 15, 10, 13, 18, 1]
        dic_genes = dict.fromkeys(range(0,9))
        dic_genes[0] = (3,5)
        dic_genes[1] = (5,8)
        dic_genes[2] = (12,15)
        dic_genes[3] = (5,6)
        dic_genes[4] = (12,15)
        dic_genes[5] = (8,10)
        dic_genes[6] = (10,13)
        dic_genes[7] = (14,18)
        dic_genes[8] = (0, 1)
        self.dic_genes = dic_genes
        #self.muestras_pacientes = generar_muestras_pacientes()

    def generar_poblacion(self):  #Genera la poblacion inicial, retorna lista de cromosomas 
        tamaño_poblacion = 15 
        poblacion_inicial = list()  
        while len(poblacion_inicial) < tamaño_poblacion: 
            vector_cromosoma = list()
            for gen in self.dic_genes:
                tupla = self.dic_genes[gen]
                gen = random.randint(tupla[0], tupla[1])
                vector_cromosoma.append(gen)
            if vector_cromosoma not in poblacion_inicial:
                poblacion_inicial.append(vector_cromosoma)
        return poblacion_inicial
        
    def calcular_funcion_aptitud(self, intervalo, alpha = 0.1, beta = 0.01, cromosoma = [3,5,12,5,12,8,10,14,0]): 
        #f(x,y,z_m,) = lt_p + pc + alhpa*max{0,CI-M$50.000} + beta*max{0,CO-M$4.500}
        cromosoma_inicial = np.array([3,5,12,5,12,8,10,14,0])
        costos_operativos = np.array([150,450,250,250,250,250,250,250,800])
        costos_inversion = np.array([0,12500,3500,3500,3500,3500,3500,3500,25000])
        extras = cromosoma - cromosoma_inicial
        ci_max = 50000
        co_max = 4500
        co = np.dot(extras,costos_operativos)
        ci = np.dot(extras,costos_inversion)
        ci_real = np.max([0,ci-ci_max])
        co_real = np.max([0,co-co_max])
        resultado = intervalo + alpha*ci_real +beta*co_real
        return resultado

    def crossover(self, pob_actual): #se aplica el crossover, retorna el hijo 
        sel1 = pob_actual[0][0]
        sel2 = pob_actual[1][0]
        sel3 = pob_actual[2][0]
        n_hijos = 6 

        h1 = sel1[:4] + sel2[4:]
        h2 = sel2[:4] + sel1[4:]
        h3 = sel1[:4] + sel3[4:]
        h4 = sel3[:4] + sel1[4:]
        h5 = sel2[:4] + sel3[4:]
        h6 = sel3[:4] + sel2[4:]

        pob_siguiente = [h1, h2, h3, h4, h5, h6, sel1, sel2, sel3]
        for i in range(len(pob_siguiente)):
            hijo = pob_siguiente[i]
            hijo_mutado = self.mutacion(hijo)
            if hijo_mutado in pob_siguiente:
                if str(hijo_mutado) not in self.lista_tabu.keys():
                # print(pob_siguiente.index(hijo_mutado))
                    pob_siguiente.append(hijo_mutado)
        
        # for i in range(len(pob_siguiente)):
        #     print(i,pob_siguiente[i])

        return pob_siguiente

        # while sel2 == sel1:
        #     sel2 = random.randint(0,len(pob_actual))
        # resultados_1 = resultados[sel1]
        # resultados_2 = resultados[sel2]
        # best = np.min([resultados_1, resultados_2])
        # papa_1 = pob_actual[resultados.index(best)]


        # print(pob_actual)
        # print(papa_1)


    def mutacion(self, hijo):
         #calcular la probabilidad (p) de mutacion de este hijo. si p<c: terminar mutacion
        lugar = random.randint(0,8)
        extremos = self.dic_genes[lugar]
        # print(lugar,extremos)
        valor_actualizar = random.randint(extremos[0],extremos[1])
        hijo[lugar] = valor_actualizar
        return hijo 
        pass 

    

    @timer
    def iteracion_algoritmo(self, n = 30):
        n = n#num iteraciones total
        # n = self.n_iter
        with open(os.path.join('Resultados', 'resultados_algoritmo.csv'),"a") as file:
            iter_realizadas = 0
            fo_evaluadas = list()
            self.lista_tabu = {}
            dic_resultados = {}
            muestras = generar_muestras_pacientes(n_seeds = 30, n_horas=24*7*2)
            while iter_realizadas < n: 
                if iter_realizadas == 0:
                    pob_actual = self.generar_poblacion()
                #muestras = generar_muestras_pacientes(n_seeds = 200, n_horas=24*7*4)
                for cromosoma in pob_actual:
                    dic_salas = vector_cromosoma(cromosoma)
                    #muestras = generar_muestras_pacientes(n_seeds = 1, n_horas=24*7*4)
                    if str(cromosoma) in self.lista_tabu.keys():
                        lt_crom = self.lista_tabu[str(cromosoma)]
                        # print(cromosoma,"in lista tabu")
                        
                    else:

                        lt_crom = realizar_simulacion_completa(dic_salas,copy.deepcopy(muestras))
                        self.lista_tabu[str(cromosoma)] = lt_crom
                    lt_i = obtener_intervalo_confianza(lt_crom)[1]# Esto despues sera el intervalo de confianza
                    fo = self.calcular_funcion_aptitud(lt_i,cromosoma = cromosoma)
                    dic_resultados[str(cromosoma)] = fo
                    # print(fo)
                    fo_evaluadas.append((cromosoma,fo))     
                fo_evaluadas.sort(key = lambda x:x[1],reverse = False)
                # print(fo_evaluadas)
                pob_actual = self.crossover(fo_evaluadas)
                fo_evaluadas_resultados = [duo[1] for duo in fo_evaluadas]
                fo_evaluadas_resultados = sorted(fo_evaluadas_resultados,reverse = False)[:20]
                mean = np.mean(fo_evaluadas_resultados)
                min = np.min(fo_evaluadas_resultados)
                max = np.max(fo_evaluadas_resultados)
                best= 0
                for key in dic_resultados:
                    if dic_resultados[key] == min:
                        best= key
                line = f"{iter_realizadas};{min};{mean};{max};{best};{pob_actual} \n"
                file.write(line)
                print("N° de iteraciones",iter_realizadas)
                print("Minimo",np.min(fo_evaluadas_resultados))
                print("Mean",np.mean(fo_evaluadas_resultados))
                print("Max",np.max(fo_evaluadas_resultados))

                iter_realizadas += 1
            # print(lista_tabu)

        
            




if __name__ == "__main__":
    #instancia = pygad.GA()
    #instancia.run()
    cromosoma_inicial = [3, 5, 12, 5, 12, 8, 10, 14 ,0] #x, y, z_1, z_2, z_4, z_5, z_6, z_7, e
    res_inicial = [44200.96030345001,
                        44000.93867937252, 
                        37000.93199233972, 
                        35000.9374771365,
                         28000.943639212135,
                          26001.067227299278,
                           23000.94852666772,
                            19001.05187153868,
                             13501.061599483626, 
                             12000.956109608425,
                              8500.94574871874,
                               5000.957289042866, 
                               1.0249610356969987, 
                               1.0247527976921778, 
                               0.9412720493707553]

    a = AlgoritmoGenetico(cromosoma_inicial)
    a.iteracion_algoritmo()
    # pob_actual = a.generar_poblacion()
    # a.crossover(pob_actual, res_inicial)
    
    
