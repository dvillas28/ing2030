from flask import Flask, render_template
from backend import utils
from backend import data_paths

app = Flask(__name__)

# static data from cerro_navia.csv
cn_data = utils.get_generacion_electrico(data_paths.CERRO_NAVIA)

consumo_data = utils.get_consumo_electrico(
    data_paths.CONSUMO_ELECTRICO, data_paths.CERRO_NAVIA)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dia_<int:i>')
def mostrar_grafico(i):
    if i == 0 or i == 366:
        return render_template('index.html')

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


if __name__ == '__main__':
    app.run(debug=True)
