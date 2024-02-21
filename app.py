from datetime import datetime
from flask import Flask, flash, render_template
import random
from turbo_flask import Turbo
import threading
import time

app = Flask(__name__)

turbo = Turbo(app)

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
        }
    }
    return {'values': values_dict}

@app.route('/')
def hello():
    return render_template('index.html')

def update_load():
    with app.app_context():
        while True:
            time.sleep(60*7)
            turbo.push(turbo.replace(render_template('refreshable.html'), 'load'))
            

th = threading.Thread(target=update_load)
th.daemon = True
th.start()
            
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')