from openpyxl import load_workbook
from model.user import User
class tagExtractor():

    excellFile = load_workbook(filename='restaurantTag.xlsx', read_only=True)


    def getRestaurantTag(self,restaurant):
        description=""
        if 'about' in restaurant:
            description = restaurant['about'].lower()
        wb = self.excellFile
        ws = wb['Foglio1']
        tags=[]
        for row in ws.rows:
            if row[0].value.lower() in description:
                if row[1].value.lower() not in tags:
                    tags.append(row[1].value.lower())

        return tags

    def updateUserTags(self,chatid, restaurant):
        chatid=str(chatid)
        tags = self.getRestaurantTag(restaurant)
        u = User(chatid)
        tagsUser =u.getRestaurantTags()
        print(tags,tagsUser)
        for i,tag in enumerate(tagsUser):
            if tag[0] in tags:
                tagsUser[i]=[tag[0],tag[1]+1]
                tags.remove(tag[0])
        for t in tags:
            tagsUser.append([t,1])

        u.setRestaurantTags(tagsUser)

#TEST
if __name__ == "__main__":

    updateUserTags(48779981,{'about':'molto bello e accogliente, ottima pasta fatta in casa'})


