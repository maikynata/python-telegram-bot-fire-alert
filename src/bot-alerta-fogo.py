import requests

resp = requests.get('http://queimadas.dgi.inpe.br/queimadas/dados-abertos/api/auxiliar/paises')
if resp.status_code != 200:
    # This means something went wrong.
    raise requests.exceptions.RequestException('GET /auxiliar/paises/ {}'.format(resp.status_code))
for todo_item in resp.json():
    print('{} {}'.format(todo_item['pais_id'], todo_item['pais_name']))

