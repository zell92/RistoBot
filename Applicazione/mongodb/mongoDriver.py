import datetime
from pymongo import MongoClient, errors
from model.user import User
from model.operations.sentimentAnalysis import findSentiment
from model.operations.recommendationExtractor import recommendationPearson,recommendationCosSim
from model.operations.tagOperation import tagExtractor
from ResturantData.ResturantAPI.ResturantFacebook import RestaurantFacebook
from bson.objectid import ObjectId
from random import shuffle
from numpy import mean, std,sqrt
from scipy.stats import norm,zscore
from math import pow




def removeRecommendation(chatId):
    chatId=str(chatId)
    client = MongoClient()
    db = client.usersbot
    db.recommendation.remove({'chatid': chatId})
    client.close()

def isName(query):
    client = MongoClient()
    db = client.usersbot
    words = query.title().split()

    name = None
    for w in words:
        nameFind = db.persons.find({"Name": w})
        if db.persons.find({"Name": w}).count() > 0:
            name = nameFind[0]['Name']
    client.close()
    return name


def saveRecommendation(chatid, serializedReasturant):
    client = MongoClient()
    db = client.usersbot
    chatid = str(chatid)
    about=""
    categories=""
    cucina=[]

    if 'category_list' in serializedReasturant:
        categories = serializedReasturant['category_list']
        for c in categories:
            if c['sub_category'] not in cucina:
                cucina.append(c['sub_category'])
            #if c['category'] not in cucina:
                #cucina.append(c['category'])
    db.recommendation.update({'chatid': chatid}, {'$unset': {"facebookRestaurants": "", "yelpRestaurants": ""}})
    db.recommendation.update_one({'chatid': chatid}, {'$set': {'restaurant': serializedReasturant}}, upsert=False)
    db.recommendation.update_one({'chatid': chatid}, {'$set': {'feedback': []}}, upsert=False)

    r = db.recommendation.find({'chatid': chatid})[0]
    print(r)
    db.recommendation.remove({'chatid': chatid})
    db.recommendations.insert(r)
    user = User(chatid)
    tExt = tagExtractor()
    tExt.updateUserTags(chatid,serializedReasturant)
    user.addFavouriteCategories(cucina)
    client.close()


def saveFeedBack(chatid, feedback, date,vote):
    part = date.split(" ")
    part1 = part[0].split("-")
    part3 = part[3].split(".")
    d = datetime.datetime(int(part1[0]), int(part1[1]), int(part1[2]), int(part[1]), int(part[2]), int(part3[0]), int(part3[1]))
    #print(feedback)
    #print(date)
    #print(vote)
    sentiment = findSentiment(feedback)
    print(sentiment)
    realSentiment=0
    vote = int(vote)
    if vote in range(0,5):
        realSentiment=sentiment-1
    elif vote in range (5,7):
        realSentiment=sentiment
    else:
        realSentiment=sentiment+1
    print(realSentiment)
    if realSentiment<-1:
        realSentiment=-1
    if realSentiment>1:
        realSentiment=1

    #set tipologie ristoranti
    #----
    client = MongoClient()
    db = client.usersbot
    user = db.usersinfo.find({'chatid':chatid})[0]
    rec = db.recommendations.find({'chatid': chatid, 'date': d})[0]
    rest = rec["restaurant"]
    category = []
    for c in rest["category_list"]:
        category.append(c["sub_category"])

    tExt = tagExtractor()
    tag = tExt.getRestaurantTag(rest)
    fcs=[]
    rts=[]
    if "favouriteCategories" in user:
        fcs =user["favouriteCategories"]
        print(fcs)
        for i in range(0,len(fcs)):
            fc = fcs[i]
            if fc[0] in category:
                print(fc[1])
                fc[1]=fc[1]+(realSentiment-1)
                fcs[i]=fc
                print(fc[1])

                if fc[1]<0:
                    del fcs[i]
        print(fcs)


    if "restaurantTags" in user:
        rts = user["restaurantTags"]
        print(rts)
        for i in range(0,len(rts)):
            rt = rts[i]
            if rt[0] in tag:
                rt[1] = rt[1] + (realSentiment - 1)
                rts[i] = rt
                if rt[1] < 0:
                    del rts[i]
        print(rts)
    db.usersinfo.update_one({'chatid':chatid},{'$set':{"favouriteCategories":fcs,"restaurantTags":rts}})
    print(category,tag)
    db.recommendations.update_one({'chatid': chatid, 'date': d}, {'$set': {'feedback': [feedback,sentiment,vote,realSentiment]}}, upsert=False)
    client.close()

def savePhoto(chatid,restaurantId):
    client = MongoClient()
    db = client.usersbot
    photoList = db.photoLinks.count({'chatid':chatid})
    if photoList==0:
        rFb = RestaurantFacebook()
        rFb.getPhoto(restaurantId)
        db.photoLinks.insert({"createdAt": datetime.datetime.utcnow(),'chatid':chatid,'links':rFb.photoiD})
        client.close()
        return rFb.photoiD
    else:
        p = db.photoLinks.find({'chatid':chatid})[0]['links']
        client.close()
        return p
def removePhoto(chatid):
    client = MongoClient()
    db = client.usersbot
    db.photoLinks.remove({'chatid':chatid})
    client.close()

def getUsers():
    client = MongoClient()
    db = client.usersbot
    users= db.usersinfo.find()
    client.close()
    return users

def getUser(chatid):
    client = MongoClient()
    db = client.usersbot
    user= db.usersinfo.find({'chatid':chatid})[0]
    client.close()
    return user

def getRecommendations():
    client = MongoClient()
    db = client.usersbot
    recs= db.recommendations.find()
    client.close()
    return recs

def getUserRecommendations(chatid):
    client = MongoClient()
    db = client.usersbot
    userRecs= db.recommendations.find({'chatid':chatid})
    client.close()
    return userRecs

def getRecommendation(id,chatid):
    client = MongoClient()
    db = client.usersbot
    recommendation=db.recommendations.find({'_id':ObjectId(id),'chatid':chatid})
    client.close()
    return recommendation
def getRecommendationsResults():
    client = MongoClient()
    db = client.usersbot
    r = db.recommendationsResults.find()
    client.close()
    return r
def getRecommendationResults(id):
    client = MongoClient()
    db = client.usersbot
    r = db.recommendationsResults.find({'_id':ObjectId(id)})
    client.close()
    return r

def cleanTestUserDB():
    client = MongoClient()
    db = client.usersbot
    users = []
    count = 1
    for u in db.testUser.find():
        if u['completed']==1:
            user = u
            user['_id'] = str(count)
            users.append(u)
            count+=1
    db.testUser.drop()
    for u in users:
        db.testUser.insert(u)
    client.close()

def saveTestUser(form):
    client = MongoClient()
    db = client.usersbot
    cleanTestUserDB()

    #print("testUser"+str(count+1))

    count = db.testUser.count()


    u = User("testUser"+str(count+1))
    u.setName(form['nome'])
    u.setGender(form['sesso'])
    u.setAge(form['eta'].split("-")[1])
    u.setVehicle(form['veicolo'])
    u.setJob(form['lavoro'])
    u.setRestaurantTags([])
    u.setPearsonValue()
    pearson = recommendationPearson("testUser"+str(count+1), 50,10)[0]
    cosSim = recommendationCosSim("testUser"+str(count+1), 50,10)[0]

    user = {'_id': str(count + 1), "chatid": "testUser" + str(count + 1), "name": form['nome'], "gender": form['sesso'],
            "age": form['eta'], "vehicle": form['veicolo'],
            "job": form['lavoro'], 'qualification': form['titolo'],
            'pearsonCat': pearson[0:5], 'cosSimCat':cosSim[0:5], 'restaurantTags':[], 'completed':0}
    db.testUser.insert(user)
    #print(pearson[0:5])
    db.usersinfo.remove({'chatid':"testUser"+str(count+1)})
    client.close()

    return user

def getRestaurantTestList():
    client = MongoClient()
    db = client.usersbot.restaurantForTest
    res = []
    for r in db.find():
        res.append(r)

    shuffle(res)
    client.close()
    return res

def getRecRestaurantList(typeList):
    res=getRestaurantTestList()
    p1 = []
    p2 = []
    p3 = []
    p4 = []
    p5 = []
    other = []
    ordineGiusto=[]
    typeRestaurantList = []
    #divisione ristoranti per categorie
    for r in res:
        cat = []

        for c in r['category_list']:
            cat.append(c['sub_category'])
            cat.append(c['category'])

        if typeList[0] in cat:
            p1.append(r)
        elif typeList[1] in cat:
            p2.append(r)
        elif typeList[2] in cat:
            p3.append(r)
        elif typeList[3] in cat:
            p4.append(r)
        elif typeList[4] in cat:
            p5.append(r)
        else:
            other.append(r)
    #inserimento di 5 ristoranti non consigliati
    for i in range(0, min(len(other), 5)):
        typeRestaurantList.append(other[i])
        ordineGiusto.append([other[i]['id'], 0])
    #inserimento di restanti ristoranti consigliati
    count = 0
    while len(typeRestaurantList) <= 10:
        if len(p1) > count:
            typeRestaurantList.append(p1[count])
        if len(p2) > count:
            typeRestaurantList.append(p2[count])
        if len(p3) > count:
            typeRestaurantList.append(p3[count])
        if len(p4) > count:
            typeRestaurantList.append(p4[count])
        if len(p5) > count:
            typeRestaurantList.append(p5[count])
        count = count + 1
    #la lista ottenuta conterrà solo 10 elemrnti
    typeRestaurantList = typeRestaurantList[0:10]
    #creazione della lista per il calcolo di precision e recall
    for r in typeRestaurantList:
        if [r['id'],0] not in ordineGiusto:
            ordineGiusto.append([r['id'],5])
    shuffle(typeRestaurantList)
    typeRestaurantList = [typeRestaurantList, ordineGiusto]
    return typeRestaurantList


def getNearestRestaurantList():
    res = getRestaurantTestList()
    nearest=[]
    furthest=[]
    ordineGiusto=[]
    restaurantList=[]
    for r in res:
        dist=r['distance']
        if dist<0.1:
            nearest.append(r)
        if dist>1.850:
            furthest.append(r)
    shuffle(nearest)
    shuffle(furthest)
    nearest=nearest[0:5]
    furthest=furthest[0:5]
    for r in nearest:
        restaurantList.append(r)
        ordineGiusto.append([r['id'],5])
    for r in furthest:
        restaurantList.append(r)
        ordineGiusto.append([r['id'],0])
    shuffle(restaurantList)

    return [restaurantList,ordineGiusto]

def getVoteRestaurantList():
    res = getRestaurantTestList()
    hVote=[]
    lVote=[]
    ordineGiusto=[]
    restaurantList=[]
    for r in res:
        vote=r['overall_star_rating']
        if vote>4.9:
            hVote.append(r)
        if vote<3.7:
            lVote.append(r)
    shuffle(hVote)
    shuffle(lVote)
    hVote=hVote[0:5]
    lVote=lVote[0:5]
    for r in hVote:
        restaurantList.append(r)
        ordineGiusto.append([r['id'],5])
    for r in lVote:
        restaurantList.append(r)
        ordineGiusto.append([r['id'],0])
    shuffle(restaurantList)

    return [restaurantList,ordineGiusto]

def updateTestUser(id,field,value):
    client = MongoClient()
    db = client.usersbot
    id=str(id)
    db.testUser.update({'_id': id}, {'$set': {field: value}})
    client.close()

def getTestResults():
    client = MongoClient()
    db = client.usersbot
    u = []
    for user in db.testUser.find():
        if user['completed']==1:
            u.append(user)

    client.close()
    return u

def getPrecisionRecallTest():
    client = MongoClient()
    db = client.usersbot.testUser
    result = []
    for u in db.find({'completed':1}):
        migliorRaccomandazione = "indifferente"
        if u['completed'] == 1:
            if u['pearsonRacOpinion'] > u['cosSimRacOpinion']:
                migliorRaccomandazione = ("pearson")
            elif u['pearsonRacOpinion'] < u['cosSimRacOpinion']:
                migliorRaccomandazione = ("cossim")
    ### CALCOLO PRECISION E RECALL PEARSON
            pearsonRest = u['pearsonRest']
            pearsonRestByUser = u['pearsonRestByUser']
            # 5 e hanno ricevuto voto da 3 a 5
            vp = 0
            # 0 e hanno ricevuto voto da 1 a 2
            vp2 = 0
            #elementi raccomandati
            countRec=0

            for r in pearsonRest:
                if r[1] > 0:
                    countRec+=1
                    if int(pearsonRestByUser[r[0]][0]) in [3, 4, 5]:
                        vp += 1
                else:
                    if int(pearsonRestByUser[r[0]][0]) in [1, 2]:
                        vp2 += 1

            precisionPearson = vp/countRec
            recallPearson = (vp+vp2)/10

    ### CALCOLO PRECISION E RECALL COSENO SIMILARITà

            cosSimRest = u['cosSimRest']
            cosSimRestByUser = u['cosSimRestByUser']
            # 5 e hanno ricevuto voto da 3 a 5
            vp = 0
            # 0 e hanno ricevuto voto da 1 a 2
            vp2 = 0
            # elementi raccomandati
            countRec = 0

            for r in cosSimRest:
                if r[1] > 0:
                    countRec+=1
                    if int(cosSimRestByUser[r[0]][0]) in [3, 4, 5]:
                        vp += 1
                else:
                    if int(cosSimRestByUser[r[0]][0]) in [1, 2]:
                        vp2 += 1

            precisionCosSim = vp/countRec
            recallCosSim = (vp+vp2)/10

            ### CALCOLO PRECISION E RECALL VICINANZA

            distanceRest = u['distanceRest']
            distanceRestByUser = u['distanceRestByUser']
            # 5 e hanno ricevuto voto da 3 a 5
            vp = 0
            # 0 e hanno ricevuto voto da 1 a 2
            vp2 = 0
            # elementi raccomandati
            countRec = 0

            for r in distanceRest:
                if r[1] > 0:
                    countRec += 1
                    if int(distanceRestByUser[r[0]][0]) in [3, 4, 5]:
                        vp += 1
                else:
                    if int(distanceRestByUser[r[0]][0]) in [1, 2]:
                        vp2 += 1

            precisionDistance = vp / countRec
            recallDistance = (vp+vp2) / 10

            ### CALCOLO PRECISION E RECALL VOTO

            voteRest = u['voteRest']
            voteRestByUser = u['voteRestByUser']
            # 5 e hanno ricevuto voto da 3 a 5
            vp = 0
            # 0 e hanno ricevuto voto da 1 a 2
            vp2 = 0
            # elementi raccomandati
            countRec = 0

            for r in voteRest:
                if r[1] > 0:
                    countRec += 1
                    if int(voteRestByUser[r[0]][0]) in [3, 4, 5]:
                        vp += 1
                else:
                    if int(voteRestByUser[r[0]][0]) in [1, 2]:
                        vp2 += 1

            precisionVote = vp / countRec
            recallVote = (vp+vp2) / 10
            # se precision 1 --> i ristoranti consigliati piacciono all'utente
            # se recall 1 --> i ristoranti consigliati piacciono all'utente e gli altri no
            res = {'_id': u['_id'],
                   'preferRaccomandation': migliorRaccomandazione,
                   'precision_recallPearson': [precisionPearson, recallPearson],
                   'precision_recallCosSim': [precisionCosSim, recallCosSim],
                   'precision_recallDistance': [precisionDistance, recallDistance],
                   'precision_recallVote':[precisionVote,recallVote]}

            result.append(res)
    client.close()
    preferRaccomandation=[0,0,0]
    precision_recallPearson=[[],[]]
    precision_recallCosSim=[[],[]]
    precision_recallDistance=[[],[]]
    precision_recallVote=[[],[]]
    for r in result:
        if r['preferRaccomandation']=="pearson":
            preferRaccomandation[0]+=1
        elif r['preferRaccomandation']=="cossim":
            preferRaccomandation[1]+=1
        else:
            preferRaccomandation[2]+=1
        precision_recallPearson[0].append(r['precision_recallPearson'][0])
        precision_recallPearson[1].append(r['precision_recallPearson'][1])
        precision_recallCosSim[0].append(r['precision_recallCosSim'][0])
        precision_recallCosSim[1].append(r['precision_recallCosSim'][1])
        precision_recallDistance[0].append(r['precision_recallDistance'][0])
        precision_recallDistance[1].append(r['precision_recallDistance'][1])
        precision_recallVote[0].append(r['precision_recallVote'][0])
        precision_recallVote[1].append(r['precision_recallVote'][1])

    data =[list(precision_recallPearson),list(precision_recallCosSim),list(precision_recallDistance),list(precision_recallVote)]

    precision_recallPearson[0]=round(mean(precision_recallPearson[0]),2)
    precision_recallPearson[1] = round(mean(precision_recallPearson[1]),2)
    precision_recallCosSim[0] = round(mean(precision_recallCosSim[0]),2)
    precision_recallCosSim[1] = round(mean(precision_recallCosSim[1]),2)
    precision_recallDistance[0] = round(mean(precision_recallDistance[0]),2)
    precision_recallDistance[1] = round(mean(precision_recallDistance[1]),2)
    precision_recallVote[0] = round(mean(precision_recallVote[0]),2)
    precision_recallVote[1] = round(mean(precision_recallVote[1]),2)

    return [result,preferRaccomandation,precision_recallPearson,precision_recallCosSim,precision_recallDistance,precision_recallVote,data]
    
def getFMeasure():

    precRec = getPrecisionRecallTest()[6]
    pearson = precRec[0]
    cosSim = precRec[1]
    distance = precRec[2]
    vote = precRec[3]
    fP=[]
    fC=[]
    fD=[]
    fV=[]
    for i in range(0,len(pearson[0])):
        denP = pearson[0][i]+pearson[1][i]
        if denP==0:
            fP.append(0)
        else:
            fP.append(round(((2*pearson[0][i]*pearson[1][i])/(denP)),2))
        denC=(cosSim[0][i] + cosSim[1][i])
        if denC==0:
            fC.append(0)
        else:
            fC.append(round(((2 * cosSim[0][i] * cosSim[1][i]) / denC ),2))
        denD=(distance[0][i] + distance[1][i])
        if denD==0:
            fD.append(0)
        else:
            fD.append(round(((2 * distance[0][i] * distance[1][i]) / denD),2))
        denV=(vote[0][i] + vote[1][i])
        if denV==0:
            fV.append(0)
        else:
            fV.append(round(((2 * vote[0][i] * vote[1][i]) / denV),2))
    data = [fP,fC,fD,fV]
    return [round(mean(data[0]),2),round(mean(data[1]),2),round(mean(data[2]),2),round(mean(data[3]),2),data]
def getSE():
    data = getFMeasure()[4]
    pc=[]
    pd=[]
    pv=[]
    for i in range(0,40):
        pc.append(data[0][i]-data[1][i])
        pd.append(data[0][i] - data[2][i])
        pv.append(data[0][i] - data[3][i])
    sdPC = std(pc)
    sePC = (sqrt(40)*sdPC)/40
    sdPD = std(pd)
    sePD = (sqrt(40) * sdPD) / 40
    sdPV=std(pv)
    sePV = (sqrt(40) * sdPV) / 40

    return [sePC,sePD,sePV]
def testZ():
    fMeasure=getFMeasure()
    se = getSE()
    diffPC = fMeasure[0] - fMeasure[1]
    zPC = (diffPC)/se[0]
    diffPD = fMeasure[0] - fMeasure[2]
    zPD = (diffPC)/se[1]
    diffPV = fMeasure[0] - fMeasure[3]
    zPV = diffPV/se[2]
    pValuePC = norm.cdf(zPC) * 100
    pValuePD = norm.cdf(zPD) * 100
    pValuePV = norm.cdf(zPV) * 100
    return [[zPC,pValuePC],[zPD,pValuePD],[zPV,pValuePV]]

def avonaTest():
    fMeasure = getFMeasure()[4]
    count = 40
    fMediaP = mean(fMeasure[0])
    fMediaC = mean(fMeasure[1])
    fMediaD = mean(fMeasure[2])
    fMediaV = mean(fMeasure[3])
    fMediaTot = mean([fMediaP,fMediaC,fMediaD,fMediaV])
    print(round(fMediaP,3),round(fMediaC,3),round(fMediaD,3),round(fMediaV,3),round(fMediaTot,3))

    sdP = std(fMeasure[0])
    sdC = std(fMeasure[1])
    sdD = std(fMeasure[2])
    sdV = std(fMeasure[3])
    sdTot = mean([sdP,sdC,sdD,sdV])

    print(round(sdP,3),round(sdC,3),round(sdD,3),round(sdV,3),round(sdTot,3))

    g1=count*pow(fMediaP-fMediaTot,2)
    g2=count*pow(fMediaC-fMediaTot,2)
    g3=count*pow(fMediaD-fMediaTot,2)
    g4=count*pow(fMediaV-fMediaTot,2)
    ssqA = g1+ g2+g3+g4
    print(round(g1,3),round(g2,3),round(g3,3),round(g4,3),round(ssqA,3))

    ssqE = 0
    for f in fMeasure:
        x=ssqE
        for fi in f:
            ssqE += pow(fi-mean(f),2)
        print(round(ssqE-x,3))
    print(round(ssqE,3))
    fTest = (ssqA/3)/(ssqE/156)
    fcrit = 2.66
    return round(fTest,3)


    return fMeasure
# TEST
if __name__ == "__main__":

    print(avonaTest())




