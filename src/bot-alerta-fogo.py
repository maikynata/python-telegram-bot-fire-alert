import requests

baseURL = 'http://queimadas.dgi.inpe.br/queimadas/dados-abertos/api'
pais_id = int(33)
estado_id = int(52)
municipio_id = int(5205307)

coordinatesURL = baseURL + '/focos/?pais_id={}&estado_id={}&municipio_id={}'.format(pais_id, estado_id, municipio_id)
countURL = baseURL + '/focos/count?pais_id={}&estado_id={}&municipio_id={}'.format(pais_id, estado_id, municipio_id)

respCount = requests.get(countURL)
respCoordinates = requests.get(coordinatesURL)

if respCoordinates.status_code != 200 or respCount.status_code != 200:
    # This means something went wrong.
    raise requests.exceptions.RequestException('GET /focos/ {}'.format(respCoordinates.status_code))
    raise requests.exceptions.RequestException('GET /focos/count/ {}'.format(respCount.status_code))
else:
    print("Success")

count = respCount.json()
print('Numero de supostos focos: {}'.format(count['Brasil']))

for todo_item in respCoordinates.json():
    print('municipio = {}, localizacao = {}, {}'.format(todo_item['properties']['municipio'],
                                                        todo_item['properties']['latitude'],
                                                        todo_item['properties']['longitude']))
