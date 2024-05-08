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
problema, x, z, I = resultados_opti.obtener_resultados(
    path=data_paths.RESULTADOS)


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
    x_of_the_day = utils.get_day_data_of_results(i, x)
    z_of_the_day = utils.get_day_data_of_results(i, z)
    I_of_the_day = utils.get_day_data_of_results(i, I)

    print('| d | h |  x  |  z  |  I  |')
    print('|---|---|-----|-----|-----|')
    for t in range(1, 25):
        print(
            f'| {i} | {t} | {round(x_of_the_day[t], 2)} | {round(z_of_the_day[t], 2)} | {round(I_of_the_day[t], 2)} |')

    return render_template('ahorro.html',
                           x=x_of_the_day,
                           z=z_of_the_day,
                           I=I_of_the_day)


if __name__ == '__main__':
    app.run(debug=True)
