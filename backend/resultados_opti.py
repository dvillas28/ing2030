import pickle


def obtener_resultados(path: str) -> None:
    # Dani: si esta tirando errores al importar ese modulo, cambiar la ruta nomas
    with open(path, 'rb') as file:
        resultados = pickle.load(file)

    problema = resultados["problema.objVal"]
    x = resultados["x"]
    z = resultados["z"]
    I = resultados["I"]
    P = resultados["P"]
    D = resultados["D"]

    return problema, x, z, I, P, D


if __name__ == "__main__":
    problema, x, z, I, P, D = obtener_resultados(
        'data/resultados_modelo.pickle')

    # imprimir los resultados
    T = range(1, 25)

    # for t in T:
    #     print(f"Valor de I({t}, {1}):", I[(t, 1)])
    #     print(f"Valor de xI({t}, {1}):", x[(t, 1)])
    #     print(f"Valor de z({t}, {1}):", z[(t, 1)])

    # print("Valor óptimo:", problema)
