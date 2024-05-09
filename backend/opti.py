# import cells
import pandas as pd
from datetime import datetime
from gurobipy import GRB
import gurobipy as gp
import pickle


def optimize():
    # Definir conjuntos T y K
    T = range(1, 25)  # Conjunto T: {1, 2, ..., 24}
    K = range(1, 366)  # Conjunto K: {1, 2, ..., 365}
    # K = [1]

    # Parámetros
    F = 40  # Capacidad de carga
    alpha = 20  # Flujo de carga

    # INCORPORAR EL CONSUMO HORARIO "D" (DATOS GENERADOS AL AZAR)

    # Lee el archivo Excel
    fd = pd.read_excel('data/consumo_electrico.xlsx', header=None)

    # Elimina la primera fila que contiene los nombres de las columnas
    fd = fd.drop(0)

    fd = fd / 10

    # Define los nombres de las columnas manualmente
    kolumn_names = ['V'+str(i).zfill(2) for i in range(1, 25)]

    # Asigna los nombres de las columnas al DataFrame
    fd.columns = kolumn_names

    # Crea la variable D[t, k] que almacene el valor para la hora t del día k
    D = {}

    # Recorre cada fila del DataFrame y actualiza el valor para cada hora t del día k
    for index, row in fd.iterrows():
        k = index   # Ajusta el índice de fila para comenzar desde el día 2
        for t in range(1, 25):
            D[(t, k)] = row['V'+str(t).zfill(2)]

    # INCORPORAR EL COSTO MARGINAL

    # Lee el archivo CSV sin encabezado y con punto y coma como delimitador
    df = pd.read_csv('data/cerro_navia.csv', header=None, delimiter=';')

    # Define los nombres de las columnas manualmente
    column_names = ['fecha', 'dia', 'hora', 'costo_en_dolares', 'nombre']

    # Asigna los nombres de las columnas al DataFrame
    df.columns = column_names

    # Elimina la primera fila que contiene la palabra "fecha"
    df = df.drop(0)

    # Reemplaza las comas por puntos en la columna 'costo_en_dolares'
    df['costo_en_dolares'] = df['costo_en_dolares'].str.replace(',', '.')

    # Convierte la columna 'costo_en_dolares' a tipo numérico
    df['costo_en_dolares'] = pd.to_numeric(
        df['costo_en_dolares'], errors='coerce')

    # Divide la columna 'fecha' en 'dia', 'mes' y 'ano'
    df[['dia', 'mes', 'ano']] = df['fecha'].str.split('-', expand=True)

    # Elimina la columna 'fecha' ya que ahora está dividida en 'dia', 'mes' y 'ano'
    df.drop(columns=['fecha'], inplace=True)

    # Convierte las columnas 'dia', 'mes' y 'ano' a tipo numérico
    df['dia'] = pd.to_numeric(df['dia'], errors='coerce')
    df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
    df['ano'] = pd.to_numeric(df['ano'], errors='coerce')

    # Crea la variable P[t, k] que almacene el costo para el día k a la hora t
    P = {}

    def fecha(ano, mes, dia):
        fechaa = datetime((row["ano"]), (row["mes"]), (row['dia']))
        return fechaa.toordinal() - 738520
    # Recorre cada fila del DataFrame y actualiza el costo para cada día k a la hora t
    for index, row in df.iterrows():
        t = int(row['hora'])
        # Verifica si los valores de año, mes y día son válidos antes de crear el objeto datetime
        if pd.notnull(row['ano']) and pd.notnull(row['mes']) and pd.notnull(row['dia']):
            # fecha = datetime((row["ano"]), (row["mes"]), (row['dia']))
            k = int(fecha((row["ano"]), (row["mes"]), (row['dia'])))
            costo = row['costo_en_dolares']
            if (t, k) not in P:
                P[(t, k)] = costo

    # print(P)

    # GUROBI

    # Crear el modelo
    problema = gp.Model("problema")

    # Definir variables de decisión
    x = {(t, k): problema.addVar(vtype=GRB.CONTINUOUS, lb=0,
                                 ub=1, name=f"x[{t},{k}]") for t in T for k in K}
    z = {(t, k): problema.addVar(vtype=GRB.CONTINUOUS,
                                 lb=0, name=f"z[{t},{k}]") for t in T for k in K}

    # Definir la función objetivo
    problema.setObjective(gp.quicksum(((1 - x[(t, k)]) * D[(t, k)] * P[(
        t, k)] + z[(t, k)] * P[(t, k)]) for k in K for t in T), GRB.MINIMIZE)

    # RESTRICCIONES

    # RESTRICCION DE INVENTARIO
    # Definir la variable auxiliar I
    I = {(t, k): problema.addVar(vtype=GRB.CONTINUOUS,
                                 lb=0, name=f"I[{t},{k}]") for t in T for k in K}

    # Condiciones de borde para I
    problema.addConstr(I[(1, 1)] == 0, name="borde1")
    for k in K:
        for t in T:
            problema.addConstr(I[(t, k)] <= F, name=f"borde2_{t}_{k}")
            problema.addConstr(I[(t, k)] >= 0, name=f"borde3_{t}_{k}")

    # Definición de I
    for k in K:
        for t in range(2, 25):
            problema.addConstr(I[(t, k)] == I[(
                t-1, k)] + z[(t-1, k)] - x[(t-1, k)] * D[(t-1, k)], name=f"carga_{t}_{k}")
        if k >= 2:
            problema.addConstr(I[(1, k)] == I[(
                24, k-1)] + z[(24, k-1)] - x[(24, k-1)] * D[(24, k-1)], name=f"borde4_{k}")
    for k in K:
        for t in T:
            M = 10**6
            problema.addConstr(M * I[(t, k)] >= x[(t, k)],
                               name=f"restriccion_{t}_{k}")

    # RESTRICCIÓN DE FLUJO:
    for t in T:
        for k in K:
            problema.addConstr(x[(t, k)] * D[(t, k)] +
                               z[(t, k)] <= 2.6, name=f"flujo_{t}_{k}")

    # RESTRICCION, SI x = 0, NO SE USAN LAS BATERIAS
    M = 10e6
    for t in T:
        for k in K:
            problema.addConstr(P[(t, k)]*M >= x[(t, k)])

    # Resolver el problema
    problema.optimize()

    # Imprimir resultados
    # print("Estado:", problema.status)
    # if problema.status == GRB.OPTIMAL:
    #     for t in T:
    #         print(f"Valor de I({t}, {1}):", I[(t, 1)].x)
    #         print(f"Valor de xI({t}, {1}):", x[(t, 1)].x)
    #         print(f"Valor de z({t}, {1}):", z[(t, 1)].x)
    # print("Valor óptimo:", problema.objVal)

    return problema, x, z, I, P, D


if __name__ == "__main__":
    problema, X, Z, i, p, d = optimize()

    problema.update()

    # declarar los diccionarios
    x = {}
    z = {}
    I = {}
    P = {}
    D = {}

    for key, var in X.items():
        x[key] = var.x

    for key, var in Z.items():
        z[key] = var.x

    for key, var in i.items():
        I[key] = var.x

    for key, var in p.items():
        P[key] = var

    for key, var in d.items():
        D[key] = var

    resultados_serializados = {
        "problema.objVal": problema.objVal,
        "x": x,
        "z": z,
        "I": I,
        "P": P,
        "D": D
    }

    with open('data/resultados_modelo.pickle', 'wb') as file:
        pickle.dump(resultados_serializados, file)
