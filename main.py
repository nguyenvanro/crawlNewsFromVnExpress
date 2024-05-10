import os
import json
import time
import requests

# import unidecode
# from datetime import datetime

from PIL import Image, ImageDraw, ImageFont


def api_home_express():
    i = 0
    while i < 5:
        i+=1
        try:
            url = "https://vnexpress.net/microservice/home"
            payload = {}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload)
            return json.loads(response.text)
        except Exception as e:
            print(str(e))
        time.sleep(2)
        return None
        
def save_image_from_url(url_img, save_path):
    try:
        response = requests.get(url_img)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print("Image saved successfully at:", save_path)
        else:
            print("Failed to download image. Status code:", response.status_code)
    except Exception as e:
        print("Error:", str(e))
    
def writeTo_image(image, text, position, font, color, maxLine):
    charPerLine = 650 // font.getsize('x')[0]
    pen = ImageDraw.Draw(image)
    yStart = position[1]
    xStart = position[0]
    point = 0
    prePoint = 0
    while point < len(text):
        prePoint = point
        point += charPerLine
        while point < len(text) and text[point] != " ":
            point -= 1
        pen.text((xStart, yStart), text[prePoint:point], font=font, fill=color)
        yStart += font.getsize('hg')[1]
        maxLine -= 1
        if (maxLine == 0):
            if (point < len(text)):
                pen.text((xStart, yStart), "...", font=font, fill="black")
            break
        
def make_news(data):
    if not os.path.exists("news"):
        os.makedirs("news")
                
    for index, item in enumerate(data):
        # make new image and tool to draw
        image = Image.new('RGB', (650, 750), color="white")
        pen = ImageDraw.Draw(image)
        # load image from internet => resize => paste to main image
        pen.rectangle(((0, 0), (650, 300)), fill="grey")
        # newsImage = Image.open(item["image"])
        newsImage = Image.open(requests.get(item["image"], stream=True).raw)
    
        newsImage.thumbnail((650, 300), Image.ANTIALIAS)
        image.paste(newsImage, (650 // 2 - newsImage.width // 2, 300 // 2 - newsImage.height//2))
        ## write title
        titleFont = ImageFont.truetype("font/arial.ttf", 22)
        writeTo_image(image, item["title"], (10, 310), titleFont, "black", 3)
        abstractFont = ImageFont.truetype("font/arial.ttf", 15)
        writeTo_image(image, item["abstract"], (10, 390), abstractFont, "gray", 4)
        contentFont = ImageFont.truetype("font/arial.ttf", 20)
        writeTo_image(image, item["content"], (10, 460), contentFont, "black", 11)
        name = "news-" + str(index) + ".png"
        image.save("news/" + name)
        print("saved to " + "news/" + name)
    
def crawl_data():
    json_data = api_home_express()
    if not json_data:
        return
    datas =  json_data["data"]
    data = []
    for key, value in datas.items():
        print('------------------------------')
        print('key: ', key)
        # print(value["data"])
        values = value["data"]
        for i_article in values:
            # article_category = unidecode.unidecode(i_article["article_category"]["cate_name"])
            title = i_article["title"]
            lead = i_article["lead"]
            # share_url = i_article["share_url"]
            thumbnail_url = i_article["thumbnail_url"]
            if not thumbnail_url:
                continue
            # newpath = f"{'img'}\\{article_category}"
            # if not os.path.exists(newpath):
            #     os.makedirs(newpath)
            # date_current = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
            # save_path = f"{newpath}\\{date_current}{'.jpeg'}"
            # save_image_from_url(thumbnail_url, save_path)
            data.append({
                "title": title,
                "abstract": lead,
                "content": lead,
                "image": thumbnail_url,
            })         
    
    return data

if __name__ == "__main__":
    data = crawl_data()
    if data:
        make_news(data)