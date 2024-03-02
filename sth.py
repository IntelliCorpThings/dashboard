import requests

ip = '34.95.217.0'

# Constantes
HEADERS = {'fiware-service': 'smart', 'fiware-servicepath': '/'}

def get_attribute_data(entity, lastN=None):
    """Obtém dados do atributo da API."""
    if lastN is not None:
        url = f"http://{ip}:8666/STH/v1/contextEntities/type/dt/id/urn:ngsi-ld:wine:001/attributes/{entity}?lastN={lastN}"
    else:
        url = f"http://{ip}:1026/v2/entities/urn:ngsi-ld:wine:001/attrs/{entity}"
    result = None
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        result = response.json()
    except requests.HTTPError as http_err:
        result = f"Erro HTTP ao obter dados: {http_err}"
    except Exception as err:
        result = f"Erro ao obter dados: {err}"
    finally:
        return result

if __name__ == '__main__':
    attribute_data = get_attribute_data("tempext")
    print(attribute_data)