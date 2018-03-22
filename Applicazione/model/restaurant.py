import json
from bson import ObjectId
from bson.json_util import dumps


class Restaurant():
    name=""
    about=""
    category_list=""
    hours=[]
    fb_site=""
    site=""
    location =""
    rating=""
    phone=""
    price=""
    distance=""
    def __init__(self,jsonResturant):
        if 'name' in jsonResturant:
            self.name = jsonResturant['name']
        if 'about' in jsonResturant:
            self.about = jsonResturant['about']
        if 'category_list' in jsonResturant:
            self.setCategoryList(jsonResturant['category_list'])
        if 'hours' in jsonResturant:
            self.hours=jsonResturant['hours']
        if 'link' in jsonResturant:
            self.fb_site=jsonResturant['link']
        if 'website' in jsonResturant:
            self.site = jsonResturant['website']
            self.site=self.site.split(" ")[0]
        if 'location' in jsonResturant:
            self.location =jsonResturant['location']
        if 'overall_star_rating' in jsonResturant:
            self.rating = jsonResturant['overall_star_rating']
        if 'phone' in jsonResturant:
            self.phone = jsonResturant['phone']
        if 'price_range' in jsonResturant:
            self.price = jsonResturant['price_range']
        if 'distance' in jsonResturant:
            self.distance = jsonResturant['distance']

    def setCategoryList(self,categoryList):
        cl=""
        for c in categoryList:
            cat = str(c['sub_category']).replace("_"," ")
            cl=cl+cat+", "
        self.category_list=cl[:-2]

    def serialize(self):
        return {'name':self.name, 'about':self.about, 'category_list':self.category_list, 'hours':self.hours, 'fb_site':self.fb_site,
        'site':self.site, 'location':self.location, 'rating':self.rating, 'phone':self.phone,'price':self.price,'distance':self.distance}

    def __str__(self):
        s = str("*Nome*: %s\n"
                "*Tipologia di cucina*: %s\n"%(self.name,self.category_list))
        if self.phone != "":
            s=s+str("Telefono: %s\n"%(self.phone))
        if self.price!="":
            s=s+str("Prezzo: %s\n" %(self.price))
        if self.rating!="":
            s=s+str("Valutazione: %s\n" %(self.rating))
        if self.distance!="":
            s=s+str("Dista da te %s m\n" %(str(int(float(self.distance)*1000))))
        if 'latitude' in self.location:
            s=s+str("[Mostra sulla mappa](%s)\n"%("https://www.google.com/maps/?q="+str(self.location['latitude'])+","+str(self.location['longitude'])))
        if self.site != "":
            s=s+str("[Vai al sito](%s)" %(self.site))
        else:
            s=s+str("[Vai alla pagina FaceBook](%s)" %(self.fb_site))
        return s

#{'name': 'Gli artisti della pizza', 'about': "Il nostro impasto lievitato 72 ore vi permetterà di assaporare tutti i vari tipi di pizze con leggerezza. Venite a scoprire le idee dell'Artista.", 'category_list': [{'_id': ObjectId('5a4794407204ae19606a972c'), 'old_category': 'Pizza Place', 'sub_category': 'pizza', 'category': 'pizza'}], 'engagement': {'count': 137, 'social_sentence': '137 people like this.'}, 'fan_count': 137, 'hours': {'mon_1_open': '10:00', 'mon_1_close': '22:00', 'tue_1_open': '10:00', 'tue_1_close': '23:00', 'wed_1_open': '10:00', 'wed_1_close': '23:00', 'thu_1_open': '10:00', 'thu_1_close': '23:00', 'fri_1_open': '10:00', 'fri_1_close': '23:00', 'sat_1_open': '10:00', 'sat_1_close': '23:30', 'sun_1_open': '16:00', 'sun_1_close': '23:00'}, 'is_always_open': False, 'is_permanently_closed': False, 'is_verified': False, 'link': 'https://www.facebook.com/gliartistidellapizza/', 'location': {'city': 'Rome', 'country': 'Italy', 'latitude': 41.8173056, 'longitude': 12.4453663, 'street': 'Via del Pianeta Terra 89/91', 'zip': '00144'}, 'phone': '3468479285', 'photos': {'data': [{'created_time': '2017-02-18T15:44:38+0000', 'id': '1648017205504019'}], 'paging': {'cursors': {'before': 'MTY0ODAxNzIwNTUwNDAxOQZDZD', 'after': 'MTY0ODAxNzIwNTUwNDAxOQZDZD'}}}, 'picture': {'data': {'height': 50, 'is_silhouette': False, 'url': 'https://scontent.xx.fbcdn.net/v/t1.0-1/p50x50/16730678_1648017205504019_254208720981062711_n.jpg?oh=fea727431efaad00f988f9a7bf03fbc3&oe=5AE73868', 'width': 50}}, 'rating_count': 0, 'id': '1647988218840251'}
#TEST
if __name__ == "__main__":
    a = {'name': 'Gli artisti della pizza', 'about': "Il nostro impasto lievitato 72 ore vi permetterà di assaporare tutti i vari tipi di pizze con leggerezza. Venite a scoprire le idee dell'Artista.", 'category_list': [{'_id': ObjectId('5a4794407204ae19606a972c'), 'old_category': 'Pizza Place', 'sub_category': 'pizza', 'category': 'pizza'}], 'engagement': {'count': 137, 'social_sentence': '137 people like this.'}, 'fan_count': 137, 'hours': {'mon_1_open': '10:00', 'mon_1_close': '22:00', 'tue_1_open': '10:00', 'tue_1_close': '23:00', 'wed_1_open': '10:00', 'wed_1_close': '23:00', 'thu_1_open': '10:00', 'thu_1_close': '23:00', 'fri_1_open': '10:00', 'fri_1_close': '23:00', 'sat_1_open': '10:00', 'sat_1_close': '23:30', 'sun_1_open': '16:00', 'sun_1_close': '23:00'}, 'is_always_open': False, 'is_permanently_closed': False, 'is_verified': False, 'link': 'https://www.facebook.com/gliartistidellapizza/', 'location': {'city': 'Rome', 'country': 'Italy', 'latitude': 41.8173056, 'longitude': 12.4453663, 'street': 'Via del Pianeta Terra 89/91', 'zip': '00144'}, 'phone': '3468479285', 'photos': {'data': [{'created_time': '2017-02-18T15:44:38+0000', 'id': '1648017205504019'}], 'paging': {'cursors': {'before': 'MTY0ODAxNzIwNTUwNDAxOQZDZD', 'after': 'MTY0ODAxNzIwNTUwNDAxOQZDZD'}}}, 'picture': {'data': {'height': 50, 'is_silhouette': False, 'url': 'https://scontent.xx.fbcdn.net/v/t1.0-1/p50x50/16730678_1648017205504019_254208720981062711_n.jpg?oh=fea727431efaad00f988f9a7bf03fbc3&oe=5AE73868', 'width': 50}}, 'rating_count': 0, 'id': '1647988218840251'}
    b=dumps(a,indent=4)
    r=Restaurant(json.loads(b))
    print(r)