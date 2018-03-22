from pymongo import MongoClient
client = MongoClient()
db = client.usersbot.usersinfo
from model import user
from random import randint

tipologie = "all_you_can_eat,brunch,cena,cucina_afgana,cucina_africana,cucina_americana,cucina_araba,cucina_armena,cucina_asiatica,cucina_australiana," \
            "cucina_basca,cucina_belga,cucina_birmana,cucina_britannica,cucina_bulgara,cucina_cambogiana,cucina_canadese,cucina_caraibica,cucina_catalana," \
            "cucina_ceca,cucina_centroeuropea,cucina_cinese,cucina_coreana,cucina_creola_e_cajun,cucina_dello_sri_lanka,cucina_esteuropea,cucina_filippina," \
            "cucina_francese,cucina_fusion_asiatica,cucina_giapponese,cucina_greca,cucina_halal,cucina_hawaiana,cucina_himalayana/nepalese,cucina_indiana," \
            "cucina_indonesiana,cucina_irlandese,cucina_italiana,cucina_latino-americana,cucina_malese,cucina_marocchina,cucina_mediorientale," \
            "cucina_mediterranea,cucina_mongola,cucina_nordeuropea,cucina_pachistana,cucina_persiana/iraniana,cucina_polacca,cucina_polinesiana," \
            "cucina_portoghese,cucina_romena,cucina_russa,cucina_scandinava,cucina_scozzese,cucina_singaporiana,cucina_siriana,cucina_slovacca,cucina_spagnola," \
            "cucina_sudamericana,cucina_sudeuropea,cucina_svizzera,cucina_taiwanese,cucina_tedesca,cucina_thailandese,cucina_turca,cucina_ucraina,cucina_ungherese," \
            "cucina_uzbeka,cucina_vietnamita,fonduta,insalate,panini_e_sandwich,pesce,pizza,pub,ristorante,senza_glutine,steak_house,vegetariano_e_vegano,zuppa".split(",")

def userGenerator():
    for i in range(0, 200):
        u = user.User('user' + str(i))
        u.setName('user' + str(i))
        u.setGender(randomGender())
        u.setAge(randint(18, 90))
        u.setVehicle(randomVeichle())
        u.setFavouriteCategories(randomCategories())
        u.setJob(randomJob())
        print(u)

def randomGender():
    n = randint(0,1)
    if n is 0:
        return 'uomo'
    else:
        return 'donna'
def randomVeichle():

    n = randint(0,4)
    if n==0:
        return 'ciclomotore 50'
    if n==1:
        return 'automobile'
    if n == 2:
        return 'moto'
    if n == 3:
        return 'bicicletta'
    if n == 4:
        return 'mezzi pubblici'

def randomJob():
    n=randint(0,7)
    if n==0:
        return 'impiegato'
    elif n==1:
        return 'lavoratore_autonomo'
    elif n==2:
        return 'disoccupato'
    elif n==3:
        return 'casalinga'
    elif n==4:
        return 'studente'
    elif n==5:
        return 'corpo_militare'
    elif n==6:
        return 'pensionato'
    elif n==7:
        return 'altro'

def randomCategories():
    restaurants = randint(7,30)
    categories = []
    t = list(tipologie)
    a=[]
    t.extend(a)

    for i in range(0,restaurants):
        max = len(t)-1
        n=randint(0,max)

        type= t[n]
        a.append(type)
        t.remove(type)
        categories.append([type,randint(1,15)])
    return categories


userGenerator()
