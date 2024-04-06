from datetime import datetime
from flask import Flask, flash, render_template, request
import random
from turbo_flask import Turbo
import threading
import time
from pint import UnitRegistry
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
        'options': ['°Bx'],
        'selectedOption': '°Bx',
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

@app.context_processor
def inject_load():
    values_dict = {
        'alcohol': {
            'name': 'Teor alcoólico',
            'value': int(random.random() * 100) / 100,
            'unit': '%',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/alcool.png',
            'image_alt': 'Umidade'
        },
        'brix': {
            'name': 'BRIX',
            'value': int(random.random() * 100) / 100,
            'unit': '%',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/sugar.png',
            'image_alt': 'BRIX'
        },
        'density': {
            'name': 'Densidade',
            'value': int(random.random() * 100) / 100,
            'unit': 'kg/m³',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/density.svg',
            'image_alt': 'Densidade'
        },
        'pressure': {
            'name': 'Pressão',
            'value': int(random.random() * 100) / 100,
            'unit': 'PSI',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/pressure.svg',
            'image_alt': 'Pressão'
        },
        'internal_temperature': {
            'name': 'Temp. Interna',
            'value': int(random.random() * 100) / 100,
            'unit': '°C',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/temperature.svg',
            'image_alt': 'Temp. Interna'
        },
        'external_temperature': {
            'name': 'Temp. Externa',
            'value': int(random.random() * 100) / 100,
            'unit': '°C',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/temperature.svg',
            'image_alt': 'Temp. Externa'
        },
        'co2': {
            'name': 'CO2',
            'value': int(random.random() * 100) / 100,
            'unit': '%',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/co2.png',
            'image_alt': 'CO2'
        },
        'volume': {
            'name': 'Volume',
            'value': int(random.random() * 100) / 100,
            'unit': 'mL',
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
        return render_template('settings.html', values=unit_options)

def update_load():
    with app.app_context():
        while True:
            time.sleep(5)
            turbo.push(turbo.replace(render_template('refreshable.html'), 'load'))
            

th = threading.Thread(target=update_load)
th.daemon = True
th.start()
            
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')