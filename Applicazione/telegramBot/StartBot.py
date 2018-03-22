from telegramBot.message import message as messaggio
from model.restaurant import Restaurant
from model.operations.recommendationExtractor import saveRecommendationResults
import time
import json
import telegram
from telegram.ext import Updater, CommandHandler,MessageHandler, Filters, CallbackQueryHandler
import logging
from model.recommendation import Recommendation
from ResturantData.ResturantAPI import ResturantFacebook
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram.message
from bson.json_util import dumps
from mongodb.mongoDriver import saveRecommendation,savePhoto,removePhoto,removeRecommendation, getRecommendation
from Config import config



updater = Updater(token=config.TOKEN)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

def controllaMessaggio(string,message):
    for m in message:
        if string in m:
            return True
    else:
        return False


def recommendation(bot, update, message):
    while '\\end' not in message[0]:
        if message[0] == "":
            message = "a"
        message = [messaggio.sendTelegramMessage(update.message.chat.id, message)]
    if "\\end tipologia" in message:
        r = Recommendation(update.message.chat.id)
        b =[]
        for t in r.getTopFiveRecommendation():
            text = t.replace("_"," ")
            b.append(text)
        custom_keyboard = [[b[0],b[1]],[b[2],b[3]],[b[4]],["Non mi interessa"]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        sendMessageToUser(bot, update, ["Vorresti mangiare qualcosa in particolare?",
                                        "Puoi scegliere tra i miei consigli oppure specificarmi una tipologia di cucina da te preferita!"],reply_markup)

    elif "\\end time" in message:
        custom_keyboard = [["Pranzo"], ["Cena"], ["Non lo so"]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        sendMessageToUser(bot, update, ["Vuoi andare al ristorante a pranzo o a cena?"], reply_markup)

    else:
        reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
        r = Recommendation(update.message.chat.id)
        sendMessageToUser(bot, update, ["Ok, ho bisogno della tua posizione per raccomandarti dei ristoranti"], reply_markup)



def sendMessageToUser(bot,update,message,reply_markup):
    #print(reply_markup)
    #if reply_markup is None:
    #    reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
    remove= 'remove_keyboard' in str(reply_markup)
    if len(message[0]) is 0:
        reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
        bot.send_message(update.message.chat.id, text="errore",reply_markup=reply_markup)
    else:
        for i in range(0, len(message)):
            if len(message)==1:
                bot.send_message(update.message.chat.id, text=message[i], reply_markup=reply_markup)
            else:
                if i==0:
                    if remove:
                        bot.send_message(update.message.chat.id, text=message[i], reply_markup=reply_markup)
                    else:
                        bot.send_message(update.message.chat.id, text=message[i])
                else:
                    if not remove:
                        bot.send_message(update.message.chat.id, text=message[i], reply_markup=reply_markup)
                    else:
                        bot.send_message(update.message.chat.id, text=message[i])

            time.sleep(0.5)


def message(bot, update):

    #estraggo il messaggio inviato dall'utente
    messaggioUtente= update.message.text
    if messaggioUtente =="Non mi interessa":
        messaggioUtente = "\\next ristorante"
    if messaggioUtente =="Non lo so":
        messaggioUtente = "\\next cena"
    if messaggioUtente =="Annulla raccomandazione":
        messaggioUtente = "\\reset"
    print("user: "+messaggioUtente)
    #invio il messaggio a dialogFlow e estraggo la risposta
    rispostaBot=messaggio.sendTelegramMessage(update.message.chat.id, messaggioUtente)
    reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
    print("bot: "+rispostaBot)
    rispostaBot = rispostaBot.split("\m")


    casoBase=True


#controlli per inserire o rimuovere bottoni
    if controllaMessaggio("annullare la raccomandazione",rispostaBot):
        #print(1)
        #print(controllaMessaggio("annullare la raccomandazione", rispostaBot))
        custom_keyboard = [["Annulla raccomandazione"]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        sendMessageToUser(bot, update, rispostaBot, reply_markup)
        casoBase = False

    if controllaMessaggio("Raccomandazione annullata",rispostaBot):
        removeRecommendation(update.message.chat.id)
        reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
        sendMessageToUser(bot, update, rispostaBot, reply_markup)
        casoBase = False

    if controllaMessaggio("raccomandazione2",rispostaBot):
        recommendation(bot, update, messaggioUtente)
        casoBase=False
    if controllaMessaggio('Grazie del giudizio! Buona Giornata!', rispostaBot ):
        t = messaggio.sendTelegramMessage(update.message.chat.id, "Fine raccomandazione")
        print("feedback salvato:" + t)
        reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)

        sendMessageToUser(bot,update,rispostaBot,reply_markup)
        casoBase=False
    #if controllaMessaggio('',rispostaBot):
    if controllaMessaggio('uomo o una donna', rispostaBot):
        uomo_keyboard = telegram.KeyboardButton(text="uomo")
        donna_keyboard = telegram.KeyboardButton(text="donna")
        custom_keyboard = [[uomo_keyboard], [donna_keyboard]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        sendMessageToUser(bot,update,rispostaBot,reply_markup)
        casoBase=False

    if controllaMessaggio('Perfetto!',rispostaBot):
        reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
        sendMessageToUser(bot,update,rispostaBot,reply_markup)
        casoBase=False

    if controllaMessaggio('con che mezzo ti muovi di solito', rispostaBot):
        automobile_keyboard = telegram.KeyboardButton(text="automobile")
        ciclomotore_keyboard = telegram.KeyboardButton(text="ciclomotore 50")
        moto_keyboard = telegram.KeyboardButton(text="moto")
        bicicletta_keyboard = telegram.KeyboardButton(text="bicicletta")
        mezzi_keyboard = telegram.KeyboardButton(text="mezzi pubblici")
        custom_keyboard = [[automobile_keyboard, bicicletta_keyboard], [moto_keyboard, ciclomotore_keyboard],
                           [mezzi_keyboard]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        sendMessageToUser(bot, update, rispostaBot, reply_markup)
        casoBase=False

    if controllaMessaggio('Ottimo,abbiamo terminato!', rispostaBot):
        reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
        sendMessageToUser(bot, update, rispostaBot, reply_markup)
        casoBase=False



    if controllaMessaggio('che lavoro fai' ,rispostaBot):
        impiegato_keyboard = telegram.KeyboardButton(text="impiegato")
        disoccupato_keyboard = telegram.KeyboardButton(text="lavoratore autonomo")
        lavoratore_aut_keyboard = telegram.KeyboardButton(text="disoccupato")
        casalinga_keyboard = telegram.KeyboardButton(text="casalinga")
        studente_keyboard = telegram.KeyboardButton(text="studente")
        militare_keyboard = telegram.KeyboardButton(text="corpo militare")
        pensionato_keyboard = telegram.KeyboardButton(text="pensionato")
        altro_keyboard = telegram.KeyboardButton(text="altro")
        custom_keyboard = [[impiegato_keyboard, disoccupato_keyboard], [casalinga_keyboard, pensionato_keyboard],
                           [militare_keyboard, studente_keyboard], [lavoratore_aut_keyboard, altro_keyboard]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        sendMessageToUser(bot, update, rispostaBot, reply_markup)
        casoBase=False

    if controllaMessaggio('1 a 10',rispostaBot):
        keyboard1 = telegram.KeyboardButton(text="1")
        keyboard2 = telegram.KeyboardButton(text="2")
        keyboard3 = telegram.KeyboardButton(text="3")
        keyboard4 = telegram.KeyboardButton(text="4")
        keyboard5 = telegram.KeyboardButton(text="5")
        keyboard6 = telegram.KeyboardButton(text="6")
        keyboard7 = telegram.KeyboardButton(text="7")
        keyboard8 = telegram.KeyboardButton(text="8")
        keyboard9 = telegram.KeyboardButton(text="9")
        keyboard10 = telegram.KeyboardButton(text="10")

        custom_keyboard = [[keyboard1,keyboard2,keyboard3],[keyboard4,keyboard5,keyboard6],[keyboard7,keyboard8,keyboard9],[keyboard10]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        sendMessageToUser(bot, update, rispostaBot, reply_markup)
        casoBase = False

    if controllaMessaggio("\\end time",rispostaBot):
        custom_keyboard = [["Pranzo"], ["Cena"], ["Non lo so"]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        sendMessageToUser(bot, update, ["Vuoi andare al ristorante a pranzo o a cena?"], reply_markup)
        casoBase = False

    if controllaMessaggio("ho bisogno della tua posizione",rispostaBot):
        reply_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
        sendMessageToUser(bot, update, rispostaBot, reply_markup)
        casoBase = False


# messaggio normale
    if casoBase:
        sendMessageToUser(bot,update,rispostaBot,None)

def start(bot, update):
    testo=messaggio.sendTelegramMessage(update.message.chat.id, "ciao")
    testo=testo.split("\m")
    for i in range(0, len(testo)):
        bot.send_message(update.message.chat.id, text=testo[i])
        time.sleep(1)

def updateLocation(bot,update):
    print("update loc: ")
    print(update.edited_message.location)

def firstLocation(bot,update):

    text = messaggio.sendTelegramMessage(update.message.chat.id,"\location")
    text=text.split("\m")
    #estrazione
    #aggiorno recommendation
    #messaggio.sendTelegramMessage(update.message.chat.id,"\\risultati")

    if controllaMessaggio("annullare la raccomandazione",text):
        #print(controllaMessaggio("annullare la raccomandazione", text))
        custom_keyboard = [["Annulla raccomandazione"]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        sendMessageToUser(bot, update, text, reply_markup)
    else:
        sendMessageToUser(bot, update, text, None)

    if not controllaMessaggio("Se vuoi che ti consiglio dei ristoranti, devi chiedermelo esplicitamente!",text) and not controllaMessaggio("annullare la raccomandazione",text):

        location = {'longitude': str(update.message.location.longitude),
                    'latitude': str(update.message.location.latitude)}
        saveRecommendationResults(update.message.chat.id,50,10)
        recommendation = Recommendation(str(update.message.chat.id))
        recommendation.setLocation(location)
        rFB = ResturantFacebook.RestaurantFacebook()
        rFB.extractForRecommendation(recommendation)
        sendRecommendation(bot, update, recommendation)



def sendRecommendation(bot, update, recommendation):
    #estraggo i ristoranti
    res = recommendation.getFacebookRestaurants()
    #calcolo quanti ne ho estratti
    totExtraction = len(res)
    if totExtraction > 0:
        bot.send_message(update.message.chat.id,text="sono stati estratti " + str(totExtraction) + " ristoranti da Facebook!")
        time.sleep(1)
        keyboard = []
        r = Restaurant(res[0])

        centerInlineKeyboard = InlineKeyboardButton("• 1 •", callback_data="5,0")
        nextInlineKeyboard = InlineKeyboardButton("2 >", callback_data="4,1")
        nullInlineKeyboard = InlineKeyboardButton("   ", callback_data="5,0")


        keyboard.append(nullInlineKeyboard)
        keyboard.append(centerInlineKeyboard)
        if totExtraction>1:
            keyboard.append(nextInlineKeyboard)
        else:
            keyboard.append(nullInlineKeyboard)

        selectInlineKeyboard = InlineKeyboardButton("Scegli questo ristorante", callback_data="1,0")
        annullaInlineKeyboard = InlineKeyboardButton("Annulla raccomandazione", callback_data="2,0")
        fotoInlineKeyboard = InlineKeyboardButton("Mostra Foto", callback_data="3,0")
        reply_markup = InlineKeyboardMarkup([keyboard,[selectInlineKeyboard],[fotoInlineKeyboard],[annullaInlineKeyboard]])
        bot.send_message(chat_id=update.message.chat.id, text=str(r),
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         disable_web_page_preview=True,reply_markup=reply_markup)
    else:
        bot.send_message(update.message.chat.id,text="Mi dispiace non ho trovato nessun ristorante nella tua zona...")



def nextRecommendation(bot,chatid,messageid,index):
    recommendation = Recommendation(str(chatid))
    res = recommendation.getFacebookRestaurants()
    r=dumps(res[index],indent=4)
    restaurant=""
    totExtraction = len(res)
    keyboard = []
    backInlineKeyboard= InlineKeyboardButton("< "+str(index), callback_data="4,"+str(index-1))
    centerInlineKeyboard = InlineKeyboardButton("• "+str(index + 1) + " •", callback_data="5," + str(index))
    nextInlineKeyboard = InlineKeyboardButton(str(index + 2)+" >", callback_data="4,"+str(index+1))
    nullInlineKeyboard = InlineKeyboardButton("   ", callback_data="5,0")
    if index-1 >=0:
        keyboard.append(backInlineKeyboard)
    else:
        keyboard.append(nullInlineKeyboard)

    keyboard.append(centerInlineKeyboard)
    if index+1<totExtraction:
        keyboard.append(nextInlineKeyboard)
    else:
        keyboard.append(nullInlineKeyboard)

    selectInlineKeyboard = InlineKeyboardButton("Scegli questo ristorante", callback_data="1,"+str(index))
    annullaInlineKeyboard = InlineKeyboardButton("Annulla raccomandazione", callback_data="2,"+str(index))
    fotoInlineKeyboard = InlineKeyboardButton("Mostra Foto", callback_data="3,"+str(index))
    reply_markup = InlineKeyboardMarkup([keyboard, [selectInlineKeyboard], [fotoInlineKeyboard], [annullaInlineKeyboard]])

    if index in range (0,totExtraction):
        restaurant = Restaurant(json.loads(r))
        #print(str(restaurant.about))
    bot.edit_message_text(chat_id=chatid,message_id=messageid,text=str(restaurant), parse_mode=telegram.ParseMode.MARKDOWN,
                     disable_web_page_preview=True,reply_markup=reply_markup)

def getPhoto(bot,chatid,messageid,index,indexPhoto):
    recommendation = Recommendation(str(chatid))
    res = recommendation.getFacebookRestaurants()
    r = dumps(res[index], indent=4)
    rId=json.loads(r)['id']
    photoLinks = savePhoto(chatid,rId)
    totExtraction = len(photoLinks)
    if totExtraction > 0:
        photoLink = photoLinks[indexPhoto]


        #creo bottoni id,index ristorante, index foto
        keyboard = []
        backInlineKeyboard = InlineKeyboardButton("< " + str(indexPhoto), callback_data="6," + str(index)+"," +str(indexPhoto-1))
        centerInlineKeyboard = InlineKeyboardButton("• " + str(indexPhoto + 1) + " •", callback_data="5," + str(index))
        nextInlineKeyboard = InlineKeyboardButton(str(indexPhoto + 2) + " >", callback_data="6," + str(index)+"," +str(indexPhoto+1))
        nullInlineKeyboard = InlineKeyboardButton("   ", callback_data="5,0")
        if indexPhoto - 1 >= 0:
            keyboard.append(backInlineKeyboard)
        else:
            keyboard.append(nullInlineKeyboard)

        keyboard.append(centerInlineKeyboard)
        if indexPhoto + 1 < totExtraction:
            keyboard.append(nextInlineKeyboard)
        else:
            keyboard.append(nullInlineKeyboard)

        restaurantInlineKeyboard = InlineKeyboardButton("<-- Torna al ristorante", callback_data="7," + str(index))
        reply_markup = InlineKeyboardMarkup(
            [keyboard, [restaurantInlineKeyboard]])




        bot.sendPhoto(chat_id=chatid,
                      photo=photoLink,reply_markup=reply_markup)
        bot.delete_message(chat_id=chatid, message_id=messageid)
        return True
    else:
        removePhoto(chatid)
        return False



def returnRestaurant(bot,chatid,messageid,index):
    recommendation = Recommendation(str(chatid))
    res = recommendation.getFacebookRestaurants()
    r=dumps(res[index],indent=4)
    restaurant=""
    totExtraction = len(res)
    keyboard = []
    backInlineKeyboard= InlineKeyboardButton("< "+str(index), callback_data="4,"+str(index-1))
    centerInlineKeyboard = InlineKeyboardButton("• "+str(index + 1) + " •", callback_data="5," + str(index))
    nextInlineKeyboard = InlineKeyboardButton(str(index + 2)+" >", callback_data="4,"+str(index+1))
    nullInlineKeyboard = InlineKeyboardButton("   ", callback_data="5,0")
    if index-1 >=0:
        keyboard.append(backInlineKeyboard)
    else:
        keyboard.append(nullInlineKeyboard)

    keyboard.append(centerInlineKeyboard)
    if index+1<totExtraction:
        keyboard.append(nextInlineKeyboard)
    else:
        keyboard.append(nullInlineKeyboard)

    selectInlineKeyboard = InlineKeyboardButton("Scegli questo ristorante", callback_data="1,"+str(index))
    annullaInlineKeyboard = InlineKeyboardButton("Annulla raccomandazione", callback_data="2,"+str(index))
    fotoInlineKeyboard = InlineKeyboardButton("Mostra Foto", callback_data="3,"+str(index))
    reply_markup = InlineKeyboardMarkup([keyboard, [selectInlineKeyboard], [fotoInlineKeyboard], [annullaInlineKeyboard]])

    if index in range (0,totExtraction):
        restaurant = Restaurant(json.loads(r))
    bot.delete_message(chat_id=chatid, message_id=messageid)
    bot.sendMessage(chat_id=chatid,text=str(restaurant), parse_mode=telegram.ParseMode.MARKDOWN,
                     disable_web_page_preview=True,reply_markup=reply_markup)

def button(bot,update):
    query = update.callback_query
    data=format(query.data).split(",")
    scelta = int(data[0])
    index = int(data[1])
    indexPhoto = 0

    if len(data)>2:
        indexPhoto=int(data[2])

    if scelta is 1:
        raccomandazione = Recommendation(query.message.chat_id)
        fbRestaurants = raccomandazione.getFacebookRestaurants()
        restaurant = fbRestaurants[index]
        saveRecommendation(query.message.chat_id, restaurant)
        speech = "Hai scelto " + restaurant['name'] + "!"
        bot.edit_message_text(text=speech,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        messaggio.sendTelegramMessage(query.message.chat_id,"\\reset")
    if scelta is 2:
        text=messaggio.sendTelegramMessage(query.message.chat_id, "\\reset")
        bot.edit_message_text(text=text,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)

    if scelta is 3:
        esito = getPhoto(bot, query.message.chat_id, query.message.message_id, index, indexPhoto)
        if not esito:
            bot.answer_callback_query(callback_query_id=query.id, text="Nessuna foto presente")
        else:
            bot.answer_callback_query(query.id)

    if scelta is 4:
        if index >=0:
            nextRecommendation(bot, query.message.chat_id,query.message.message_id,index)
            bot.answer_callback_query(query.id)

    if scelta is 5:
        bot.answer_callback_query(query.id)


    if scelta is 6:
        esito=getPhoto(bot,query.message.chat_id,query.message.message_id,index,indexPhoto)
        if not esito:
            bot.answer_callback_query(callback_query_id=query.id,text="Nessuna foto presente")
        else:
            bot.answer_callback_query(query.id)

    if scelta is 7:
        removePhoto(query.message.chat_id)
        returnRestaurant(bot, query.message.chat_id, query.message.message_id, index)
        bot.answer_callback_query(query.id)


logger = logging.getLogger(__name__)
def _error(bot, update, e: BaseException):
    #messaggio.sendTelegramMessage(update.message.chat.id,"reset")
    logger.error(e)

c1 = CommandHandler("start",start)
h0=MessageHandler(Filters.location, firstLocation, edited_updates=False)
h1=MessageHandler(Filters.location, updateLocation, message_updates=False, edited_updates=True)
h2 = MessageHandler(Filters.text,message)
cb= CallbackQueryHandler(button)
#dispatcher.add_handler(h1)
dispatcher.add_handler(h0)
dispatcher.add_handler(h2)
dispatcher.add_handler(c1)
dispatcher.add_handler(cb)
dispatcher.add_error_handler(_error)


updater.start_polling(poll_interval = 1.0,timeout=20)
