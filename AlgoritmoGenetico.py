import numpy 
import pygad

#de simulacion tenemos: 
#


class AlgoritmoGenetico: 
    def __init__(self, cromosoma_inicial):
        self.cromosoma_inicial = cromosoma_inicial
        dic_genes = dict.fromkeys(range(0,8))
        dic_genes[0] = (3,5)
        dic_genes[1] = (5,8)
        dic_genes[2] = (12,15)
        dic_genes[3] = (5,6)
        dic_genes[4] = (12,15)
        dic_genes[5] = (8,10)
        dic_genes[6] = (10,13)
        dic_genes[7] = (14,18)
        self.dic_genes = dic_genes

    def generar_poblacion(self):  #Genera la poblacion inicial, retorna lista de genes 

        for gen in self.dic_genes:
            print(self.dic_genes[gen])


       
        #print(x)
        
        pass
        
    def funcion_aptitud(self):  #f(x,y,z_m,) = lt_p + pc + alhpa*max{0,CI-M$50.000} + beta*max{0,CO-M$4.500}
        pass


 # Sorted the matrix in decreasing order of fitness function. **
 # Seleccionar 2 padres random, los que obtengan mejor resultado de funcion de aptitud


    def crossover(self, padre1, padre2): #se aplica el crossover, retorna el hijo 
        pass

    def mutacion(self, hijo): #calcular la probabilidad (p) de mutacion de este hijo. si p<c: terminar mutacion
        pass 

    #reemplazar el hijo resultante en la mala poblacion (?
    #

if __name__ == "__main__":
    #instancia = pygad.GA()
    #instancia.run()
    cromosoma_inicial = [3, 5, 12, 5, 12, 8, 10, 14 ]#,0] #x, y, z_1, z_2, z_4, z_5, z_6, z_7, e
    a = AlgoritmoGenetico(cromosoma_inicial)

    a.generar_poblacion()
    
