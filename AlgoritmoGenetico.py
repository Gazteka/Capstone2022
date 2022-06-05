import random
import numpy as np
import pygad
from Simulacion import realizar_simulacion_completa, generar_muestras_pacientes, vector_cromosoma,timer
import time
import copy
random.seed(2)

class AlgoritmoGenetico: 
    def __init__(self, cromosoma_inicial):
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
        self.muestras_pacientes = generar_muestras_pacientes()
        self.m = self.muestras_pacientes.copy()

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
        
    def calcular_funcion_aptitud(self, intervalo, alpha = 0.01, beta = 0.01, cromosoma = [3,5,12,5,12,8,10,14,0]): 
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

    def crossover(self, pob_actual, resultados): #se aplica el crossover, retorna el hijo 
        sel1 = pob_actual[0]
        sel2 = pob_actual[1]
        sel3 = pob_actual[2]
        n_hijos = 6 

        h1 = sel1[:4] + sel2[4:]
        h2 = sel2[:4] + sel1[4:]
        h3 = sel1[:4] + sel3[4:]
        h4 = sel3[:4] + sel1[4:]
        h5 = sel2[:4] + sel3[4:]
        h6 = sel3[:4] + sel2[4:]

        pob_siguiente = [h1, h2, h3, h4, h5, h6, sel1, sel2, sel3]
        return pob_siguiente

        # while sel2 == sel1:
        #     sel2 = random.randint(0,len(pob_actual))
        # resultados_1 = resultados[sel1]
        # resultados_2 = resultados[sel2]
        # best = np.min([resultados_1, resultados_2])
        # papa_1 = pob_actual[resultados.index(best)]


        # print(pob_actual)
        # print(papa_1)


    def mutacion(self, hijo): #calcular la probabilidad (p) de mutacion de este hijo. si p<c: terminar mutacion
        pass 

    

    @timer
    def iteracion_algoritmo(self, n = 5):
        n = n#num iteraciones total
        iter_realizadas = 0
        fo_evaluadas = list()
        while iter_realizadas < n: 
            if iter_realizadas == 0:
                pob_actual = self.generar_poblacion()
            for cromosoma in pob_actual:
                dic_salas = vector_cromosoma(cromosoma)
                muestras = generar_muestras_pacientes()
                lt_crom = realizar_simulacion_completa(dic_salas,muestras)
                lt_i = np.mean(lt_crom)# Esto despues sera el intervalo de confianza
                fo = self.calcular_funcion_aptitud(lt_i,cromosoma = cromosoma)
                fo_evaluadas.append(fo)           
            fo_evaluadas.sort(reverse=False)
            pob_actual = self.crossover(pob_actual, fo_evaluadas)
            print("-"*10)
            print("Minimo",np.min(fo_evaluadas))
            print("Mean",np.mean(fo_evaluadas))
            print("Max",np.max(fo_evaluadas))

            iter_realizadas += 1



        
            




if __name__ == "__main__":
    #instancia = pygad.GA()
    #instancia.run()
    cromosoma_inicial = [3, 5, 12, 5, 12, 8, 10, 14 ]#,0] #x, y, z_1, z_2, z_4, z_5, z_6, z_7, e
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
    #pob_actual = a.generar_poblacion()
    #a.crossover(pob_actual, res_inicial)
    
    
