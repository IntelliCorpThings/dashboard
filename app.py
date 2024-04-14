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
        'label': 'Brix'
    },
    'density': {
        'options': ['kg/m³', 'g/cm³', 'lb/ft³'],
        'selectedOption': 'kg/m³',
        'label': 'Densidade'
    },
    'pressure': {
        'options': ['psi', 'bar'],
        'selectedOption': 'psi',
        'label': 'Pressão'
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
        'options': ['%'],
        'selectedOption': '%',
        'label': 'Gás Carbônico'
    },
    'volume': {
        'options': ['ml', 'floz', 'cups', 'l', 'gal'],
        'selectedOption': 'ml',
        'label': 'Volume'
    }
}

def get_converted_value(value, startUnit, finalUnit):
    if startUnit == '°bx':
        return round(float(value), 2)
    else:
        return round(float(Q_(value, startUnit).to(finalUnit).magnitude), 2)


@app.context_processor
def inject_load():
    values_dict = {
        'alcohol': {
            'name': 'Teor alcoólico',
            'value': "{:.2f}".format(
                get_converted_value(
                    float(calc_brix_level()) * 0.6,
                    '%',
                    unit_options['alcohol']['selectedOption']
                )
            ),
            'unit': unit_options['alcohol']['selectedOption'],
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/alcool.png',
            'image_alt': 'Umidade'
        },
        'brix': {
            'name': 'BRIX',
            'value': get_converted_value(
                calc_brix_level(),
                '°bx',
                unit_options['brix']['selectedOption']
            ),
            'unit': unit_options['brix']['selectedOption'],
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/sugar.png',
            'image_alt': 'BRIX'
        },
        'density': {
            'name': 'Densidade',
            'value': "{:.2f}".format(get_converted_value(
                calc_density(),
                'kg/m³',
                unit_options['density']['selectedOption']
            )),
            'unit': unit_options['density']['selectedOption'],
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/density.svg',
            'image_alt': 'Densidade'
        },
        'pressure': {
            'name': 'Pressão',
            'value': "{:.2f}".format(get_converted_value(
                (get_attribute_data('pressure_bottom').get('value') + get_attribute_data('pressure_middle').get('value'))/2,
                'psi',
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
            'value': "{:.2f}".format(get_converted_value(
                (get_attribute_data('distance').get('value')-21)*math.pi*(10**2),
                'ml',
                unit_options['volume']['selectedOption']
            )),
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
th.start()
            
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')