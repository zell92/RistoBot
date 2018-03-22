from ResturantData.ResturantAPI import ResturantFacebook
from rippletagger.tagger import Tagger
from pymongo import MongoClient, errors,TEXT, DESCENDING
import string
import re
import xlsxwriter


coordinate = "Latitudine: 41.808019 | Longitudine: 12.436592,Latitudine: 41.805511 | Longitudine: 12.49585,Latitudine: 41.840307 | Longitudine: 12.578247," \
             "Latitudine: 41.898597 | Longitudine: 12.60022,Latitudine: 41.948664 | Longitudine: 12.572754,Latitudine: 41.975215 | Longitudine: 12.512329," \
             "Latitudine: 41.966025 | Longitudine: 12.424438,Latitudine: 41.93232 | Longitudine: 12.385986,Latitudine: 41.90473 | Longitudine: 12.381866," \
             "Latitudine: 41.897575 | Longitudine: 12.434051,Latitudine: 41.903708 | Longitudine: 12.476624,Latitudine: 41.894508 | Longitudine: 12.553528," \
             "Latitudine: 41.859743 | Longitudine: 12.498596"

coordinate= coordinate.split(",")
coordinateList=[]
for a in coordinate:
    a = a.replace("Latitudine:","").replace("Longitudine:","").replace(" ","")
    coordinateList. append(a.split("|"))
#print(coordinateList)


def extractAbout():
    for c in coordinateList:
        latitude = c[0]
        longitude =c[1]
        radius = 2000
        r = ResturantFacebook.RestaurantFacebook()
        r.getRestaurants(lat=latitude, lon=longitude, rag=radius, allRestaurant=False)
        for res in r.restaurants['restaurants']:
            client = MongoClient()
            db = client.usersbot.testRecommendation
            try:
                if 'about' in res:

                    db.insert({'_id': res['id'],'about':strip_punctuation(res['about'].lower())})
            except errors.DuplicateKeyError:
                print("Ristorante già inserito")
            client.close()

def posTagging():
    extractAbout()
    client = MongoClient()
    db = client.usersbot.testRecommendation
    tagger = Tagger(language="it")
    count=0
    for r in db.find():
        count=count+1
        print("ristorante"+str(count))
        id = r['_id']
        tagADJ = []
        tagNOUN = []
        for el in tagger.tag(r['about']):
            if el[1] == 'ADJ':
                tagADJ.append(el[0])
            if el[1] == 'NOUN':
                tagNOUN.append(el[0])
        if len(tagADJ)>0 or len(tagNOUN)>0:
            db.update_one({"_id":id},{"$set": {"tagADJ": tagADJ,"tagNOUN":tagNOUN}})
        else:
            db.remove({'_id':id})
    client.close()


def getTagWords():
    client = MongoClient()
    db1 = client.usersbot.testRecommendation
    db2 = client.usersbot.tagWords
    db2.drop()
    db2.create_index([('word', TEXT)],unique=True)
    tagger = Tagger(language="it")
    count = 1
    for r in db1.find():
        #print(r)
        for adj in r['tagADJ']:
            try:
                db2.insert({'_id': count, 'word': adj,'type':'ADJ', 'count':1})
                count =count+1
            except errors.DuplicateKeyError as e:
                word = str(e).split("{ : ")[1].split(",")[0].replace("\"", "")
                try:
                    id = db2.find({'$text': {'$search':word, '$diacriticSensitive': False}})[0]['_id']
                except IndexError:
                    id = db2.find({'$text': {'$search': adj, '$diacriticSensitive': False}})[0]['_id']
                db2.update_one({"_id": id}, {"$inc": {"count":+1}})
        for noun in r['tagNOUN']:
            try:
                db2.insert({'_id': count, 'word': noun,'type':'NOUN', 'count':1})
                count =count+1
            except errors.DuplicateKeyError as e:
                # coding=utf-8
                #noun = noun.replace("å","à").encode().replace("xa1","xa0").decode()
                word = str(e).split("{ : ")[1].split(",")[0].replace("\"", "")
                try:
                    id = db2.find({'$text': {'$search':word, '$diacriticSensitive': False}})[0]['_id']
                except IndexError:
                    id = db2.find({'$text': {'$search': noun, '$diacriticSensitive': False}})[0]['_id']
                db2.update_one({"_id": id}, {"$inc": {"count": +1}})


    client.close()

def strip_punctuation(s):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    out = regex.sub(' ', s)
    return out

def scriviFile():
    workbook = xlsxwriter.Workbook('aboutTag.xlsx')
    worksheet = workbook.add_worksheet()
    client = MongoClient()
    db = client.usersbot.testRecommendation
    worksheet.write('A1', 'Descrizione')
    worksheet.write('B1', 'Tag Aggettivi')
    worksheet.write('C1', 'Tag Nomi')

    count=2
    for a in db.find():
        print(a)

        worksheet.write('A'+str(count), a['about'])
        worksheet.write('B' + str(count), ",".join(a['tagADJ']))
        worksheet.write('C' + str(count), ",".join(a['tagNOUN']))

        count=count+1

    workbook.close()
    client.close()


def scriviFile2():
    workbook = xlsxwriter.Workbook('tagsFrequency.xlsx')
    worksheet = workbook.add_worksheet()
    client = MongoClient()
    db = client.usersbot.tagWords
    worksheet.write('A1', 'Tag')
    worksheet.write('B1', 'Tipo')
    worksheet.write('C1', 'Frequenza')

    count=2
    for a in db.find().sort( [("count", DESCENDING)] ):
        print(a)

        worksheet.write('A'+str(count), a['word'])
        worksheet.write('B' + str(count),a['type'])
        worksheet.write('C' + str(count), a['count'])

        count=count+1

    workbook.close()
    client.close()
scriviFile2()
#posTagging()
#getTagWords()
#prova()
#print("cinecittå".replace("å","à"))#.decode('utf-8'))
#print (strip_punctuation("cia,sad. mi chiamo .sdada"))
#print(posTagging("ristorante accogliente immerso nel verde della natura, sushi open bar"))