from pyquery import PyQuery as pq
from settings import CREDENTIALS
from utils import downloadImage, evalRegex
import requests
import random

selectors = [
    'div._XWk',  # Fecha nacimiento, lugar de nacimiento
    '#cwos',  # Calculos
    'div.kpd-ans',  # tasas de desempleo
    '#wob_ttm',  # temperatura
    'div.vk_bk.vk_ans',  # conversion de monedas por ejemplo, hora tambien
    'span._Tgc',
    'div.zloOqf.kno-fb-ctx',
    'div.HwtpBd.kno-fb-ctx',
    'ol.lr_dct_wd_ol',  # que es
    '#knowledge-currency__tgt-amount',
    'div.vk_sh.vk_gy',  # ubicacion, donde estoy
    # Span wikipedia julian assange testing, hernan botbol, barra a la derecha
    'div.kno-rdesc span',
    '#tw-target-text',  # traducciones
    'div._mr.kno-fb-ctx'
]


def findResponse(body):
    response = ""
    d = pq(body)
    for selector in selectors:
        response = d(selector).eq(0).text()
        if response != "":
            if selector == '#wob_ttm':
                temp = "Temperatura: " + response + " °C"
                city = d("#wob_loc").eq(0).text()
                humidity = "Humedad: " + d("#wob_hm").eq(0).text()
                wind = "Viento: " + d("#wob_tws").eq(0).text()
                response = "▪️ " + city + " ▫️\n" + temp + "\n" + humidity + "\n" + wind
            break
    return response


def googleQuestion(message):
    url = "https://overpp.herokuapp.com/www.google.{tld}/search?hl={lang}&q={query}&start={start}&sa=N&num={num}&ie=UTF-8&oe=UTF-8&nfpr=1&gws_rd=ssl".format(
        tld="com.co",
        lang='es',
        query=message,
        start="0",
        num="25"
    )

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-419,es;q=0.8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
        'Connection': 'keep-alive',
        'DNT': '1'
    }

    r = requests.get(url, headers=headers)
    return findResponse(r.text)


def googleImage(text):
    params = {
        "key": CREDENTIALS["google"],
        "q": text,
        "searchType": 'image',
        "cx": "13192483152618313298:4ggaqm_1t0k",
        "alt": "json",
        "num": 10,
        "start": 1
    }
    try:
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1", params=params)
        data = r.json()
        if data["searchInformation"]["totalResults"] == str(0):
            return {
                "type": "text",
                "message": "No hay resultados para '{text}'".format(text=text)
            }
        img = random.choice(data["items"])
        return {
            "type": "image",
            "image": img
        }
    except Exception as err:
        print("[GoogleImage]", err)
        return {
            "type": "text",
            "message": "Error al contactar el servidor. Por favor, intenta mas tarde."
        }


def process_message(message, msg_sender, msg_to, msg_type, connector, bot):
    #if not msg_sender.get("is_admin"):
    #    return
    regex = "{bot_name},? (.*?)\?$".format(bot_name=bot.name)
    found = evalRegex(regex, message)
    if found:
        response = googleQuestion(found)
        if response:
            connector.send_message(msg_to, response, is_reply=True)
        else:
            connector.send_message(msg_to, "Ni puta idea", is_reply=True)
    else:
        regex = "(?:^{bot_name} |^\.)img (.*)$".format(bot_name=bot.name.lower())
        found = evalRegex(regex, message)
        if found:
            response = googleImage(found)
            if response:
                if response["type"] == "image":
                    img_path = downloadImage(response["image"]["link"])
                    connector.send_image(
                        msg_to, img_path, is_reply=True)
                else:
                    connector.send_message(
                        msg_to, response["message"], is_reply=True)
