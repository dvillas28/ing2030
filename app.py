from flask import Flask, render_template
from backend import utils
from backend import data_paths
from backend import resultados_opti

app = Flask(__name__)

# static data from cerro_navia.csv
cn_data = utils.get_generacion_electrico(data_paths.CERRO_NAVIA)

# test data from consumo_electrico.csv
consumo_data = utils.get_consumo_electrico(path=data_paths.CONSUMO_ELECTRICO,
                                           path2=data_paths.CERRO_NAVIA)

# results from the optimization model
# problema: costo minimo
# x: fraccion de energia que es suministrada por las baterias en el periodo t,k
# z: energia comprada para ser almacenada en baterias en el periodo t,k
# I: porcentaje de energia en las baterias?
problema, x, z, I, P, D = resultados_opti.obtener_resultados(
    path=data_paths.RESULTADOS)
ahorro_todos_los_dias = utils.ahorro_todos_los_dias(P, D, x, z)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/dia_<int:i>')
def mostrar_grafico(i):
    if i == 0 or i == 366:
        return render_template('home.html')

    data_of_the_day = utils.get_day_data(i, cn_data)

    data_of_the_day_consumo = utils.get_day_data(i, consumo_data)

    dataset_cn = {
        "labels": data_of_the_day["hours"],
        "data": data_of_the_day["costs"]
    }

    dataset_consumo = {
        "labels": data_of_the_day_consumo["hours"],
        "data": data_of_the_day_consumo["costs"]
    }

    return render_template('graficos.html',
                           dia=i,
                           fecha=data_of_the_day["fecha"],
                           dataset_cn=dataset_cn,
                           dataset_consumo=dataset_consumo)


@app.route('/ahorro_dia_<int:i>')
def mostrar_ahorros(i):
    """
    I es un dia
    """
    if i == 0 or i == 366:
        return render_template('home.html')

    # estos no son utilizados en ningun calculo
    x_of_the_day = utils.get_day_data_of_results(i, x)
    z_of_the_day = utils.get_day_data_of_results(i, z)
    I_of_the_day = utils.get_day_data_of_results(i, I)

    print(f'PROGRAM LOGS')
    print('| d | h |  x  |  z  |  I  |')
    print('|---|---|-----|-----|-----|')
    for t in range(1, 25):
        print(
            f'| {i} | {t} | {round(x[(t,i)], 2)} | {round(z[(t,i)], 2)} | {round(I[(t,i)], 2)} |')

    ahorros_anuales, gasto_anual = utils.calcular_ahorro_anual(problema, P, D)
    print()
    print(ahorros_anuales)

    ahorros_diarios, gasto_diario = utils.calcular_ahorro_diario(P, D, x, z, i)
    print()
    print(ahorros_diarios)

    ahorros_por_hora = {t: utils.calcular_ahorro_por_hora(P=P,
                                                          D=D,
                                                          x=x,
                                                          z=z,
                                                          t_hora=t,
                                                          k_dia=i) for t in range(1, 25)}
    print()
    for key, value in ahorros_por_hora.items():
        print(f'hora {key}: {value}')

    print('-------------')
    # utils.buscar_x_uno_anual(x, P)

    for key, value in ahorro_todos_los_dias.items():
        print(f'dia {key}: ')

    fecha = data_of_the_day = utils.get_day_data(i, cn_data)["fecha"]

    # TODO: nos faltan los ahorros diarios de todos los dias
    multiLineData = {
        "labels": list(ahorro_todos_los_dias.keys()),
        "data1": list(ahorro_todos_los_dias.values())[0][0],
        "data2": list(ahorro_todos_los_dias.values())[0][1]
    }
    return render_template('ahorro.html',
                           ahorros_anuales=ahorros_anuales,
                           ahorros_diarios=ahorros_diarios,
                           ahorros_por_hora=ahorros_por_hora,
                           fecha=fecha,
                           dia=i,
                           gasto_anual=gasto_anual,
                           gasto_diario=gasto_diario,
                           multiLineData=multiLineData)

# negativos interpredso como surplus (exceso) comprar energia y comparar energia para la bateria
# ahorro diario: numero y paster

# ahorro hora: grafico


if __name__ == '__main__':
    app.run(debug=True)
