
from datetime import datetime


def dia_absoluto(dia, mes, año):
    fecha = datetime(year=año, month=mes, day=dia)
    primer_dia_del_año = datetime(year=año, month=1, day=1)
    numero_dia_absoluto = (fecha - primer_dia_del_año).days + 1
    return numero_dia_absoluto


def create_data(path: str) -> dict:
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

        data[(dia_abs, hora)] = costo

    return data


def get_day_data(day: int, data: dict) -> list:

    hours = []
    costs = []

    for key, value in data.items():
        if key[0] == day:
            hours.append(str(key[1]))
            costs.append(value)

    return [hours, costs]


if __name__ == '__main__':
    data = create_data('data/cerro_navia.csv')

    enero_1 = get_day_data(1, data)
    print(enero_1)
