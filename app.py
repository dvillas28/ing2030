from flask import Flask, render_template
from backend import utils
from backend import data_paths

app = Flask(__name__)

# static data from cerro_navia.csv
cn_data = utils.create_data(data_paths.CERRO_NAVIA)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/dia_<int:i>')
def mostrar_grafico(i):
    if i == 0 or i == 366:
        return render_template('index.html')

    data_of_the_day = utils.get_day_data(i, cn_data)

    dataset = {
        "labels": data_of_the_day["hours"],
        "data": data_of_the_day["costs"]
    }

    print(dataset)

    return render_template('graficos.html', dataset=dataset, fecha=data_of_the_day["fecha"], dia=i)


if __name__ == '__main__':
    app.run(debug=True)
