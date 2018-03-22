from operator import itemgetter
import requests
import json
from math import radians, cos, sin, asin, sqrt
from pymongo import MongoClient
from Config import config


class RestaurantFacebook():
    CLIENT_ID = config.CLIENT_ID
    CLIENT_SECRET = config.CLIENT_SECRET
    accessToken=""
    restaurants = ""
    restaurantsIds=[]
    events = []
    photoiD=[]

    def __init__(self):
        self.autenticazione()
        self.restaurants = ""
        self.restaurantsIds = []
        self.events = []
        self.photoiD = []

    def autenticazione(self):
        url="https://graph.facebook.com/v2.11/oauth/access_token?"
        payload = {'client_id': self.CLIENT_ID,'client_secret': self.CLIENT_SECRET, 'grant_type':'client_credentials'}

        r=requests.post(url,data=payload)
        risp=json.loads(json.dumps(r.json(),indent=4))
        self.accessToken= risp['access_token']

    def getRestaurants(self,lat,lon,rag):

        client = MongoClient()
        db2 = client.usersbot.restaurantMoneyAndVote
        rag=float(rag)/1000
        lat = str(lat)
        lon = str(lon)
        restaurants = []
        for r in db2.find():
            lat2 = r['location']['latitude']
            lon2=r['location']['longitude']
            distance = self.haversine(lon,lat,lon2,lat2)
            if distance<=rag:
                r['distance']=distance
                restaurants.append([r,distance])
        restaurants = sorted(restaurants, key=itemgetter(1))
        restaurants=  [i[0] for i in restaurants]
        self.restaurants={'restaurants':restaurants}
        client.close()




    def getPhoto(self,restaurantId):

        url="https://graph.facebook.com/v2.11/"+restaurantId+"/photos?type=uploaded"
        payload={'access_token':self.accessToken}

        r= requests.get(url=url,params=payload)
        risp=json.loads(json.dumps(r.json(),indent=4))
        if 'data' in risp:
            data = risp['data']
            for d in data:
                self.photoiD.append("https://graph.facebook.com/"+d['id']+"/picture?type=normal")
            self.searchPhoto(r.json())
        else:
            print("id error")
            print(risp)
            self.getPhoto(restaurantId)



    def searchPhoto(self,result):
        r=result
        if 'paging' in r:
            paging = r['paging']
            if 'next' in paging:
                next = paging['next']
                r = requests.get(url=next)
                risp =r.json()
                if 'data' in risp:
                    data=risp['data']
                    for d in data:
                        self.photoiD.append("https://graph.facebook.com/"+d['id']+"/picture?type=normal")
                        if len(self.photoiD)>=100:
                            return


                        #print(risp)
                    #salva i risultati
                    self.searchPhoto(risp)
                else:
                    print("id error")
                    print(risp)
                    self.searchPhoto(result)

    def extractForRecommendation(self,rac):

        location = rac.getLocation()
        if location is not "":
            raggio = rac.getRaggio()
            self.getRestaurants(lon=location['longitude'],lat=location['latitude'],rag=raggio)
            lista = self.restaurants['restaurants']
            rac.setFacebookRestaurants(lista)
        else:
            rac.setFacebookRestaurants([])


    def haversine(self,lon1, lat1, lon2, lat2):
        lon1=float(lon1)
        lat1=float(lat1)
        lon2=float(lon2)
        lat2=float(lat2)
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers is 6371
        km = 6371 * c
        return km

    def convertCategory(self,resturantFacebook):
        client = MongoClient()
        db = client.usersbot.facebookCategories
        categories = resturantFacebook['category_list']
        category_list=[]
        cambiato = False
        for c in categories:
            val = c['name']
            q=db.find({'old_category':val})
            if q.count()>0:
                cambiato=True
                category_list.append(q[0])
        client.close()
        if cambiato:
            #sostitituisco
            resturantFacebook.update({'category_list': category_list})
            return resturantFacebook
        else:
            return None



if __name__ == "__main__":
    #test
    print("ciao")
