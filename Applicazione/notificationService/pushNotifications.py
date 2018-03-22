from datetime import datetime,timedelta
import threading
from telegramBot.message import message as messaggio
import telegram
from pymongo import MongoClient









def notification():
    x = datetime.today()
    # y=x.replace(day=x.day+1, hour=1, minute=0, second=0, microsecond=0)
    y1 = (x + timedelta(days=1)).replace(hour=10, minute=00, second=0)
    y2 = (x + timedelta(days=1)).replace(hour=17, minute=12, second=0)
    delta_t1 = y1 - x
    delta_t2 = y2 - x

    if delta_t1.seconds<delta_t2.seconds:
        minimo=delta_t1.seconds
    else:
        minimo=delta_t2.seconds

    getFeedBack()
    secs =  minimo + 1

    threading.Timer(secs, notification).start()
def getFeedBack():
    client = MongoClient()
    db = client.usersbot.recommendations
    recommendations=[]
    chatids=[]
    recs = db.find()
    client.close()

    for r in recs:
        #print(r)
        if len(r['feedback'])==0:
            if r['chatid'] not in chatids:
                recommendations.append(str(r['chatid']+","+str(r['date'])+",("+str(r['restaurant']['name']+")")))
                chatids.append(r['chatid'])

    print(recommendations)

    for cid in recommendations:
        c = cid.split(",")
        print("GETFeedBacK "+c[1]+" GETFeedBacK "+c[2])
        testo = messaggio.sendTelegramMessage(c[0], "GETFeedBacK "+c[1]+" GETFeedBacK "+c[2])
        t=telegram.Bot(token='464290673:AAGKuIqJjSOBKkdKJPoT7RZmRSh9QBqEylw')

        t.send_message(chat_id=cid, text=testo)
        print(testo)


notification()