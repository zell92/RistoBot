# Ristobot 

Ristobot e' un chatbot di raccomandazione di ristoranti, realizzato da Nicola Sardella, per la tesi magistrale in ingegneria informatica. Realizzato durante l'anno accademico 2016/2017.
La tesi in formato LaTex o PDF e le relative slide, sono scaricabili al seguente Link:
https://mega.nz/#F!tlQliCpA!rSVq2t7PpyjxnVfH6CGzOQ

## Cosa e' contenuto in questa repository?

Codice Python dell'applicazione. 
Per eseguire l'applicazione inserire all'interno della cartella "\Ristobot-master" la cartella "Installazione" scaricabile all'indirizzo: 
https://mega.nz/#F!x0AQFJjR!fNUCvskCRxHIn15u4mS8qw
e seguire le indicazioni riportate più avanti
## Requisiti
- **Python** versione 3.6 
- **Pip** versione 9.0.1 o superiore
- MongoDB
- Account **Google**

## Installazione
#####Download cartella installazione
- Scaricare la cartella "Install" al seguente link: https://mega.nz/#F!x0AQFJjR!fNUCvskCRxHIn15u4mS8qw
- Posizionare la cartella scaricata all'interno della cartella "\Ristobot-master"
##### 1 - Setting MongoDB
- Aprire il file di testo "config" presente nella cartella "*.\Install\StartApplication*"
- Sostituire il path presente nel file con quello relativo alla cartella di installazione di mongoDB
##### 2 - Creazione Database
- Eseguire il file batch **1_mongod.bat** presente all'interno della cartella "*.\Install\StartApplication*"
- Eseguire il file batch **restoreDB.bat** presente all'interno della cartella "*.\Install\DataBase*" 
- Chiudere eventuali finestre dos rimaste aperte
##### 3 - Packages Python
- - Eseguire il file batch **install_packages.bat** presente all'interno della cartella "*.\Install\Packages*" 
##### 4 - Creazione Agente su DialogFlow
- Collegarsi al sito https://console.dialogflow.com/api-client/
- Accedere utilizzando le credenziali Google
- Creare un nuovo agente
- Andare sulle **impostazioni** dell'agente
- Proseguire su **Export and Import**
- Cliccare su **Import from ZIP** e selezionare il file contenuto nella cartella "*.\Install\DialogFlow*" 
## Avvio Applicazione
- Eseguire tutti i file batch presenti nella cartella "*.\Install\StartApplication*" 
- Accedere alla cartella Chiamata *RistoBot* ed eseguire tramite Python i seguenti file:
    - "\_\_init\_\_.py"
        - Copiare la URL che viene stampata in console.
        - Accedere alla console relativa all'agente presente su DialogFlow.
        - Accedere all'area **Fulfillment**.
        - Incollarla nel campo URL*, il testo copiato in precedenza
        - Salvare       
    - "\telegramBot\StartBot.py"
    - "\notificationService\pushNotification.py"
- Collegarsi, su Telegram, con il chatbot, chiamato: **@ristobot_bot**
