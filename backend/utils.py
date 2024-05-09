from datetime import datetime


def dia_absoluto(dia: int, mes: int, año: int) -> int:
    # 1 de enero es el día 1
    # 31 de diciembre es el día 365 o 366 (depende si es año bisiesto)
    fecha = datetime(year=año, month=mes, day=dia)
    primer_dia_del_año = datetime(year=año, month=1, day=1)
    numero_dia_absoluto = (fecha - primer_dia_del_año).days + 1
    return numero_dia_absoluto


def get_generacion_electrico(path: str) -> dict:
    with open(path) as file:
        lineas = file.readlines()

    lista = list()
    for linea in lineas:
        lista.append(linea.split(';'))

    # queremos un diccionario del tipo {(dia, hora): [costo]}
    data = {}
    for linea in lista[1:]:
        date_list = linea[0].split('-')

        dia_abs = dia_absoluto(int(date_list[0]), int(
            date_list[1]), int(date_list[2]))

        # fecha en formato DD-MM-YYY
        fecha = linea[0]
        hora = int(linea[2])
        costo = float(linea[3].replace(',', '.'))

        data[(dia_abs, hora)] = [fecha, costo]

    return data


def pretify_hour(hour: int) -> str:
    # hora 1: 00:00
    # hora 24: 23:00

    if 1 <= hour <= 9:
        return f"0{hour - 0}:00"

    elif hour == 24:
        return "00:00"

    else:
        return f"{hour - 0}:00"


def get_day_data(day: int, data: dict) -> dict:

    hours = []
    costs = []

    for key, value in data.items():
        if key[0] == day:
            hours.append(pretify_hour(key[1]))
            costs.append(value[1])
            fecha: str = value[0]

        elif key[0] > day:
            # ya nos pasamos, no queremos más datos
            break

    return {"hours": hours, "costs": costs, "fecha": fecha}


def get_fechas(path) -> list:
    with open(path) as file:
        lineas = file.readlines()
    lista = list()
    for linea in lineas:
        lista.append(linea.split(';'))
    # queremos un diccionario del tipo {(dia, hora): [costo]}
    fechas = list()

    for linea in lista[1:]:
        # fecha en formato DD-MM-YYY
        fecha = linea[0]

        if fecha not in fechas:
            fechas.append(fecha)

    return fechas


def get_consumo_electrico(path: str, path2: str) -> dict:
    # se recibe un csv en formato columnas: horas, filas: dia
    # queremos crear un diccionario de la forma
    # {"hours": hours, "costs": costs, "fecha": fecha}

    fechas = get_fechas(path2)

    with open(path) as file:
        lineas = file.readlines()

    costos = list()
    # lista con 365 listas, cada una con 24 elementos
    for linea in lineas[1:]:
        linea = linea.strip().split(';')
        costos.append(linea)

    data = {}

    for i in range(len(fechas)):
        # la fecha y el dia absoluto en ese año
        fecha = fechas[i]
        date_list = fecha.split('-')
        dia_abs = dia_absoluto(int(date_list[0]), int(
            date_list[1]), int(date_list[2]))

        # obtener los 24 costos de ese dia
        costo = costos[i]

        contador_hora = 1
        for valor in costo:
            # transformar a dato numerico
            new_valor = float(valor.replace(',', '.'))

            # Dani: el Fernando me dijo actualizar este valor
            data[(dia_abs, contador_hora)] = [fecha, new_valor/10]

            contador_hora += 1

    return data


def get_day_data_of_results(day: int, data: dict) -> dict:
    new_data = {}

    for key, value in data.items():
        if key[1] == day:
            new_data[key[0]] = value

    return new_data


def calcular_ahorro_anual(valor_optimo, P: dict, D: dict) -> dict:
    """
    Ahorro en el año completo
    """
    T = range(1, 25)  # Conjunto T: {1, 2, ..., 24}
    K = range(1, 366)  # Conjunto K: {1, 2, ..., 365}

    gasto = sum([D[(t, k)] * P[(t, k)] for t in T for k in K])
    ahorro_anual = round(gasto - valor_optimo, 2)

    ahorro_porcentual = round((ahorro_anual / gasto) * 100, 2)

    return {"ahorro_anual": ahorro_anual, "ahorro_porcentual": ahorro_porcentual}


def calcular_ahorro_diario(P: dict, D: dict, x: dict, z: dict, k_dia: int) -> dict:
    """
    Ahorro en el dia K
    """
    T = range(1, 25)  # Conjunto T: {1, 2, ..., 24}
    K = range(1, 366)  # Conjunto K: {1, 2, ..., 365}

    # el gasto en el dia k
    gasto = sum([D[(t, k_dia)] * P[(t, k_dia)] for t in T])

    # esto lo saque del modelo que mandaste
    ahorro_diario = round(sum([(P[(t, k_dia)] * D[(t, k_dia)]) - (P[(t, k_dia)] * (
        (1 - x[(t, k_dia)]) * D[(t, k_dia)] + z[(t, k_dia)])) for t in T]), 2)

    # esta formula no aparece directamente en el doc del modelo. ¿Esta correcta?
    ahorro_diario_porcentual = round((ahorro_diario / gasto) * 100, 2)

    # retornar estos resultados
    return {"ahorro_diario": ahorro_diario, "ahorro_diario_porcentual": ahorro_diario_porcentual}


def calcular_ahorro_por_hora(P: dict, D: dict, x: dict, z: dict, t_hora: int, k_dia: int) -> dict:
    """
    Ahorro en el momento t_hora, k_dia, donde estos son parametros dados
    """
    gasto = D[(t_hora, k_dia)] * P[(t_hora, k_dia)]
    ahorro_en_hora = round((P[(t_hora, k_dia)] * D[(t_hora, k_dia)]) - (P[(t_hora, k_dia)] * (
        (1 - x[(t_hora, k_dia)]) * D[(t_hora, k_dia)] + z[(t_hora, k_dia)])), 2)

    try:
        ahorro_en_hora_porcentual = round((ahorro_en_hora / gasto) * 100, 2)

    except ZeroDivisionError:
        # si no hay gasto en ese dia, hora, no es posible tener ahorro en forma porentual
        ahorro_en_hora_porcentual = 0

    return {f"ahorro": ahorro_en_hora, f"ahorro_porcentual": ahorro_en_hora_porcentual}


def buscar_x_uno_anual(x: dict, P: dict) -> None:
    cantidad = 0
    T = range(1, 25)  # Conjunto T: {1, 2, ..., 24}
    K = range(1, 366)  # Conjunto K: {1, 2, ..., 365}

    for k in K:
        # horas que hay en el dia
        for t in range(6, 19):
            if x[(t, k)] > 0 and P[(t, k)] == 0:
                cantidad += 1

    print(f'cantidad de casos donde x > 0 y P == 0: {cantidad}')


if __name__ == '__main__':
    # data = create_data('data/cerro_navia.csv')
    # enero_1 = get_day_data(1, data)

    cerro_navia = get_generacion_electrico('data/cerro_navia.csv')
    consumo = get_consumo_electrico(
        'data/consumo_electrico.csv', 'data/cerro_navia.csv')

    # for key, value in cerro_navia.items():
    #     print(key, value)

    # print()

    for key, value in consumo.items():
        print(key, value)
