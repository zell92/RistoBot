import json
import datetime
import model.operations.weatherExtractor as we
from model.user import User
from model.operations import recommendationExtractor
from pymongo import MongoClient
from operator import itemgetter




class Recommendation():
    date = datetime.datetime.now()
    cucina = []
    time_pasto = ""
    location = ""
    weather = ""
    prezzo = ""
    raggio = ""
    tipologia_pasto = ""
    facebookRestaurants = []
    yelpRestaurants = []
    typeRecommendation = []

    def __init__(self, chatid):
        self.chatid = str(chatid)
        client = MongoClient()
        db = client.usersbot.recommendation
        recommendation = db.find({'chatid':self.chatid})
        if recommendation.count() > 0:
            recommendation = recommendation[0]
            self.setDate(recommendation['date'])
            self.setCucina(recommendation['cucina'])
            self.setTime_Pasto(recommendation['time_pasto'])
            self.setLocation(recommendation['location'])
            self.setPrezzo(recommendation['prezzo'])
            self.setRaggio()
            self.setTipologia_Pasto(recommendation['tipologia_pasto'])
            self.setFacebookRestaurants(recommendation['facebookRestaurants'])
            self.setYelpRestaurants(recommendation['yelpRestaurants'])
            self.typeRecommendation=recommendation['typeRecommendation']
        else:
            self.typeRecommendation = recommendationExtractor.recommendation(self.chatid, 50, 10)
            print(self.typeRecommendation)
            db.insert(self.serialize())
        client.close()


    def getDate(self):
        return self.date
    def setDate(self,date):
        self.date=date
        client = MongoClient()
        db = client.usersbot.recommendation
        db.update_one({'chatid': self.chatid}, {'$set': {'date': date}}, upsert=False)
        client.close()

    def getCucina(self):
        return self.cucina
    def setCucina(self,cucina):
        if 'ristorante' in cucina and len(cucina)>1:
            cucina.remove('ristorante')
        self.cucina=cucina
        client = MongoClient()
        db = client.usersbot.recommendation
        db.update_one({'chatid': self.chatid}, {'$set': {'cucina': cucina}}, upsert=False)
        client.close()

    def getTime_Pasto(self):
        return self.time_pasto
    def setTime_Pasto(self,time_pasto):
        self.time_pasto=time_pasto
        client = MongoClient()
        db = client.usersbot.recommendation
        db.update_one({'chatid': self.chatid}, {'$set': {'time_pasto': time_pasto}}, upsert=False)
        client.close()

    def getLocation(self):
        return self.location
    def setLocation(self,location):
        self.location=location
        client = MongoClient()
        db = client.usersbot.recommendation
        db.update_one({'chatid': self.chatid}, {'$set': {'location': location}}, upsert=False)
        client.close()

        self.setWeather()
    def getWeather(self):
        return self.weather
    def setWeather(self):
        if (len(self.location) != 0):
            self.weather = we.getWeather(longitude=str(self.location['longitude']),latitude=str(self.location['latitude']))
            client = MongoClient()
            db = client.usersbot.recommendation
            db.update_one({'chatid': self.chatid}, {'$set': {'weather': self.weather}}, upsert=False)
            client.close()

    def getPrezzo(self):
        return self.prezzo
    def setPrezzo(self,prezzo):
        self.prezzo=prezzo
        client = MongoClient()
        db = client.usersbot.recommendation
        db.update_one({'chatid': self.chatid}, {'$set': {'prezzo': prezzo}}, upsert=False)
        client.close()

    def getRaggio(self):
        return self.raggio
    def setRaggio(self):
        user = User(self.chatid)
        if not user.isNewUser():
            veicolo = user.getVehicle()
            #print(veicolo)
            if veicolo == "automobile" or veicolo == "moto":
                self.raggio= "2000"
            else:
                self.raggio = "1000"
        else:
            self.raggio= "1000"
        client = MongoClient()
        db = client.usersbot.recommendation
        db.update_one({'chatid': self.chatid}, {'$set': {'raggio': self.raggio}}, upsert=False)
        client.close()

    def getTipologia_Pasto(self):
        return self.tipologia_pasto
    def setTipologia_Pasto(self,tipologia_pasto):
        self.tipologia_pasto=tipologia_pasto
        client = MongoClient()
        db = client.usersbot.recommendation
        db.update_one({'chatid': self.chatid}, {'$set': {'tipologia_pasto': tipologia_pasto}}, upsert=False)
        client.close()

    def getTopFiveRecommendation(self):
        userFavorite = User(self.chatid).getFavouriteCategories()
        count = 0
        typeToRecommend = []
        for u in sorted(userFavorite, key=itemgetter(1), reverse=True):
            count+=1
            typeToRecommend.append(u[0])
            if count == 3:
                break
        print("cucine scelte utente")
        print(typeToRecommend)
        count = 0
        maxCount = 5 - len(typeToRecommend)
        for u in self.typeRecommendation:
            count = count + 1
            #print(u)
            if u[0] not in typeToRecommend:
                typeToRecommend.append(u[0])
            #print(u[0])
            if count == maxCount:
                break
        print("scelte finali")
        print(typeToRecommend)
        return typeToRecommend
    def getFacebookRestaurants(self):
        user=User(self.chatid)
        userFavorite = user.getFavouriteCategories()
        userTime = self.getTime_Pasto()
        res=[]
        if len(userTime)>0:
            orario=0
            if userTime=="cena":
                orario=20
            else:
                orario=13

            print(userTime)
            print(len(self.facebookRestaurants))



            for r in self.facebookRestaurants:
                if 'hours' in r:
                    day = datetime.datetime.now()
                    day = day.strftime("%A").lower()[0:3]


                    if day+'_1_open' in r['hours']:
                        aperto = int(r['hours'][day+'_1_open'].split(":")[0])
                        chiuso = int(r['hours'][day+'_1_close'].split(":")[0])
                        if not(aperto<=orario and chiuso>=orario):

                            if day+'_2_open' in r['hours']:
                                aperto = int(r['hours'][day+'_2_open'].split(":")[0])
                                chiuso = int(r['hours'][day+'_2_close'].split(":")[0])
                                if  (aperto <= orario and chiuso >= orario):

                                    res.append(r)

                        else:
                            res.append(r)


            self.setFacebookRestaurants(res)



        if len(self.cucina) >0:
            l=[]
            for r in self.facebookRestaurants:
                if self.isCucina(r):
                    l.append(r)
            return l

        else:

            userFavorite = User(self.chatid).getFavouriteCategories()
            allCat = []
            for cats in self.facebookRestaurants:
                for cat in cats['category_list']:
                    allCat.append(cat['sub_category'])
                    allCat.append(cat['category'])

            s = set(allCat)
            result = sorted(list(s))


            count=0
            typeToRecommend=[]
            for u in sorted(userFavorite, key=itemgetter(1),reverse=True):

                if u[0] in result:
                    count=count+1
                    typeToRecommend.append(u[0])
                if count == 3:
                    break
            count=0
            maxCount = 5-len(typeToRecommend)
            for u in sorted(self.typeRecommendation, key=itemgetter(1),reverse=True):
                if u[0] in result and u[0] not in typeToRecommend:
                    count=count+1
                    typeToRecommend.append(u[0])
                if count == maxCount:
                    break

            l1=[]
            l2=[]
            l3=[]
            l4=[]
            l5=[]

            for i in range(0,len(typeToRecommend)):
                for f in self.facebookRestaurants:
                    for c in f['category_list']:
                        if typeToRecommend[i] in c['sub_category'] or typeToRecommend[i] in c['category']:
                            if i==0:
                                l1.append(f)
                            elif i ==1:
                                l2.append(f)
                            elif i==2:
                                l3.append(f)
                            elif i==3:
                                l4.append(f)
                            else:
                                l5.append(f)
                            self.facebookRestaurants.remove(f)
                            break
            finalList=[]
            maxLen= max([len(l1),len(l2),len(l3),len(l4),len(l5)])
            for i in range(0,maxLen):
                if len(l1)>i:
                    finalList.append(l1[i])
                if len(l2) > i :
                    finalList.append(l2[i])
                if len(l3) > i :
                    finalList.append(l3[i])
                if len(l4) > i :
                    finalList.append(l4[i])
                if len(l5) > i:
                    finalList.append(l5[i])
            finalList.extend(self.facebookRestaurants)

            finalType = []
            for i in typeToRecommend:
                finalType.append([i,1])
            self.setTypeRecommendation(finalType)


            return finalList

    def setFacebookRestaurants(self, facebookRestaurants):
        self.facebookRestaurants=facebookRestaurants
        client = MongoClient()
        db = client.usersbot.recommendation
        db.update_one({'chatid': self.chatid}, {'$set': {'facebookRestaurants': facebookRestaurants}}, upsert=False)
        client.close()

    def isCucina(self,facebookRestaurant):
        for c in self.cucina:
            for cat in facebookRestaurant['category_list']:
                if c == cat['sub_category'] or c == cat['category']:
                    return True
        return False
    def getYelpRestaurants(self):
        return self.yelpRestaurants
    def setYelpRestaurants(self,yelpRestaurants):
        self.yelpRestaurants=yelpRestaurants
        client = MongoClient()
        db = client.usersbot.recommendation
        db.update_one({'chatid': self.chatid}, {'$set': {'yelpRestaurants': yelpRestaurants}}, upsert=False)
        client.close()

    def getTypeRecommendation(self):
        return self.typeRecommendation
    def setTypeRecommendation(self,typeList):
        client = MongoClient()
        db = client.usersbot.recommendation
        db.update_one({'chatid': self.chatid}, {'$set': {'typeRecommendation': typeList}}, upsert=False)
        client.close()
        self.typeRecommendation=typeList

    def setValue(self,nameValue, value):

        nameValue=str(nameValue)
        value=str(value)
        client = MongoClient()
        db = client.usersbot.recommendation
        setted = db.recommendation.update_one({
            'chatid': self.chatId
        }, {
            '$set': {
                nameValue: value
            }
        }, upsert=False)
        client.close()
        return setted





    def json2Object(self,json):
        self.chatid = json['chatid']
        self.date = json['date']
        self.cucina = json['cucina']
        self.time_pasto = json['time_pasto']
        self.location = json['location']
        self.weather = json['weather']
        self.prezzo = json['prezzo']
        self.raggio = json['raggio']
        self.tipologia_pasto = json['tipologia_pasto']


    def serialize(self):
        a={'chatid': self.chatid, 'date': self.date, 'time_pasto': self.time_pasto, 'cucina': self.cucina, 'location':self.location,
           'weather':self.weather, 'prezzo':self.prezzo,'raggio':self.raggio,'tipologia_pasto':self.tipologia_pasto, 'facebookRestaurants': self.facebookRestaurants,
           'yelpRestaurants':self.yelpRestaurants, 'typeRecommendation':self.typeRecommendation}
        return a

#TEST
if __name__ == "__main__":
    r = Recommendation(48779981)
    print(r.facebookRestaurants)