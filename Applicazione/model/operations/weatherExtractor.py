import requests
import json
def getWeather(latitude,longitude):
    url = "http://query.yahooapis.com/v1/public/yql?q=select * from weather.forecast where woeid in (SELECT woeid FROM geo.places WHERE text=\"("+latitude+","+longitude+")\")" \
                "&format=json&lang"

    r = requests.get(url)
    risp = json.dumps(r.json(), indent=4)

    risp=json.loads(risp)
    return risp['query']['results']['channel']['item']['condition']['text']


