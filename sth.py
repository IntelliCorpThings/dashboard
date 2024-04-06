import requests

ip = '46.17.108.131'

# Constantes
HEADERS = {'fiware-service': 'smart', 'fiware-servicepath': '/'}

def get_attribute_data(entity, lastN=None):
    """Obtém dados do atributo da API."""
    if lastN is not None:
        url = f"http://{ip}:8666/STH/v1/contextEntities/type/dt/id/urn:ngsi-ld:WineTest:003/attributes/{entity}?lastN={lastN}"
    else:
        url = f"http://{ip}:1026/v2/entities/urn:ngsi-ld:WineTest:003/attrs/{entity}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.HTTPError as http_err:
        return f"Erro HTTP ao obter dados: {http_err}"
    except Exception as err:
        return f"Erro ao obter dados: {err}"

def calc_brix_level():
    g = 9.81  # m/s², gravidade na Terra
    rho_w = 1000  # kg/m³, densidade da água
    delta_h = 0.061  # metros, distância entre os sensores
    psi_to_pa = 6894.76
    
    # Obtendo os valores de pressão
    pressure_bottom_data = get_attribute_data('pressure_bottom')
    pressure_middle_data = get_attribute_data('pressure_middle')

    if isinstance(pressure_bottom_data, dict) and isinstance(pressure_middle_data, dict):
        pressure_bottom = pressure_bottom_data.get('value') * psi_to_pa
        pressure_middle = pressure_middle_data.get('value') * psi_to_pa
        print(pressure_bottom_data.get('value'))
        print(pressure_middle_data.get('value'))
        # Calculando a pressão diferencial (ΔP)
        delta_p = pressure_bottom - pressure_middle
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

def calc_density():
    # Constantes
    g = 9.81  # m/s², gravidade na Terra
    psi_to_pa = 6894.76  # Conversão de PSI para Pascal
    cm_to_m = 0.01  # Conversão de cm para metros
    pressure_bottom_data = get_attribute_data('pressure_bottom')
    pressure_middle_data = get_attribute_data('pressure_middle')
    # Convertendo pressões de PSI para Pascal
    
    pressure_bottom = pressure_bottom_data.get('value') * psi_to_pa
    pressure_middle = pressure_middle_data.get('value') * psi_to_pa
    
    # Convertendo distância entre os sensores para metros
    distance_sensors = 0.061
    
    # Calculando a pressão diferencial (ΔP) em Pascal
    delta_p = pressure_bottom - pressure_middle
    
    # Calculando a densidade do líquido (ρ) usando a equação (2)
    rho = delta_p / (g * distance_sensors)
    
    return rho