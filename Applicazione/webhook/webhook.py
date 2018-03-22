from __future__ import print_function
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, json, make_response
from mongodb import mongoDriver
from model.user import User
from model.recommendation import Recommendation
import json
import re
from random import shuffle


app = Flask(__name__)

@app.route('/',methods=['GET'])
def home():
    usersTest = mongoDriver.getTestResults()
    age={}
    gender ={}
    vehicle={}
    job={}
    qualification={}
    a=[]
    g=[]
    v=[]
    j=[]
    q=[]
    for u in usersTest:
        if u['age'] in age:
            age[u['age']]=age[u['age']]+1
        else:
            age[u['age']]=1
        if u['gender'] in gender:
            gender[u['gender']]=gender[u['gender']]+1
        else:
            gender[u['gender']]=1
        if u['vehicle'] in vehicle:
            vehicle[u['vehicle']]=vehicle[u['vehicle']]+1
        else:
            vehicle[u['vehicle']]=1
        if u['job'] in job:
            job[u['job']]=job[u['job']]+1
        else:
            job[u['job']]=1

        if u['qualification'] in qualification:
            qualification[u['qualification']]=qualification[u['qualification']]+1
        else:
            qualification[u['qualification']]=1

    for key in age.keys():
        a.append([key,age[key]])

    for key in gender.keys():
        g.append([key,gender[key]])

    for key in vehicle.keys():
        v.append([key,vehicle[key]])

    for key in job.keys():
        j.append([key,job[key]])

    for key in qualification.keys():
        q.append([key,qualification[key]])
    results=mongoDriver.getPrecisionRecallTest()
    from operator import itemgetter
    a = sorted(a, key=itemgetter(0))

    fmeasure = mongoDriver.getFMeasure()

    return render_template('index.html',usersTest=usersTest,age=a, gender=g,vehicle=v,job=j,qualification=q,results=results,fmeasure=fmeasure)


@app.route('/testRecommendation.html')
def test1():
    return render_template('testRecommendation.html')

@app.route('/testRecommendation1.html',methods=['POST'])
def testDescription():
    u = request.form
    user = {'nome':u['nome'],'sesso':u['sesso'],'eta':u['eta'],'veicolo':u['veicolo'],'lavoro':u['lavoro'],'titolo':u['titolo']}
    return render_template('testRecommendation1.html',user=user)

@app.route('/testRecommendation2.html', methods=['POST'])
def test2():
    #print(request.form)
    user=request.form['user']
    #print(user)

    user=json.loads(user.replace("\'", "\""))
    #print(user)
    u = mongoDriver.saveTestUser(user)
    return render_template('testRecommendation2.html', user=u)
@app.route('/testRecommendation3.html', methods=['POST'])
def test3():
    #salvo risultati pagina precedente
    pearson=int(request.form['pearson'])
    cossim = int(request.form['cossim'])

    if request.form['bestRac']=="1":
        pearson=pearson+1
    if request.form['bestRac']=="2":
        cossim=cossim+1

    user = request.form['user']

    user=json.loads(user.replace("\'","\""))

    mongoDriver.updateTestUser(user['_id'],"pearsonRacOpinion",pearson)
    mongoDriver.updateTestUser(user['_id'],"cosSimRacOpinion",cossim)

    #estraggo ristoranti per pagina attuale

    listsRest=mongoDriver.getRecRestaurantList([item[0] for item in user['pearsonCat']])

    ordineGiusto=listsRest[1]
    listsRest=listsRest[0]

    mongoDriver.updateTestUser(user['_id'],"pearsonRest",ordineGiusto)

    return render_template('testRecommendation3.html',pearsonRest=listsRest, user=user)

@app.route('/testRecommendation4.html', methods=['POST'])
def test4():

    #salvo i risultati ottenuti nella pagina precedente
    user = request.form['user']
    user = json.loads(user.replace("\'", "\""))
    form = request.form
    value = form.to_dict(flat=False)
    del value['user']
    mongoDriver.updateTestUser(user['_id'],"pearsonRestByUser",value)

    # estraggo ristoranti per pagina attuale
    listsRest = mongoDriver.getRecRestaurantList([item[0] for item in user['cosSimCat']])
    ordineGiusto = listsRest[1]
    listsRest = listsRest[0]
    mongoDriver.updateTestUser(user['_id'], "cosSimRest", ordineGiusto)

    return render_template('testRecommendation4.html',cosSimRest=listsRest,user=user)


@app.route('/testRecommendation5.html', methods=['POST'])
def test5():
    #salvo i risultati ottenuti nella pagina precedente
    user = request.form['user']
    user = json.loads(user.replace("\'", "\""))
    form = request.form
    value = form.to_dict(flat=False)
    del value['user']
    mongoDriver.updateTestUser(user['_id'], "cosSimRestByUser", value)

    # estraggo ristoranti per pagina attuale
    listsRest =mongoDriver.getNearestRestaurantList()
    ordineGiusto = listsRest[1]
    listsRest = listsRest[0]

    mongoDriver.updateTestUser(user['_id'],"distanceRest",ordineGiusto)

    return render_template('testRecommendation5.html',simpleRest=listsRest,user=user)

@app.route('/testRecommendation6.html', methods=['POST'])
def test6():
    #salvo i risultati ottenuti nella pagina precedente
    user = request.form['user']
    user = json.loads(user.replace("\'", "\""))
    form = request.form
    value = form.to_dict(flat=False)
    del value['user']
    mongoDriver.updateTestUser(user['_id'], "distanceRestByUser", value)

    # estraggo ristoranti per pagina attuale
    listsRest =mongoDriver.getVoteRestaurantList()
    ordineGiusto = listsRest[1]
    listsRest = listsRest[0]

    mongoDriver.updateTestUser(user['_id'],"voteRest",ordineGiusto)

    return render_template('testRecommendation6.html',simpleRest=listsRest,user=user)


@app.route('/fineTest.html', methods=['POST'])
def testFine():
    #salvo i risultati ottenuti nella pagina precedente
    user = request.form['user']
    user = json.loads(user.replace("\'", "\""))
    form = request.form
    value = form.to_dict(flat=False)
    del value['user']
    mongoDriver.updateTestUser(user['_id'], "voteRestByUser", value)
    mongoDriver.updateTestUser(user['_id'], "completed", 1)
    return render_template('fineTest.html')

@app.route('/users.html', methods=['GET'])
def users():

    data=mongoDriver.getUsers()
    return render_template('users.html', data=data)

@app.route('/recommendations.html', methods=['GET'])
def recommendations():

    data=mongoDriver.getRecommendations()
    return render_template('recommendations.html', data=data)

@app.route('/compareRecommendations.html', methods=['GET'])
def compareRecommendations():
    data=mongoDriver.getRecommendationsResults()
    return render_template('compareRecommendations.html', data=data)
@app.route('/racCompare/id=<id>', methods=['GET','POST'])
def racCompare(id):
    rac = mongoDriver.getRecommendationResults(id)
    return render_template('racCompare.html', data=rac[0])

@app.route('/feedback.html', methods=['GET'])
def feedback():

    data=mongoDriver.getRecommendations()
    return render_template('feedback.html', data=data)
@app.route('/findUser/<chatid>', methods=['GET','POST'])
def user(chatid):
    data=mongoDriver.getUser(chatid)
    return render_template('userInfo.html', data=data)

@app.route('/findUserRecommendations/<chatid>', methods=['GET','POST'])
def userRecommendations(chatid):
    data=mongoDriver.getUserRecommendations(chatid)
    return render_template('recommendationsInfo.html', data=data,chatid=chatid)

@app.route('/findUserFeedBack/<chatid>', methods=['GET','POST'])
def userFeedBack(chatid):
    data=mongoDriver.getUserRecommendations(chatid)
    return render_template('feedbackInfo.html', data=data,chatid=chatid)

@app.route('/findRecommendations/id=<id>&chatid=<chatid>', methods=['GET','POST'])
def recommendationsInfo(id,chatid):
    rac = mongoDriver.getRecommendation(id,chatid)
    return render_template('recommendationInfo.html', data=rac[0])

@app.route('/webhook', methods=['POST'])
def webhook():

    req = request.get_json(silent=True, force=True)

    #print("Request:")
    #print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    #print(res)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    name=""
    chatid = getChatID(req)

    if req.get("result").get("action") =="webhook.benvenuto":
        return welcomeIntent(chatid)

    if req.get("result").get("action") == "interview.nome":
        return nameIntent(req,chatid)

    if req.get("result").get("action") == "interview.genere":
        return genderIntent(req,chatid)

    if req.get("result").get("action") == "interview.eta":
        return ageIntent(req,chatid)

    if req.get("result").get("action") == "interview.veicolo":
        return  vehicleIntetn(req,chatid)

    if req.get("result").get("action") == "feedback":
        return  feedbackIntent(req,chatid)

    if req.get("result").get("action") == "interview.lavoro":
        return  jobIntetn(req,chatid)


    if req.get("result").get("action") == "raccomandazione2":
        return raccomandazioneIntent(req,chatid)
    if req.get("result").get("action") == "filterResult.cucina":
        return  filterResultCucina(req,chatid)
    if req.get("result").get("action") == "filterResult.orario":
        return filterResultOrario(req, chatid)
        ##if req.get("result").get("action") == "selectRestaurant":
        ##  return  selectRestaurant(req,chatid)

def welcomeIntent(chatid):
    if chatid is not None:
        user=User(chatid)
        if user.isNewUser():
            speech = "Ciao! Purtroppo ancora non ci conosciamo.\mPrima di chiedermi qualcosa devo farti alcune domande.\nPosso?"
            return {
                "speech": speech,
                "displayText": speech,
                "contextOut": [{"name": "intent-di-benvenuto-followup", "lifespan": 5, "parameters": {}}]
            }
        else:
            speech = "Ciao " + user.getName() + "!"
            return {
                "speech": speech,
                "displayText": speech,
            }
def nameIntent(req,chatid):
    if chatid is not None:
        result = req.get("result")
        text = result.get("resolvedQuery")

        text = re.sub(r'[^\w\s]', '', text)
        name = mongoDriver.isName(text)
        user= User(chatid)
        user.setName(name)
        if name is None:
            speech = "Non capisco il tuo nome... potresti ripeterlo?"
            return {
                "speech": speech,
                "displayText": speech,
                "contextOut": [{"name": "domanda-2", "lifespan": 0, "parameters": {}},
                               {"name": "domanda-1", "lifespan": 5, "parameters": {}}]
            }

        speech = "Ciao " + name+"!\n\mSei un uomo o una donna?"
        return {
            "speech": speech,
            "displayText": speech
        }

def genderIntent(req,chatid):
    gender = req.get('result').get('parameters').get('gender')
    user = User(chatid)
    if gender is not None:
        user.setGender(gender)
        speech = "Perfetto!\n\mQuanti anni hai?"
        return {
            "speech": speech,
            "displayText": speech,
            "contextOut": [{"name": "DefaultFallbackIntent-followup", "lifespan": 0, "parameters": {}},
                           {"name": "domanda-2", "lifespan": 0, "parameters": {}},
                           {"name": "domanda-3", "lifespan": 5, "parameters": {}}]

        }
    else:
        speech = "Non ho capito se sei uomo o donna. potresti ripetermelo?"
        return {
            "speech": speech,
            "displayText": speech,
            "contextOut": [{"name": "domanda-3", "lifespan": 0, "parameters": {}},
                           {"name": "domanda-2", "lifespan": 5, "parameters": {}}]
        }

def ageIntent(req,chatid):
    age = str(req.get('result').get('parameters').get('number'))
    user = User(chatid)
    speech=""
    if age is not None:
        user.setAge(age)
        if int(age)<30:
            speech = "Wow! hai "+age+" anni! Beata gioventù\n\m"
        elif int(age)> 60:
            speech = "Ehi vecchietto!\n\m"
        speech=speech+"con che mezzo ti muovi di solito?"
        return {
            "speech": speech,
            "displayText": speech

        }
    else:
        speech = "Non ho capito quanti anni hai. potresti ripetermelo?"
        return {
            "speech": speech,
            "displayText": speech,
            "contextOut": [{"name": "domanda-4", "lifespan": 0, "parameters": {}},
                           {"name": "domanda-3", "lifespan": 5, "parameters": {}}]
        }
def vehicleIntetn(req,chatid):
    vehicle = req.get('result').get('parameters').get('veicolo')
    user = User(chatid)
    if vehicle is not None:
        user.setVehicle(vehicle)
        speech = "Un'ultima domanda: che lavoro fai?"
        return {
            "speech": speech,
            "displayText": speech}
    else:
        speech = "Non ho capito che veicolo utilizzi di solito. potresti ripetermelo?"
        return {
            "speech": speech,
            "displayText": speech,
            "contextOut": [{"name": "domanda-4", "lifespan": 0, "parameters": {}},
                           {"name": "domanda-3", "lifespan": 5, "parameters": {}}]
        }

def jobIntetn(req,chatid):
    job = req.get('result').get('parameters').get('lavoro')
    user = User(chatid)
    if job is not None:
        user.setJob(job)
        speech = "Ottimo,abbiamo terminato!\n\mAdesso che conosco tutte queste cose di te posso aiutarti e consigliarti tutti i ristoranti che vuoi!"
        return {
            "speech": speech,
            "displayText": speech}
    else:
        speech = "Non ho capito che lavoro fai, effettua una scelta tra i pulsanti qui sotto..."
        return {
            "speech": speech,
            "displayText": speech,
            "contextOut": [{"name": "domanda-5", "lifespan": 0, "parameters": {}},
                           {"name": "domanda-4", "lifespan": 5, "parameters": {}}]
        }

def feedbackIntent(req,chatid):
    contexts = req.get('result').get('contexts')
    date=""
    vote=""
    feedback=""
    for c in contexts:
        if c.get('name')=='feedback':
            feedback=c.get('parameters').get('any2')
            date=c.get('parameters').get('any')
            vote=c.get('parameters').get('number')


    mongoDriver.saveFeedBack(chatid,feedback,date,vote)
    return {
        "contextOut": [{"name": "feedback", "lifespan": 0, "parameters": {}}]
    }
    #user = User(chatid)
def raccomandazioneIntent(req,chatid):
    user=User(chatid)
    if user.isNewUser():
        speech = "Ciao! Purtroppo ancora non ci conosciamo.\mPrima di chiedermi una raccomandazione devo farti alcune domande.\nPosso?"
        return {
            "speech": speech,
            "displayText": speech,
            "contextOut": [{"name": "raccomandazione2", "lifespan": 0, "parameters": {}},
                           {"name": "Intent-Di-Benvenuto-followup", "lifespan": 5, "parameters": {}}]
        }
    if 'raccomandazione2' in req.get("result").get('fulfillment').get('speech'):

        mongoDriver.removeRecommendation(chatid)

        raccomandazione=Recommendation(chatid)

        return {
            "speech": "\\raccomandazione2",
            "displayText": "\\raccomandazione2"
        }


    raccomandazione=Recommendation(chatid)

    p = req.get("result").get("contexts")[0].get("parameters")

    cucina = p.get("cucina.original")
    if len(p.get("cucina")) <=1:
        cucina = [cucina]

    time_pasto = p.get("time_pasto.original")
    speech = req.get("result").get("resolvedQuery")
    # print(len(cucina))
    # print(time)
    # print (time_pasto)
    if len(p.get("cucina")) is not 0:
        raccomandazione.setCucina(p.get("cucina"))
        for cOriginal in cucina:
            speech = str(speech.replace(cOriginal, ""))
        return {
            "speech": speech,
            "displayText": speech
        }
    elif len(time_pasto) is not 0:
        raccomandazione.setTime_Pasto(p.get("time_pasto"))
        speech = speech.replace(time_pasto, "")
        return {
            "speech": speech,
            "displayText": speech
        }
    else:
        typeP=raccomandazione.getCucina()
        timeP=raccomandazione.getTime_Pasto()
        if len(typeP) is 0:

            #\end
            return {
                "speech": "\end tipologia",
                "displayText": "\end tipologia",
                "contextOut": [{"name": "raccomandazione2", "lifespan": 0, "parameters": {}},
                               {"name": "specifiche", "lifespan": 0, "parameters": {}},
                               {"name": "controllaTipologia", "lifespan": 2, "parameters": {}}
                               ]
            }
        elif timeP =="":
            return {
                "speech": "\end time",
                "displayText": "\end time",
                "contextOut": [{"name": "raccomandazione2", "lifespan": 0, "parameters": {}},
                               {"name": "specifiche", "lifespan": 0, "parameters": {}},
                               {"name": "controllaOrario", "lifespan": 2, "parameters": {}}
                               ]
            }
        else:
            return {
                "speech": "\end",
                "displayText": "\end",
                "contextOut": [{"name": "raccomandazione2", "lifespan": 0, "parameters": {}},
                               {"name": "specifiche", "lifespan": 0, "parameters": {}},
                               {"name": "location", "lifespan": 1, "parameters": {}}
                               ]
            }


def filterResultCucina(req,chatid):
    p = req.get("result").get("contexts")[0].get("parameters")
    command = p.get("any.original")
    lun = len(p.get("any"))
    typeR =p.get("cucina")
    if lun==1:
        if command == "\\next":
            typeR=[]

    raccomandazione = Recommendation(chatid)
    raccomandazione.setCucina(typeR)
    tp=raccomandazione.getTime_Pasto()
    if tp == "":
        return {
            "speech": "\\end time",
            "displayText": "\\end time",

        }
    else:
        return {
            "speech": "Ok, ho bisogno della tua posizione per raccomandarti dei ristoranti",
            "displayText": "Ok, ho bisogno della tua posizione per raccomandarti dei ristoranti",
            "contextOut": [{"name": "raccomandazione2", "lifespan": 0, "parameters": {}},
                           {"name": "specifiche", "lifespan": 0, "parameters": {}},
                           {"name": "controllaorario", "lifespan": 0, "parameters": {}},
                           {"name": "controllaOrario", "lifespan": 0, "parameters": {}},
                           {"name": "location", "lifespan": 1, "parameters": {}}
                           ]
        }

def filterResultOrario(req,chatid):
    p = req.get("result").get("contexts")[0].get("parameters")
    command = p.get("any.original")
    lun = len(p.get("any"))
    typeR = p.get("time_pasto")
    if lun==1:
        if command == "\\next":
            typeR=""

    raccomandazione = Recommendation(chatid)
    raccomandazione.setTime_Pasto(typeR)
    tp=raccomandazione.getTime_Pasto()
    return {
        "speech": "Ok, ho bisogno della tua posizione per raccomandarti dei ristoranti",
        "displayText": "Ok, ho bisogno della tua posizione per raccomandarti dei ristoranti",

    }

def selectRestaurant(req,chatid):
    p = req.get("result").get("parameters")
    raccomandazione = Recommendation(chatid)
    number = int(p.get("number"))-1
    fbRestaurants = raccomandazione.getFacebookRestaurants()
    if number<0 or number > len(fbRestaurants)-1:
        speech="Scelta non valida"
        return {
            "speech": speech,
            "displayText": speech,
            "contextOut": [{"name": "estrazione", "lifespan": 5, "parameters": {}},
                           {"name": "risultati-followup", "lifespan": 5, "parameters": {}}
                           ]
        }
    restaurant = fbRestaurants[number]
    mongoDriver.saveRecommendation(chatid,restaurant)
    speech="Hai scelto "+ restaurant['name']+"!"
    return {
        "speech": speech,
        "displayText": speech,
        "contextOut": [{"name": "estrazione", "lifespan": 0, "parameters": {}},
                       {"name": "risultati-followup", "lifespan": 0, "parameters": {}}
                       ]
    }

def getChatID(req):
    chatid = str(req.get("sessionId"))
    return chatid


def runLocalHost():
    import requests

    URL = "http://127.0.0.1:4040/api/tunnels"

    response = requests.get(URL)
    print("Running on: "+json.loads(response.content)['tunnels'][0]['public_url']+"/webhook")
    app.run(port=5000)



