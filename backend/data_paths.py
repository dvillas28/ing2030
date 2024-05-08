from os import path

CERRO_NAVIA = path.join('backend', 'data', 'cerro_navia.csv')
CONSUMO_ELECTRICO = path.join('backend', 'data', 'consumo_electrico.csv')
RESULTADOS = path.join('backend', 'data', 'resultados_modelo.pickle')

if __name__ == '__main__':
    print(CERRO_NAVIA)
    print(CONSUMO_ELECTRICO)
    print(RESULTADOS)
