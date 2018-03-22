from scipy import stats,spatial
from pymongo import MongoClient
from operator import itemgetter
import datetime
client = MongoClient()
db = client.usersbot.usersinfo

#48779981

def getKNeighboursPearson(chatid,k):
    """
    :param chatid: chatid dell'utente su cui si vuole calcolare la similarità
    :param k: massimo numero di utenti simili da restituire
    :return: userdata( chatid e categorie preferite dell'utente), lista di liste contenente il pearson value di ogni altro utente e le categorie preferite
    """
    chatid=str(chatid)

    #estraggo l'utente
    userPearson = db.find({'chatid':chatid})
    if userPearson.count()>0:
        userData = [chatid,normalizeCategoriesValue(userPearson[0]['favouriteCategories']),normalizeCategoriesValue(userPearson[0]['restaurantTags'])]
        #print(userPearson[0]['pearsonValue'])
        neighbours = []
        #estraggo gli altri utenti
        for u in db.find():
            cid = u['chatid']
            if cid != chatid and len(u['favouriteCategories'])>0:
                #print([cid,stats.pearsonr(userPearson[0]['pearsonValue'],u['pearsonValue'])[0],normalizeCategoriesValue(u['favouriteCategories'])])
                neighbours.append([cid,stats.pearsonr(userPearson[0]['pearsonValue'],u['pearsonValue'])[0],normalizeCategoriesValue(u['favouriteCategories']),normalizeCategoriesValue(u['restaurantTags'])])
        #ordino
        neighbours = sorted(neighbours, key=itemgetter(1), reverse=True)

        k = min([k,len(neighbours)])
        #print(neighbours)
        return userData,neighbours[0:k]
    return None

def normalizeCategoriesValue(categoriesArray):
    if len(categoriesArray)==0:
        return []
    value= []
    for c in categoriesArray:
        value.append(c[1])
    normalizeFactor = 5.0/max(value)
    valueNormalized=[]
    for v in categoriesArray:
        valueNormalized.append([v[0],v[1]*normalizeFactor])
    return valueNormalized

def recommendationPearson(chatid,kIn, kOut):
    """
    :param chatid: ChatId dell'utente che vuole la raccomandazione
    :param kIn: Numero di uenti vicini all'utente estratti
    :param kOut: Numero di tipologie di cucina raccomandate
    :return: Array di oggetti-> ['tipologia-cucina', int]
    """

    #estrazione k vicini
    kNeighbours = getKNeighboursPearson(chatid, kIn)


    if kNeighbours is None:
        return []

    #estrazione tipologie di cucina preferite all'utente
    userFavourite = kNeighbours[0][1]
    userTag = kNeighbours[0][2]
    """
    #creazione array di array di questo tipo: [chatid utente, valori tipologie preferite utente iniziale, valore tipologie restanti]
    categories4User = []
    #estraggo gli utenti
    for u in kNeighbours[1]:
        cambiato = False
        u3=[]
        #per ogni tipologia preferita dall'utente
        for t in userFavourite:
            #per ogni tipologia preferita dagli altri utenti
            for t1 in u[2]:
                
                if t[0] == t1[0]:
                    u3.append(t1)
                    cambiato = True
            if not cambiato:
                u3.append([t[0], 0])
            else:
                cambiato = False
        
        categories4User.append([u[0],u3,[item for item in u[2] if item not in u3]])
        u3=[]
"""
    # creazione array di array di questo tipo: [chatid utente, valori tipologie preferite utente iniziale, valore tipologie restanti]
    categories4User = []
    # estraggo gli utenti
    for u in kNeighbours[1]:
        cambiato = False
        cambiatoTag=False
        u3 = []
        tags =[]
        # per ogni tipologia preferita dall'utente
        for t in userFavourite:
            # per ogni tipologia preferita dagli altri utenti
            for t1 in u[2]:
                #se sono uguali le inserisco
                if t[0] == t1[0]:
                    u3.append(t1)
                    cambiato = True
            #se non ho inserito nulla
            if not cambiato:
                u3.append([t[0], 0])
            else:
                cambiato = False
        #per ogni tag dell'utente
        for tag in userTag:
            # per ogni tag dagli altri utenti
            for tag1 in u[3]:
                #se sono uguali le inserisco
                if tag[0] == tag1[0]:
                    tags.append(tag1)
                    cambiatoTag = True
            #se non ho inserito nulla
            if not cambiatoTag:
                tags.append([tag[0], 0])
            else:
                cambiatoTag = False

        categories4User.append([u[0], u3, [item for item in u[2] if item not in u3],tags])
        u3 = []
        tags=[]


    #creazione array utente per il calcolo con pearson
    p=[]
    for f in userFavourite:
        p.append(f[1])
    for t in userTag:
        p.append(t[1])



    if len(p) <= 2:
        if len(p)==1:
            p.append(0)
        p.append(0)


    #creazione array di array di questo tipo: [chatid, valore pearson, tipologie restanti]
    pearsonCategory = []


    for users in categories4User:
        p2=[]
        for f in users[1]:
            p2.append(f[1])
        for t in users[3]:
            p2.append(t[1])
        #print(p,p2)

        if len(p2) <= 2:
            if len(p2) ==1:
                p2.append(0)
            p2.append(0)

        if not all(v == 0 for v in p2):
            #print(p,p2)
            pc = stats.pearsonr(p, p2)
        else:
            pc=(-1.0,0.0)

        topType=[]
        for u in users[2]:
            if u[1]>4.5:
                topType.append(u)

        pearsonCategory.append([users[0],pc[0],topType])

    #ordino la lista in ordine decrescente in base al valore di pearson
    pearsonCategory =  sorted(pearsonCategory, key=itemgetter(1), reverse=True)


    #estrazione delle kOut tipologie di cucina da chi ha il valore di pearson più vicino a 1
    typeRecommendation = []

    for t in pearsonCategory:

        for c in sorted(t[2],key=itemgetter(1),reverse=True):
            if controllaInserimentoTipi(c, typeRecommendation):
                typeRecommendation.append(c)
            if len(typeRecommendation) == kOut:
                return [typeRecommendation,pearsonCategory]


    return [typeRecommendation,pearsonCategory]

def getKNeighboursCosSim(chatid,k):
    """
    :param chatid: chatid dell'utente su cui si vuole calcolare la similarità
    :param k: massimo numero di utenti simili da restituire
    :return: userdata( chatid e categorie preferite dell'utente), lista di liste contenente il pearson value di ogni altro utente e le categorie preferite
    """
    chatid=str(chatid)
    userPearson = db.find({'chatid':chatid})
    if userPearson.count()>0:
        userData = [chatid,normalizeCategoriesValue(userPearson[0]['favouriteCategories'])]
        #print(userPearson[0]['pearsonValue'])
        neighbours = []
        for u in db.find():
            cid = u['chatid']
            if cid != chatid and len(u['favouriteCategories'])>0:
                #print([cid,stats.pearsonr(userPearson[0]['pearsonValue'],u['pearsonValue'])[0],normalizeCategoriesValue(u['favouriteCategories'])])
                neighbours.append([cid,spatial.distance.cosine(userPearson[0]['pearsonValue'],u['pearsonValue']),normalizeCategoriesValue(u['favouriteCategories'])])

        neighbours = sorted(neighbours, key=itemgetter(1), reverse=True)

        k = min([k,len(neighbours)])
        #print(neighbours)
        return userData,neighbours[0:k]
    return None

def recommendationCosSim(chatid,kIn, kOut):
    """
    :param chatid: ChatId dell'utente che vuole la raccomandazione
    :param kIn: Numero di uenti vicini all'utente estratti
    :param kOut: Numero di tipologie di cucina raccomandate
    :return: Array di oggetti-> ['tipologia-cucina', int]
    """

    #estrazione k vicini
    kNeighbours = getKNeighboursCosSim(chatid, kIn)

    if kNeighbours is None:
        return []

    #estrazione tipologie di cucina preferite all'utente
    userFavourite = kNeighbours[0][1]

    #creazione array di array di questo tipo: [chatid utente, valori tipologie preferite utente iniziale, valore tipologie restanti]
    categories4User = []

    for u in kNeighbours[1]:
        cambiato = False
        u3=[]
        for t in userFavourite:
            for t1 in u[2]:
                if t[0] == t1[0]:
                    u3.append(t1)
                    cambiato = True
            if not cambiato:
                u3.append([t[0], 0])
            else:
                cambiato = False

        categories4User.append([u[0],u3,[item for item in u[2] if item not in u3]])
        u3=[]

    #creazione array utente per il calcolo con cosSim
    p=[]
    for f in userFavourite:
        p.append(f[1])

    if len(p) <= 2:
        if len(p)==1:
            p.append(0)
        p.append(0)


    #creazione array di array di questo tipo: [chatid, valore cosSim, tipologie restanti]
    cosSimCategory = []


    for users in categories4User:
        p2=[]
        for f in users[1]:
            p2.append(f[1])


        if len(p2) <= 2:
            if len(p2) ==1:
                p2.append(0)
            p2.append(0)

        if not all(v == 0 for v in p2):
            #print(p,p2)
            pc = spatial.distance.cosine(p, p2)
        else:
            pc=-1.0

        topType=[]
        for u in users[2]:
            if u[1]>4.5:
                topType.append(u)

        cosSimCategory.append([users[0],pc,topType])

    #ordino la lista in ordine decrescente in base al valore di cosSim
    cosSimCategory =  sorted(cosSimCategory, key=itemgetter(1), reverse=True)


    #estrazione delle kOut tipologie di cucina da chi ha il valore di cosSim più vicino a 1
    typeRecommendation = []

    for t in cosSimCategory:

        for c in sorted(t[2],key=itemgetter(1),reverse=True):
            if controllaInserimentoTipi(c,typeRecommendation):
                typeRecommendation.append(c)
            if len(typeRecommendation) == kOut:
                return [typeRecommendation,cosSimCategory]


    return [typeRecommendation,cosSimCategory]


def controllaInserimentoTipi(elem,typeList):
    for t in typeList:
        if elem[0]==t[0]:
            return False
    return True
def recommendation(chatid,kIn, kOut):
    pearson=recommendationPearson(chatid, kIn, kOut)

    return pearson[0]

def saveRecommendationResults(chatid,kIn,kOut):
    pearson=recommendationPearson(chatid, kIn, kOut)
    cosSim = recommendationCosSim(chatid, kIn, kOut)
    client.usersbot.recommendationsResults.insert({'chatid':chatid,'date':datetime.datetime.now(),'pearsonResults':pearson[1],'cosSimResult':cosSim[1]})


