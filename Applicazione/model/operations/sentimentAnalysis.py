from nltk.tokenize.moses import MosesTokenizer, MosesDetokenizer
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import editdistance
from pymongo import MongoClient


client = MongoClient()
db = client.usersbot.sentiment

string ="ciao.AS Ss ss iosono. sono.Non in  sono nicola sono andato a roma un porca mignotta non sapevo cosaa fare"

def tokenizer(string):

    #rimozione punteggiatura
    tokenizer = RegexpTokenizer(r'\w+')
    a=tokenizer.tokenize(string)

    data = ' '.join(a)

    #rimozione stopword
    stopWords = set(stopwords.words('italian'))
    words = word_tokenize(data)
    wordsFiltered = []

    for w in words:
        if w not in stopWords:
            wordsFiltered.append(w)

    return wordsFiltered

def stemming(stringTokenized):
    stemmer = nltk.stem.snowball.ItalianStemmer(ignore_stopwords=False)
    words = []
    for word in stringTokenized:
        words.append(stemmer.stem(word))
    return words

def importDat():
    k = [[1, 2], [4], [5, 6, 2], [1, 2], [3], [4]]
    import itertools
    k.sort()
    list(k for k, _ in itertools.groupby(k))
    f = open("senti_lexicon.dat", "r", encoding="utf8")
    e =[]
    for l in f:

        l=l.replace("\n","")
        l= l.split("\t")
        if not l[0].__contains__("_"):
            e.append([l[0],l[5]])
    #elem = {"lemma":l[0],"polarity":l[5]}
    import itertools
    e.sort()
    e = list(e for e, _ in itertools.groupby(e))
    for el in e:
            db.insert({"lemma":el[0],"polarity":el[1]})

def getPolarity(string):
    if db.count({'lemma':string})==0:
        elements= db.find()
        elem=elements[0]
        val = editdistance.eval(string,elem['lemma'])
        for e in elements:
            dist = editdistance.eval(string,e['lemma'])
            if dist<val:
                val=dist
                elem=e
        return elem
    else:
        return db.find({'lemma':string})[0]

def findSentiment(string):
    words = tokenizer(string)
    count = 0.0
    totPolarity = 0.0
    for w in words:
        print(w)
        count=count+1.0
        totPolarity = totPolarity+float(getPolarity(w)['polarity'])
    ris= totPolarity/count
    print(ris)
    if ris <=-0.15:
        return -1
    elif ris>=0.33:
        return 1
    else:
        return 0



