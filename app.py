from flask import Flask, render_template
from backend import dicts

app = Flask(__name__)

data = dicts.create_data('backend/data/cerro_navia.csv')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cerro_navia_<int:i>')
def mostrar_grafico(i):
    day = dicts.get_day_data(i, data)

    dataset = {
        "labels": day[0],
        "data": day[1]
    }

    print(dataset)
    return render_template('graficos.html', dataset=dataset, dia=i)


if __name__ == '__main__':
    app.run(debug=True)
