from pymongo import MongoClient
from operator import itemgetter

class User():
    chatid =""
    name=""
    gender =""
    age = ""
    vehicle =""
    job =""
    favouriteCategories=[]
    pearsonValue=[]
    restaurantTags=[]


    def __init__(self,chatid):
        chatid=str(chatid)

        self.chatid=chatid
        client = MongoClient()
        db = client.usersbot.usersinfo
        user = db.find({'chatid':chatid})
        if user.count()>0:
            user=user[0]
            self.name=user['name']
            self.age=user['age']
            self.gender=user['gender']
            self.vehicle=user['vehicle']
            self.job=user['job']
            self.favouriteCategories=user['favouriteCategories']
            self.pearsonValue=user['pearsonValue']
            self.restaurantTags=user['restaurantTags']

        else:
            db.insert(self.serialize())
        client.close()


    def getName(self):
        return self.name
    def setName(self, name):
        self.name=name
        client = MongoClient()
        db = client.usersbot.usersinfo
        db.update_one({'chatid': self.chatid}, {'$set': {'name': name}}, upsert=False)
        client.close()
    def getGender(self):
        return self.gender
    def setGender(self, gender):
        self.gender=gender
        client = MongoClient()
        db = client.usersbot.usersinfo
        db.update_one({'chatid': self.chatid}, {'$set': {'gender': gender}}, upsert=False)
        client.close()
        self.setPearsonValue()
    def getAge(self):
        return self.age
    def setAge(self, age):
        age = str(age)
        self.age=age
        client = MongoClient()
        db = client.usersbot.usersinfo
        db.update_one({'chatid': self.chatid}, {'$set': {'age': age}}, upsert=False)
        client.close()
        self.setPearsonValue()
    def getVehicle(self):
        return self.vehicle
    def setVehicle(self, vehicle):
        self.vehicle=vehicle
        client = MongoClient()
        db = client.usersbot.usersinfo
        db.update_one({'chatid': self.chatid}, {'$set': {'vehicle': vehicle}}, upsert=False)
        client.close()
        self.setPearsonValue()
    def getJob(self):
        return self.job
    def setJob(self, job):
        self.job=job
        client = MongoClient()
        db = client.usersbot.usersinfo
        db.update_one({'chatid': self.chatid}, {'$set': {'job': job}}, upsert=False)
        client.close()
        self.setPearsonValue()


    def getFavouriteCategories(self):
        return sorted(self.favouriteCategories, key=itemgetter(1), reverse=True)
    def setFavouriteCategories(self,favouriteCategories):
        self.favouriteCategories=favouriteCategories
        client = MongoClient()
        db = client.usersbot.usersinfo
        db.update_one({'chatid': self.chatid}, {'$set': {'favouriteCategories': self.favouriteCategories}}, upsert=False)
        client.close()


    def addFavouriteCategories(self,categoriesArray):
        setted = False
        for ca in categoriesArray:
            for c in self.favouriteCategories:
                if c[0]==ca:
                    c[1]=c[1]+1
                    setted=True
            if not setted:
                self.favouriteCategories.append([ca,1])
            setted=False
        client = MongoClient()
        db = client.usersbot.usersinfo
        db.update_one({'chatid': self.chatid}, {'$set': {'favouriteCategories': self.favouriteCategories}}, upsert=False)
        client.close()

    def getRestaurantTags(self):
        return sorted(self.restaurantTags, key=itemgetter(1), reverse=True)

    def setRestaurantTags(self,restaurantTags):
        self.restaurantTags=restaurantTags
        client = MongoClient()
        db = client.usersbot.usersinfo
        db.update_one({'chatid': self.chatid}, {'$set': {'restaurantTags': self.restaurantTags}}, upsert=False)
        client.close()

    def getTop3Categories(self):
        minimo = min([3,len(self.favouriteCategories)])
        return sorted(self.favouriteCategories, key=itemgetter(1), reverse=True)[0:minimo]



    def isNewUser(self):
        return self.name=="" or self.age=="" or self.gender=="" or self.vehicle=="" or self.job==""

    def setPearsonValue(self):
        if not self.isNewUser():
            genderValue =1
            ageValue=1
            vehicleValue= 1
            jobValue=1

            if self.gender == 'uomo':
                genderValue = 2
            age=int(self.age)
            if age in range(0,18):
                ageValue=1
            elif age in range(18,25):
                ageValue=2
            elif age in range(25,35):
                ageValue=3
            elif age in range(35,45):
                ageValue=4
            elif age in range(45,55):
                ageValue=5
            elif age in range(55,65):
                ageValue=6
            else:
                ageValue=7

        #ciclomotore 50 = 0, automobile = 1, moto = 2, bicicletta = 3, mezzi pubblici = 4

            if self.vehicle=='automobile':
                vehicleValue=2
            elif self.vehicle=='moto':
                vehicleValue=3
            elif self.vehicle=='bicicletta':
                vehicleValue=4
            elif self.vehicle=='mezzi pubblici':
                vehicleValue=5

        #impiegato=0, lavoratore_autonomo=1, disoccupato=2, casalinga=3,studente=4,corpo_militare=5,pensionato=6,altro=7
            if self.job=='lavoratore_autonomo':
                jobValue=2
            elif self.job=='disoccupato':
                jobValue=3
            elif self.job=='casalinga':
                jobValue=4
            elif self.job=='studente':
                jobValue=5
            elif self.job=='corpo_militare':
                jobValue=6
            elif self.job=='pensionato':
                jobValue=7
            elif self.job=='altro':
                jobValue=8


            values=[genderValue,ageValue,vehicleValue,jobValue]
            self.pearsonValue=values
            client = MongoClient()
            db = client.usersbot.usersinfo
            db.update_one({'chatid': self.chatid}, {'$set': {'pearsonValue': values}}, upsert=False)
            client.close()

    def serialize(self):
        return {
            'chatid': self.chatid,
            'name': self.name,
            'gender':self.gender,
            'age':self.age,
            'vehicle':self.vehicle,
            'job':self.job,
            'favouriteCategories':self.favouriteCategories,
            'pearsonValue':self.pearsonValue,
            'restaurantTags':self.restaurantTags
        }

    def __str__(self):
        r = str("ChatId: %s\n" \
            "Nome: %s\n" \
            "Genere: %s\n" \
            "Età: %s\n" \
            "Veicolo: %s\n"
            "Lavoro: %s\n"
            "Categorie preferite: %s" %(self.chatid,self.name,self.gender,self.age,self.vehicle,self.job,self.favouriteCategories))

        return r

#TEST
if __name__ == "__main__":
    client = MongoClient()
    db = client.usersbot.usersinfo
    for u in db.find():
        print(u)
    client.close()


