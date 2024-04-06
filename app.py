from datetime import datetime
from flask import Flask, flash, render_template
import random
from turbo_flask import Turbo
import threading
import time
from sth import get_attribute_data, calc_brix_level, calc_density
import math

app = Flask(__name__)

turbo = Turbo(app)

@app.context_processor
def inject_load():
    values_dict = {
        'alcohol': {
            'name': 'Teor alcoólico',
            'value': "{:.2f}".format(float(calc_brix_level()) * 0.6),
            'unit': '%',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/alcool.png',
            'image_alt': 'Umidade'
        },
        'brix': {
            'name': 'BRIX',
            'value': calc_brix_level(),
            'unit': 'ºbx',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/sugar.png',
            'image_alt': 'BRIX'
        },
        'density': {
            'name': 'Densidade',
            'value': "{:.2f}".format(calc_density()),
            'unit': 'kg/m³',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/density.svg',
            'image_alt': 'Densidade'
        },
        'pressure': {
            'name': 'Pressão',
            'value': "{:.2f}".format((get_attribute_data('pressure_bottom').get('value') + get_attribute_data('pressure_middle').get('value'))/2),
            'unit': 'PSI',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/pressure.svg',
            'image_alt': 'Pressão'
        },
        'internal_temperature': {
            'name': 'Temp. Interna',
            'value': get_attribute_data('temperature_int').get('value'),
            'unit': '°C',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/temperature.svg',
            'image_alt': 'Temp. Interna'
        },
        'external_temperature': {
            'name': 'Temp. Externa',
            'value': get_attribute_data('temperature_ext').get('value'),
            'unit': '°C',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/temperature.svg',
            'image_alt': 'Temp. Externa'
        },
        'co2': {
            'name': 'CO2',
            'value': get_attribute_data('carbon').get('value'),
            'unit': '%',
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'image_location': '/static/images/co2.png',
            'image_alt': 'CO2'
        },
        'volume': {
            'name': 'Volume',
            'value': "{:.2f}".format((get_attribute_data('distance').get('value')-21)*math.pi*(10**2)),
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