from datetime import datetime
from multiprocessing import Value
from typing import final
from flask import Flask, flash, render_template, request, redirect
import random
from turbo_flask import Turbo
import threading
import time
from pint import UnitRegistry
from datetime import datetime, timedelta
from sth import get_attribute_data, calc_brix_level, calc_density
import math
import json

ureg = UnitRegistry()
Q_ = ureg.Quantity 

app = Flask(__name__)

turbo = Turbo(app)

unit_options = {
    'alcohol': {
        'options': ['%'],
        'selectedOption': '%',
        'label': 'Teor alcóolico'
    },
    'brix': {
        'options': ['°bx'],
        'selectedOption': '°bx',
        'label': 'Teor de Sólidos Solúveis'
    },
    'density': {
        'options': ['kg/m³', 'g/cm³', 'lb/ft³'],
        'selectedOption': 'kg/m³',
        'label': 'Densidade'
    },
    'pressure': {
        'options': ['g', 'kg'],
        'selectedOption': 'g',
        'label': 'Massa'
    },
    'internal_temperature': {
        'options': ['°C', '°F'],
        'selectedOption': '°C',
        'label': 'Temperatura Interna'
    },
    'external_temperature': {
        'options': ['°C', '°F'],
        'selectedOption': '°C',
        'label': 'Temperatura Externa'
    },
    'co2': {
        'options': ['ppm'],
        'selectedOption': 'ppm',
        'label': 'Gás Carbônico'
    },
    'volume': {
        'options': ['ml', 'floz', 'cups', 'l', 'gal'],
        'selectedOption': 'ml',
        'label': 'Volume'
    }
}

def get_converted_value(value, startUnit, finalUnit):
    try:
        if startUnit == '°bx':
            return round(float(value), 2)
        else:
            return round(float(Q_(value, startUnit).to(finalUnit).magnitude), 2)
    except:
        return 0

def limitValue(val, max):
    if val < 0:
        return 0
    elif val > max:
        return max
    else:
        return val

@app.context_processor
def inject_load():
    values_dict = {
        'alcohol': {
            'name': 'Teor alcoólico',
            'value': "{:.2f}".format(
                limitValue(
                    get_converted_value(
                        float(calc_brix_level()) * 0.6,
                        '%',
                        unit_options['alcohol']['selectedOption']
                    ),
                    100
                )
            ),
            'unit': unit_options['alcohol']['selectedOption'],
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/alcool.png',
            'image_alt': 'Umidade'
        },
        'brix': {
            'name': 'Teor de Sólidos Solúveis',
            'value': limitValue(
                    get_converted_value(
                    calc_brix_level(),
                    '°bx',
                    unit_options['brix']['selectedOption']
                ),
                100
            ),
            'unit': unit_options['brix']['selectedOption'],
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/sugar.png',
            'image_alt': 'Teor de Sólidos Solúveis'
        },
        'density': {
            'name': 'Densidade',
            'value': "{:.2f}".format(limitValue(
                get_converted_value(
                    calc_density(),
                    'kg/m³',
                    unit_options['density']['selectedOption']
                ),
                5000
            )),
            'unit': unit_options['density']['selectedOption'],
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/density.svg',
            'image_alt': 'Densidade'
        },
        'pressure': {
            'name': 'Pressão',
            'value': "{:.2f}".format(get_converted_value(
                (abs(get_attribute_data('pressure_bottom').get('value') + get_attribute_data('pressure_middle').get('value'))/2),
                'g',
                unit_options['pressure']['selectedOption']
            )),
            'unit': unit_options['pressure']['selectedOption'],
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/pressure.svg',
            'image_alt': 'Pressão'
        },
        'internal_temperature': {
            'name': 'Temp. Interna',
            'value': get_converted_value(
                get_attribute_data('temperature_int').get('value'),
                '°C',
                unit_options['internal_temperature']['selectedOption']
            ),
            'unit': unit_options['internal_temperature']['selectedOption'],
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/temperature.svg',
            'image_alt': 'Temp. Interna'
        },
        'external_temperature': {
            'name': 'Temp. Externa',
            'value': get_converted_value(
                get_attribute_data('temperature_ext').get('value'),
                '°C',
                unit_options['external_temperature']['selectedOption']
            ),
            'unit': unit_options['external_temperature']['selectedOption'],
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/temperature.svg',
            'image_alt': 'Temp. Externa'
        },
        'co2': {
            'name': 'CO2',
            'value': get_converted_value(
                get_attribute_data('carbon').get('value'),
                '%',
                unit_options['co2']['selectedOption']
            ),
            'unit': unit_options['co2']['selectedOption'],
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/co2.png',
            'image_alt': 'CO2'
        },
        'volume': {
            'name': 'Volume',
            'value': "{:.2f}".format(limitValue(get_converted_value(
                (21 - get_attribute_data('distance').get('value'))*math.pi*((8.7**2) + 8.7*9.65 + (9.65**2))/3,
                'ml',
                unit_options['volume']['selectedOption']
            ),9999999999)),
            'unit': unit_options['volume']['selectedOption'],
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/measure.svg',
            'image_alt': 'mL'
        }
    }
    return {'values': values_dict}

@app.route('/')
def hello():
    return render_template('index.html')

def calcular_media(valores):
    try:
        return sum(valores) / len(valores) if valores else 0
    except:
        return 0

@app.route('/getmultdata/<finddata>', methods=['GET', 'POST'])
def getmultdata(finddata):
    resultados = {}
    sth_name = ''

    match finddata:
        case 'alcohol':
            sth_name = 'pressure_bottom'
        case 'brix': 
            sth_name = 'pressure_bottom'
        case 'density': 
            sth_name = 'pressure_bottom'
        case 'pressure': 
            sth_name = 'pressure_bottom'
        case 'internal_temperature': 
            sth_name = 'temperature_int'
        case 'external_temperature':
            sth_name = 'temperature_ext'
        case 'co2': 
            sth_name = 'carbon'
        case 'volume': 
            sth_name = 'distance'

    # Processar os dados
    for dia in get_attribute_data(sth_name, 45):
        # Verificar se há elementos no dia
        if not dia:
            continue
        
        # Extrair a data do primeiro elemento válido
        data_str = dia[0]["_id"]["origin"]
        data_obj = datetime.strptime(data_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        data_formatada = data_obj.strftime("%d/%m/%Y")
        
        # Coletar todos os valores 'max' do dia, garantindo que há pontos válidos
        valores_max = []
        for item in dia:
            if "points" in item and item["points"]:
                for ponto in item["points"]:
                    if "max" in ponto:
                        valores_max.append(ponto["max"])

        print('valores_max')
        print(valores_max)
        
        # Verificar se há valores antes de calcular a média
        if valores_max:
            tempValue = 0
            media_max = calcular_media(valores_max)
            match finddata:
                case 'alcohol':
                    tempValue = get_converted_value(
                        float(calc_brix_level(media_max)) * 0.6,
                        '%',
                        unit_options['alcohol']['selectedOption']
                    )
                case 'brix': 
                    tempValue = get_converted_value(
                        calc_brix_level(media_max),
                        '°bx',
                        unit_options['brix']['selectedOption']
                    )
                case 'density': 
                    tempValue = get_converted_value(
                        calc_density(media_max),
                        'kg/m³',
                        unit_options['density']['selectedOption']
                    )
                case 'pressure': 
                    tempValue = get_converted_value(
                        (media_max + media_max)/2,
                        'psi',
                        unit_options['pressure']['selectedOption']
                    )
                case 'internal_temperature': 
                    tempValue = get_converted_value(
                        media_max,
                        '°C',
                        unit_options['internal_temperature']['selectedOption']
                    )
                case 'external_temperature':
                    tempValue = get_converted_value(
                        media_max,
                        '°C',
                        unit_options['external_temperature']['selectedOption']
                    )
                case 'co2': 
                    tempValue = get_converted_value(
                        media_max,
                        'ppm',
                        unit_options['co2']['selectedOption']
                    )
                case 'volume': 
                    tempValue = get_converted_value(
                        limitValue((21 - media_max)*math.pi*((8.7**2) + 8.7*9.65 + (9.65**2))/3, 9999999999),
                        'ml',
                        unit_options['volume']['selectedOption']
                    )
            # Adicionar ao resultado
            resultados[data_formatada] = tempValue

    # Converter para JSON
    json_resultado = json.dumps(resultados, indent=4)
    print(json_resultado)
    return resultados

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings.html', values=unit_options)
    if request.method == 'POST':
        for item in unit_options.keys():
            unit_options[item]['selectedOption'] = request.form[item]
        return redirect("/", code=302)

def update_load():
    with app.app_context():
        while True:
            time.sleep(5)
            print(get_attribute_data('pressure_bottom').get('value'))
            print(get_attribute_data('pressure_middle').get('value'))
            turbo.push(turbo.replace(render_template('refreshable.html'), 'load'))
            

th = threading.Thread(target=update_load)
th.daemon = True
            
if __name__ == '__main__':
    th.start()
    app.run(debug=True, host='0.0.0.0', port=5000)