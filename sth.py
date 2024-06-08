import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json

ip = '46.17.108.131'

# Constantes
HEADERS = {'fiware-service': 'smart', 'fiware-servicepath': '/'}

def get_previous_days(numero_dias):
    hoje = datetime.now()

    dias = []

    for i in range(numero_dias):
        dia_anterior = hoje - timedelta(days=i + 1)
        dias.append(dia_anterior.strftime("%Y-%m-%d"))

    dias.reverse()
    
    return dias

def get_attribute_data(entity, lastN=None):
    """Obtém dados do atributo da API."""
    url = ''
    if lastN is not None:
        url = f"http://{ip}:8666/STH/v1/contextEntities/type/dt/id/urn:ngsi-ld:unittest:001/attributes/{entity}?aggrMethod=max&aggrPeriod=minute&dateFrom=2024-04-01T00:00:00.000Z&dateTo=2024-04-07T23:59:59.999Z"
    else:
        url = f"http://{ip}:1026/v2/entities/urn:ngsi-ld:unittest:001/attrs/{entity}"
    try:
        if lastN is not None:
            result = []
            dateList = get_previous_days(lastN)
            for currDate in dateList:
                url = f"http://{ip}:8666/STH/v1/contextEntities/type/dt/id/urn:ngsi-ld:unitest:001/attributes/{entity}?aggrMethod=max&aggrPeriod=minute&dateFrom={currDate}T00:00:00.000Z&dateTo={currDate}T23:59:59.999Z"
                response = requests.get(url, headers=HEADERS)
                response.raise_for_status()
                result.append(response.json()['contextResponses'][0]['contextElement']['attributes'][0]['values'])
        else:
            url = f"http://{ip}:1026/v2/entities/urn:ngsi-ld:unittest:001/attrs/{entity}"
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            result = response.json()

        # result2 = {}
        # for idx, x in enumerate(result):
        #     result2[]
        return result
    except requests.HTTPError as http_err:
        return f"Erro HTTP ao obter dados: {http_err}"
    except Exception as err:
        return f"Erro ao obter dados: {err}"

def calc_brix_level(value=None):
    g = 9.81  # m/s², gravidade na Terra
    rho_w = 1000  # kg/m³, densidade da água
    delta_h = 0.061  # metros, distância entre os sensores
    psi_to_pa = 6894.76
    
    # Obtendo os valores de pressão
    if value == None:
        pressure_bottom_data = get_attribute_data('pressure_bottom')
        pressure_middle_data = get_attribute_data('pressure_middle')
    else:
        pressure_bottom_data = value
        pressure_middle_data = value

    if isinstance(pressure_bottom_data, dict) and isinstance(pressure_middle_data, dict):
        if value == None:
            pressure_bottom = pressure_bottom_data.get('value') * psi_to_pa
            pressure_middle = pressure_middle_data.get('value') * psi_to_pa
        else:
            pressure_bottom = pressure_bottom_data * psi_to_pa
            pressure_middle = pressure_middle_data * psi_to_pa
        # Calculando a pressão diferencial (ΔP)
        delta_p = pressure_bottom - pressure_middle
        if delta_p < 0 :
            delta_p = delta_p * -1; 

        # Calculando a densidade do líquido (ρ) usando a equação (2)
        rho = delta_p / (g * delta_h)
        # Calculando a Gravidade Específica (SG) do líquido usando a equação (3)
        sg = rho / rho_w
        # Calculando o valor de Brix (∘Bx) usando a equação (4)
        brix = (sg - 1) * 1000 / 4
        print(f"Nível de Brix: {brix:.2f}°Bx")
        return "{:.2f}".format(brix)
    else:
        print("Erro ao obter dados de pressão.")
        return 'error'

def calc_density(value=None):
    # Constantes
    g = 9.81  # m/s², gravidade na Terra
    psi_to_pa = 6894.76  # Conversão de PSI para Pascal
    cm_to_m = 0.01  # Conversão de cm para metros
    if value == None:
        pressure_bottom_data = get_attribute_data('pressure_bottom')
        pressure_middle_data = get_attribute_data('pressure_middle')
    else:
        pressure_bottom_data = value
        pressure_middle_data = value
    # Convertendo pressões de PSI para Pascal
    
    if value == None:
        pressure_bottom = pressure_bottom_data.get('value') * psi_to_pa
        pressure_middle = pressure_middle_data.get('value') * psi_to_pa
    else:
        pressure_bottom = pressure_bottom_data * psi_to_pa
        pressure_middle = pressure_middle_data * psi_to_pa
    
    # Convertendo distância entre os sensores para metros
    distance_sensors = 0.061
    
    # Calculando a pressão diferencial (ΔP) em Pascal
    delta_p = pressure_bottom - pressure_middle
    if delta_p < 0 :
        delta_p = delta_p * -1; 
    
    # Calculando a densidade do líquido (ρ) usando a equação (2)
    rho = delta_p / (g * distance_sensors)
    
    return rho